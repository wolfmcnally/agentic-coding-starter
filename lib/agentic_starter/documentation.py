"""Build a curated mdBook and publish only a validated release candidate."""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
import webbrowser
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[2]
ASSET_SUFFIXES = {
    ".css",
    ".js",
    ".json",
    ".svg",
    ".png",
    ".ico",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
    ".otf",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
}
FORBIDDEN = re.compile(
    r"/Users/|/home/|"
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----|AKIA[0-9A-Z]{16}|"
    r"gh[pousr]_[A-Za-z0-9]{30,}|sk-[A-Za-z0-9]{32,}"
)


def run(args: list[str], **kwargs: object) -> str:
    """Run one bounded command, retaining its complete diagnostics."""
    result = subprocess.run(
        args, check=False, text=True, capture_output=True, timeout=900, **kwargs
    )
    if result.stderr:
        print(result.stderr, file=sys.stderr, end="")
    if result.returncode:
        if result.stdout:
            print(result.stdout, end="")
        raise subprocess.CalledProcessError(result.returncode, args)
    return result.stdout.strip()


def config(root: Path) -> dict:
    """Read the recipient's committed documentation configuration."""
    return tomllib.loads((root / "documentation.toml").read_text())


def inside(base: Path, path: Path) -> Path:
    """Reject escaping paths and symlinks, including symlinked parent directories."""
    relative = path.absolute().relative_to(base.absolute())
    current = base
    for part in relative.parts:
        current /= part
        if current.is_symlink():
            raise ValueError(f"symlink refused: {current}")
    resolved = path.resolve()
    if not resolved.is_relative_to(base.resolve()):
        raise ValueError(f"path escapes documentation boundary: {path}")
    return resolved


def sources(root: Path, settings: dict) -> Path:
    """Validate the complete publication input before any preprocessor runs."""
    book = inside(root, root / settings["book"]["directory"])
    book_config = tomllib.loads((book / "book.toml").read_text())
    if book_config.get("build", {}).get("create-missing") is not False:
        raise ValueError("build.create-missing must be false")
    if (
        book_config.get("output", {}).get("html", {}).get("playground", {}).get("runnable")
        is not False
    ):
        raise ValueError("external Rust Playground must be disabled")
    source = inside(book, book / book_config["book"]["src"])
    for css in book_config.get("output", {}).get("html", {}).get("additional-css", []):
        path = inside(book, book / css)
        if not path.is_file() or FORBIDDEN.search(path.read_text()):
            raise ValueError("missing or private additional CSS")
    summary = (source / "SUMMARY.md").read_text()
    chapters = {
        inside(source, source / unquote(link.split("#")[0]))
        for link in re.findall(r"\]\(([^)]+\.md(?:#[^)]*)?)\)", summary)
    }
    if not chapters:
        raise ValueError("SUMMARY.md must name at least one chapter")
    assets = {inside(source, source / name) for name in settings["book"].get("assets", [])}
    for asset in assets:
        if not asset.is_file() or asset.suffix not in ASSET_SUFFIXES - {".js", ".json"}:
            raise ValueError(f"invalid declared asset: {asset.name}")
    allowed = chapters | assets | {source / "SUMMARY.md", source / "404.md"}
    for path in source.rglob("*"):
        inside(source, path)
        if path.is_dir():
            continue
        if path not in allowed:
            raise ValueError(f"unlisted publication input: {path.relative_to(source)}")
        if path in assets and path.suffix not in {".svg", ".css"}:
            continue
        text = path.read_text()
        if FORBIDDEN.search(text):
            raise ValueError(f"private/local material in publication input: {path.name}")
        if "{{#" in text or "file://" in text or re.search(r"<(?:script|iframe)\b", text, re.I):
            raise ValueError(f"include/embed directives refused: {path.name}")
    for path in chapters:
        if not path.is_file():
            raise ValueError(f"missing chapter: {path.name}")
    return book


