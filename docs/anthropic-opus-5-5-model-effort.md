If you're unsure which model to use, start with [Claude Opus 5.5](https://platform.claude.com/docs/en/models/opus-5-5/overview) for most workloads. Use [Claude Fable 5.1](https://platform.claude.com/docs/en/models/fable-5-1/overview) for demanding reasoning and long-horizon agentic work, or when your evals on Claude Opus 5.5 at higher effort still fall short.

### Recommended effort levels for Claude Opus 5.5

Claude Opus 5.5 supports all five effort levels, and `medium` is the default (Claude Opus 5 and earlier Opus models default to `high`, so a request that omits `effort` runs one level lower than it did on Claude Opus 5). Adaptive thinking is always on and can't be turned off, so effort is the primary control for how much the model reasons and what a request costs. Run an effort sweep on your own evals rather than carrying settings over from an earlier model, and set a large `max_tokens` at the higher levels: it's a hard limit on total output (thinking plus response text).

### Recommended effort levels for Claude Fable 5.1

Claude Fable 5.1 supports all five effort levels. **Start with `high`, the default.** Step up to `xhigh` or `max` for the most capability-sensitive agentic and coding work, and step down to `medium` or `low` for routine or latency-sensitive work once your evals show quality holds.

## Calibrate effort

Start at `medium`, the default on Claude Opus 5.5 (Claude Opus 5 defaults to `high`), set it explicitly, and test several levels against your own evals rather than carrying over the setting you used on Claude Opus 5.

Reserve `xhigh` and `max` for work where you've measured a quality gain.

| Level | When to use it |
| :- | :- |
| `low` | Quick exchanges where you review each result, such as brainstorming, a first sketch, or a small change like a rename |
| `medium` | The default on Opus 5.5 and Sonnet 5.5, where it fits day-to-day engineering work with a clear scope, such as implementing a new feature. On other models, reduces token usage for cost-sensitive work that can trade off some intelligence |
| `high` | Work where verification matters or edge cases are likely, such as fixing a bug in an existing codebase. The default on every model except Opus 5.5, Sonnet 5.5, and Opus 4.7 |
| `xhigh` | Deeper reasoning at higher token spend. The default on Opus 4.7 |
| `max` | Hard problems you want Claude to work through without you, such as finding security vulnerabilities. `max` may show diminishing returns and is prone to overthinking, so test before adopting it broadly |

In tests on Opus 5.5 and Fable 5.1, Claude at a higher level tested more edge cases and verified more of its work before answering. It also made more choices on its own. At a lower level, Claude returned a starting point sooner, which fits work where you review each result and steer the next step.