def tools(root: Path, settings: dict, install: bool = False) -> dict[str, str]:
    """Use exact installed versions, or install locally without changing global tools."""
    selected = {}
    local = root / ".kickoff/docs-tools" / f"{sys.platform}-{platform.machine()}"
    for name, version in (
        ("mdbook", settings["tools"]["mdbook"]),
        ("mdbook-admonish", settings["tools"]["admonish"]),
    ):
        candidates = [local / "bin" / name]
        ambient = shutil.which(name)
        if ambient:
            candidates.append(Path(ambient))
        for candidate in candidates:
            if (
                candidate.is_file()
                and run([str(candidate), "--version"]).split()[-1].lstrip("v") == version
            ):
                selected[name] = str(candidate.resolve())
                break
        if name not in selected:
            if not install:
                raise ValueError(f"required {name} {version} missing; run ./bin/docs setup")
            cargo = shutil.which("cargo")
            if not cargo:
                raise ValueError(
                    "Rust/Cargo prerequisite missing; use the owner's normal toolchain setup"
                )
            print(
                run(
                    [
                        cargo,
                        f"+{settings['tools']['rust']}",
                        "install",
                        name,
                        "--version",
                        f"={version}",
                        "--locked",
                        "--root",
                        str(local),
                    ]
                )
            )
            candidate = local / "bin" / name
            if run([str(candidate), "--version"]).split()[-1].lstrip("v") != version:
                raise ValueError(f"installed {name} version mismatch")
            selected[name] = str(candidate.resolve())
    return selected


class Page(HTMLParser):
    """Collect browser-visible destinations and anchors from built HTML."""

    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.links: list[str] = []
        self.base: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "base" and self.base is None:
            self.base = values.get("href")
        if values.get("id"):
            self.ids.add(values["id"] or "")
        for name in ("href", "src"):
            if values.get(name):
                self.links.append(values[name] or "")
        if tag == "img" and "alt" not in values:
            raise ValueError("image lacks a text alternative")


def output_check(destination: Path, site_url: str) -> None:
    """Check every generated page, asset, link and fragment, including print/search."""
    pages = {}
    for path in destination.rglob("*"):
        inside(destination, path)
        if path.is_dir():
            continue
        if path.suffix not in ASSET_SUFFIXES | {".html"} and path.name not in {
            ".nojekyll",
            "LICENSE",
            "LICENSE.txt",
            "SOURCE-CODE-PRO-LICENSE.txt",
            "OPEN-SANS-LICENSE.txt",
            "ADMONISH-LICENSE.txt",
            "MDBOOK-LICENSE.txt",
        }:
            raise ValueError(f"unapproved output file: {path.name}")
        if path.suffix in {".html", ".json", ".js"} and FORBIDDEN.search(path.read_text()):
            raise ValueError(f"private/local material in generated output: {path.name}")
        if path.suffix == ".html":
            page = Page()
            page.feed(path.read_text())
            pages[path.resolve()] = page
    for path, page in pages.items():
        document_url = site_url + path.relative_to(destination).as_posix()
        base_url = urljoin(document_url, page.base or "")
        if urlsplit(base_url).scheme or not base_url.startswith(site_url):
            raise ValueError(f"base URL escapes the publication site: {path.name}")
        for link in page.links:
            parsed = urlsplit(link)
            if parsed.scheme or parsed.netloc or link.startswith("//"):
                continue
            parsed = urlsplit(urljoin(base_url, link))
            target_text = unquote(parsed.path)
            if target_text.startswith("/"):
                if not target_text.startswith(site_url):
                    raise ValueError(f"link escapes site prefix: {link}")
                target = destination / target_text[len(site_url) :]
            else:
                target = path.parent / target_text if target_text else path
            if target.is_dir():
                target /= "index.html"
            target = inside(destination, target)
            if not target.is_file():
                raise ValueError(f"broken local link in {path.name}: {link}")
            if (
                parsed.fragment
                and target in pages
                and unquote(parsed.fragment) not in pages[target].ids
            ):
                raise ValueError(f"broken anchor in {path.name}: {link}")
    for required in ("index.html", "404.html", "print.html", "searchindex.js"):
        if not (destination / required).is_file():
            raise ValueError(f"missing generated affordance: {required}")


def build(root: Path, settings: dict) -> Path:
    """Build into a fresh isolated directory and publish only the checked output."""
    book = sources(root, settings)
    selected = tools(root, settings)
    env = dict(os.environ)
    env["PATH"] = str(Path(selected["mdbook-admonish"]).parent) + os.pathsep + env["PATH"]
    runtime = root / ".kickoff"
    runtime.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="docs-build-", dir=runtime) as temporary:
        destination = Path(temporary) / "html"
        print(
            run(
                [
                    selected["mdbook"],
                    "build",
                    str(book),
                    "--dest-dir",
                    str(destination),
                ],
                env=env,
            )
        )
        for notice in ("ADMONISH-LICENSE", "MDBOOK-LICENSE"):
            license_file = inside(book, book / notice)
            if license_file.is_file():
                shutil.copyfile(license_file, destination / f"{notice}.txt")
        # mdBook's 404 <base> changes fragment-only URLs to the site root.
        # Bind heading links to the actual 404 document before link validation.
        not_found = destination / "404.html"
        if not_found.is_file():
            not_found.write_text(not_found.read_text().replace('href="#', 'href="404.html#'))
        site_url = tomllib.loads((book / "book.toml").read_text())["output"]["html"]["site-url"]
        output_check(destination, site_url)
        # Replace only this command's ignored, conventional output directory.
        final = runtime / "manual"
        if final.is_symlink():
            raise ValueError("documentation output must not be a symlink")
        if final.exists():
            shutil.rmtree(final)
        shutil.copytree(destination, final)
    print("DOCS BUILD PASS (curated source, generated links/assets/anchors, search and print)")
    return final


def release(root: Path, settings: dict) -> tuple[str, str, str]:
    """Bind a remote operation to this clean, pushed release branch."""
    deploy = settings["deploy"]
    repository, branch = deploy["repository"], deploy["release_branch"]
    if not re.fullmatch(r"[\w.-]+/[\w.-]+", repository) or not branch or branch.startswith("-"):
        raise ValueError("configure a valid deployment repository and release branch first")
    if run(["git", "status", "--porcelain"], cwd=root):
        raise ValueError("deployment requires a clean committed candidate")
    if run(["git", "branch", "--show-current"], cwd=root) != branch:
        raise ValueError("checkout is not the configured release branch")
    remote = run(["git", "remote", "get-url", "origin"], cwd=root)
    if remote not in {
        f"https://github.com/{repository}.git",
        f"https://github.com/{repository}",
        f"git@github.com:{repository}.git",
    }:
        raise ValueError("origin does not match the configured publication repository")
    head = run(["git", "rev-parse", "HEAD"], cwd=root)
    remote_head = run(
        ["git", "ls-remote", "--exit-code", "origin", f"refs/heads/{branch}"], cwd=root
    ).split()[0]
    if head != remote_head:
        raise ValueError("release candidate is not the latest pushed release branch")
    return repository, branch, head


def deploy(root: Path, settings: dict, continuous: str | None) -> None:
    """Use an already approved workflow; never create permissions or enable Pages."""
    repository, branch, head = release(root, settings)
    workflow = root / ".github/workflows" / settings["deploy"]["workflow"]
    if not workflow.is_file():
        raise ValueError(
            "Pages workflow missing; approve the prepared permission boundary before installing it"
        )
    if continuous:
        print(
            run(
                [
                    "gh",
                    "variable",
                    "set",
                    "DOCS_RELEASE_BRANCH",
                    "--repo",
                    repository,
                    "--body",
                    branch,
                ]
            )
        )
        print(
            run(
                [
                    "gh",
                    "variable",
                    "set",
                    "DOCS_CONTINUOUS",
                    "--repo",
                    repository,
                    "--body",
                    continuous,
                ]
            )
        )
        for name, value in (("DOCS_RELEASE_BRANCH", branch), ("DOCS_CONTINUOUS", continuous)):
            observed = json.loads(
                run(["gh", "api", f"repos/{repository}/actions/variables/{name}"])
            )
            if observed.get("value") != value:
                raise ValueError(f"repository variable verification failed: {name}")
        print(f"DOCS continuous {continuous} for {branch}; manual deployment remains available")
        return
    build(root, settings)
    print(
        run(
            [
                "gh",
                "workflow",
                "run",
                settings["deploy"]["workflow"],
                "--repo",
                repository,
                "--ref",
                branch,
                "-f",
                f"candidate={head}",
            ]
        )
    )
    print("DOCS deployment requested; completion and live-site verification remain unproved")


def verify(url: str, chapters: list[str]) -> None:
    """Probe the deployed site, its deep links, assets, search and private exclusions."""
    if not url.startswith("https://") or not url.endswith("/"):
        raise ValueError("live publication verification requires an HTTPS base URL ending in /")
    for name in (
        "",
        *chapters,
        "404.html",
        "searchindex.js",
        "css/general.css",
    ):
        with urlopen(urljoin(url, name), timeout=20) as response:
            if response.status != 200 or not response.read():
                raise ValueError(f"live resource failed: {name}")
    from urllib.error import HTTPError

    for name in (
        ".env",
        "LOG.md",
        "AGENTS.md",
        "secrets/credentials.json",
        ".codex/config.toml",
    ):
        try:
            with urlopen(urljoin(url, name), timeout=20) as response:
                raise ValueError(
                    f"private path publicly reachable: {name} (HTTP {response.status})"
                )
        except HTTPError as exc:
            if exc.code not in {403, 404}:
                raise
    print("DOCS LIVE PROBES PASS; rendered browser/search interaction remains a separate check")


def main(argv: list[str] | None = None, *, root: Path = ROOT) -> int:
    """Execute the repository documentation interface."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        nargs="?",
        default="open",
        choices=("open", "build", "check", "setup", "serve", "deploy", "verify"),
    )
    parser.add_argument("arguments", nargs="*")
    parser.add_argument("--url", help="existing approved Tailnet proxy URL for browser opening")
    parser.add_argument("--no-open", action="store_true")
    parser.add_argument(
        "--release",
        action="store_true",
        help="verify CI branch/repository against committed publication settings",
    )
    args = parser.parse_args(argv)
    try:
        settings = config(root)
        if args.release:
            if args.command not in {"build", "check"}:
                raise ValueError("--release is only valid for build/check")
            if (
                os.environ.get("GITHUB_REF_NAME") != settings["deploy"]["release_branch"]
                or os.environ.get("GITHUB_REPOSITORY") != settings["deploy"]["repository"]
            ):
                raise ValueError(
                    "CI branch/repository does not match committed publication settings"
                )
            if os.environ.get("GITHUB_EVENT_NAME") == "workflow_dispatch":
                expected = os.environ.get("DOCS_VALIDATED_COMMIT")
                if not expected or run(["git", "rev-parse", "HEAD"], cwd=root) != expected:
                    raise ValueError("CI commit differs from the locally validated manual dispatch")
        if args.command == "deploy":
            if args.arguments not in ([], ["continuous", "on"], ["continuous", "off"]):
                raise ValueError("usage: docs deploy [continuous on|off]")
            deploy(root, settings, args.arguments[-1] if args.arguments else None)
        elif args.command == "verify":
            if len(args.arguments) > 1:
                raise ValueError("usage: docs verify [https://site/prefix/]")
            book = sources(root, settings)
            book_config = tomllib.loads((book / "book.toml").read_text())
            summary = (book / book_config["book"]["src"] / "SUMMARY.md").read_text()
            chapters = [
                link.split("#")[0].removesuffix(".md") + ".html"
                for link in re.findall(r"\]\(([^)]+\.md(?:#[^)]*)?)\)", summary)
            ]
            verify(args.arguments[0] if args.arguments else settings["deploy"]["url"], chapters)
        else:
            if args.arguments:
                raise ValueError("unexpected arguments")
            if args.command == "setup":
                tools(root, settings, install=True)
                print("DOCS SETUP PASS")
            else:
                destination = build(root, settings)
                if args.command == "open" and not args.no_open:
                    if not webbrowser.open((destination / "index.html").as_uri()):
                        raise ValueError("browser did not accept the open request")
                elif args.command == "serve":
                    from functools import partial
                    from http.server import (
                        SimpleHTTPRequestHandler,
                        ThreadingHTTPServer,
                    )

                    port = settings["preview"]["port"]
                    book = root / settings["book"]["directory"]
                    site_url = tomllib.loads((book / "book.toml").read_text())["output"]["html"][
                        "site-url"
                    ]

                    class PreviewHandler(SimpleHTTPRequestHandler):
                        def translate_path(self, request: str) -> str:
                            if request.startswith(site_url):
                                request = "/" + request[len(site_url) :]
                            return super().translate_path(request)

                    handler = partial(PreviewHandler, directory=str(destination))
                    with ThreadingHTTPServer(("127.0.0.1", port), handler) as server:
                        url = args.url or f"http://127.0.0.1:{port}{site_url}"
                        print(
                            f"DOCS preview: {url} (foreground; Ctrl-C stops)",
                            flush=True,
                        )
                        if not args.no_open and not webbrowser.open(url):
                            raise ValueError("browser did not accept the preview request")
                        server.serve_forever()
        return 0
    except KeyboardInterrupt:
        print("DOCS preview stopped")
        return 0
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        print(f"DOCS REFUSED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
