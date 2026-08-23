(() => {
  "use strict";

  const phaseData = window.AGENTIC_STARTER_EXECUTION_DASHBOARD_DATA;
  const indexData = window.AGENTIC_STARTER_EXECUTION_DASHBOARD_INDEX;
  const app = document.getElementById("app");
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const animationDuration = reduceMotion ? 0 : 225;
  const palette = {
    planning: "#5b3f9b",
    plan_review: "#007c91",
    implementation: "#2456a6",
    code_review: "#9b4a13",
    automated_checks: "#087f8c",
    integration: "#087a55",
    agent_work: "#8b4b9e",
    parallel_work: "#525f7a",
    orchestration_setup: "#667085",
    orchestration_planning: "#596780",
    orchestration_implementation: "#4f6175",
    orchestration_acceptance: "#435a70",
    orchestration_close: "#384f63",
    orchestration_unmeasured: "#7c8596",
    success: "#087a55",
    failure: "#a63d40"
  };
  let exact = false;
  const charts = [];

  const el = (tag, attrs = {}, children = []) => {
    const node = document.createElement(tag);
    Object.entries(attrs).forEach(([key, value]) => {
      if (key === "class") node.className = value;
      else if (key === "text") node.textContent = value;
      else if (key === "hidden") node.hidden = Boolean(value);
      else node.setAttribute(key, String(value));
    });
    const items = Array.isArray(children) ? children : [children];
    items.filter(Boolean).forEach((child) => node.append(child));
    return node;
  };
  const ns = (value) => {
    if (value === null || value === undefined) return "Unknown";
    if (exact) return `${Number(value).toLocaleString("en-US")} ns`;
    const seconds = Number(value) / 1e9;
    if (seconds < 1) return `${(seconds * 1000).toFixed(1)} ms`;
    if (seconds < 120) return `${seconds.toFixed(seconds < 10 ? 2 : 1)} s`;
    const minutes = Math.floor(seconds / 60);
    const remainder = seconds - minutes * 60;
    if (minutes < 120) return `${minutes}m ${remainder.toFixed(1)}s`;
    const hours = Math.floor(minutes / 60);
    return `${hours}h ${minutes % 60}m`;
  };
  const pct = (value) => `${(Number(value) * 100).toFixed(1)}%`;
  const nsToMinutes = (value) => Number(value) / 60e9;
  const axisMinutes = (value) => {
    const minutes = Number(value);
    const precision = Math.abs(minutes) >= 10 || Number.isInteger(minutes) ? 0 : 1;
    return `${minutes.toFixed(precision)}m`;
  };
  const titleBlock = (title, subtitle) => el("div", {}, [
    el("h2", {text: title}),
    el("p", {class: "subtitle", text: subtitle})
  ]);
  const panel = (title, subtitle, wide = false) => {
    const body = el("section", {class: `panel${wide ? " wide" : ""}`});
    body.append(el("div", {class: "panel-head"}, titleBlock(title, subtitle)));
    return body;
  };
  const table = (headers, rows) => {
    const node = el("table", {class: "semantic-table"});
    const head = el("thead");
    head.append(el("tr", {}, headers.map((header, index) =>
      el("th", {scope: "col", class: index ? "number" : "", text: header})
    )));
    const body = el("tbody");
    rows.forEach((row) => body.append(el("tr", {}, row.map((value, index) =>
      el("td", {class: index ? "number" : "", "data-label": headers[index], text: String(value)})
    ))));
    node.append(head, body);
    return node;
  };
  const chartNode = (label, size = "standard") =>
    el("div", {class: `chart${size === "tall" ? " tall" : size === "compact" ? " compact" : ""}`, role: "img", tabindex: "0", "aria-label": label});
  const initChart = (node, option) => {
    const chart = echarts.init(node, null, {renderer: "svg"});
    const accessibleDescription = node.getAttribute("aria-label");
    chart.setOption({
      animation: !reduceMotion,
      animationDuration,
      animationDurationUpdate: animationDuration,
      animationEasing: "cubicOut",
      animationEasingUpdate: "cubicOut",
      aria: {enabled: true, description: accessibleDescription, decal: {show: false}},
      textStyle: {fontFamily: "system-ui, sans-serif", color: "#172033"},
      ...option
    });
    charts.push(chart);
    return chart;
  };
  const detailsTable = (label, headers, rows) => {
    const details = el("details");
    details.append(el("summary", {text: label}), table(headers, rows));
    return details;
  };
  const outcomeMark = (outcome) => {
    const failed = outcome !== "success";
    return el("span", {class: `status-mark ${failed ? "failure" : "success"}`, "aria-hidden": "true"}, [
      el("span", {text: failed ? "!" : "✓"})
    ]);
  };

  const roleLabels = {
    planner: "Planning",
    reviewer: "Plan Review",
    coder: "Implementation",
    critic: "Code Review"
  };
  const roleActivityKeys = {
    planner: "planning",
    reviewer: "plan_review",
    coder: "implementation",
    critic: "code_review"
  };
  const activityLabels = {
    planning: "Planning",
    plan_review: "Plan Review",
    implementation: "Implementation",
    code_review: "Code Review",
    automated_checks: "Automated Checks",
    integration: "Integration",
    agent_work: "Other Agent Work",
    parallel_work: "Parallel Work",
    orchestration_setup: "Setup & Coordination",
    orchestration_planning: "Plan Coordination",
    orchestration_implementation: "Implementation Coordination",
    orchestration_acceptance: "Acceptance Coordination",
    orchestration_close: "Close Preparation",
    orchestration_unmeasured: "Orchestration / Unmeasured"
  };

  function titleCase(value) {
    return value
      .replace(/[_-]+/g, " ")
      .replace(/\b\w/g, (letter) => letter.toUpperCase());
  }

  function gateLabel(operation) {
    const name = operation
      .replace(/^gate\.acceptance\./, "")
      .replace(/^gate\.check\./, "")
      .replace(/^gate\./, "");
    const known = {
      full: "Full Build Gate",
      focused: "Focused Tests",
      broad: "Broad Test Suite",
      final: "Final Acceptance",
      "status-smoke": "Status Smoke Tests",
      "selection-smoke": "Selection Smoke Tests",
      "check-graph-smoke": "Graph Smoke Tests",
      "null-honesty-smoke": "Null-Honesty Smoke Tests",
      "window-smoke": "Window Smoke Tests",
      "fixture-status": "Fixture Status Check",
      gate9: "Acceptance Gate 9",
      gate10: "Acceptance Gate 10"
    };
    return known[name] || titleCase(name.replace(/\./g, " "));
  }

  function activityKey(span) {
    if (span.category === "intelligence") return roleActivityKeys[span.role] || "agent_work";
    if (span.category === "gate") return "automated_checks";
    if (span.category === "reconciliation") {
      const stage = {
        "orchestration.setup": "orchestration_setup",
        "orchestration.planning": "orchestration_planning",
        "orchestration.implementation": "orchestration_implementation",
        "orchestration.acceptance": "orchestration_acceptance",
        "orchestration.close": "orchestration_close"
      };
      return stage[span.operation] || "integration";
    }
    return null;
  }

  function activityLabel(span) {
    if (span.category === "intelligence") return roleLabels[span.role] || "Other Agent Work";
    if (span.category === "gate") return gateLabel(span.operation);
    if (span.category === "reconciliation") {
      return activityLabels[activityKey(span)] || "Integration";
    }
    return titleCase(span.operation);
  }

  function isOrchestrationStage(span) {
    return span.category === "reconciliation" && span.operation.startsWith("orchestration.");
  }

  function attributionSpans(view) {
    const parentIds = new Set(
      view.spans
        .filter((span) => span.category === "gate" && span.parent_span_id)
        .map((span) => span.parent_span_id)
    );
    return view.spans.filter((span) => {
      if (!activityKey(span)) return false;
      if (span.category === "gate" && parentIds.has(span.span_id)) return false;
      return true;
    });
  }

  function meaningfulSpans(view) {
    return attributionSpans(view).filter((span) => !isOrchestrationStage(span));
  }

  function labeledActivities(view) {
    const spans = meaningfulSpans(view)
      .sort((a, b) => a.start_offset_ns - b.start_offset_ns || b.duration_ns - a.duration_ns);
    const totals = {};
    spans.forEach((span) => {
      const base = activityLabel(span);
      totals[base] = (totals[base] || 0) + 1;
    });
    const seen = {};
    return spans.map((span) => {
      const base = activityLabel(span);
      seen[base] = (seen[base] || 0) + 1;
      const sequence = totals[base] > 1
        ? ` · ${span.category === "gate" ? "run" : "pass"} ${seen[base]}`
        : "";
      const outcome = span.outcome === "success" ? "" : " · failed";
      return {span, label: `${base}${sequence}${outcome}`};
    });
  }

  function activityRows(view) {
    const roots = view.spans.filter((span) => span.category === "run");
    const labeled = labeledActivities(view);
    const meaningful = attributionSpans(view);
    const boundaries = [...new Set([
      ...roots.flatMap((span) => [span.start_offset_ns, span.end_offset_ns]),
      ...meaningful.flatMap((span) => [span.start_offset_ns, span.end_offset_ns])
    ])].sort((a, b) => a - b);
    const totals = {};
    for (let index = 0; index < boundaries.length - 1; index += 1) {
      const start = boundaries[index];
      const end = boundaries[index + 1];
      if (end <= start || !roots.some((root) => root.start_offset_ns <= start && root.end_offset_ns >= end)) continue;
      const active = meaningful
        .filter((span) => span.start_offset_ns <= start && span.end_offset_ns >= end);
      const specificKeys = new Set(
        active
          .filter((span) => !isOrchestrationStage(span))
          .map(activityKey)
      );
      const stageKeys = new Set(
        active
          .filter(isOrchestrationStage)
          .map(activityKey)
      );
      const keys = specificKeys.size ? specificKeys : stageKeys;
      const key = keys.size === 0
        ? "orchestration_unmeasured"
        : keys.size === 1
          ? [...keys][0]
          : "parallel_work";
      totals[key] = (totals[key] || 0) + end - start;
    }
    const order = [
      "planning", "plan_review", "implementation", "code_review",
      "automated_checks", "integration", "parallel_work", "agent_work",
      "orchestration_unmeasured"
    ];
    return order
      .filter((key) => totals[key])
      .map((key) => ({key, label: activityLabels[key], value: totals[key]}));
  }

  function unmeasuredGaps(view) {
    const roots = view.spans.filter((span) => span.category === "run");
    const meaningful = attributionSpans(view);
    const labelById = new Map(
      meaningful.map((span) => [span.span_id, activityLabel(span)])
    );
    const boundaries = [...new Set([
      ...roots.flatMap((span) => [span.start_offset_ns, span.end_offset_ns]),
      ...meaningful.flatMap((span) => [span.start_offset_ns, span.end_offset_ns])
    ])].sort((a, b) => a - b);
    const gaps = [];
    for (let index = 0; index < boundaries.length - 1; index += 1) {
      const start = boundaries[index];
      const end = boundaries[index + 1];
      if (end <= start || !roots.some((root) => root.start_offset_ns <= start && root.end_offset_ns >= end)) continue;
      if (meaningful.some((span) => span.start_offset_ns <= start && span.end_offset_ns >= end)) continue;
      const previous = gaps[gaps.length - 1];
      if (previous && previous.end === start) previous.end = end;
      else gaps.push({start, end});
    }
    return gaps
      .map((gap) => {
        const before = [...meaningful]
          .filter((span) => span.end_offset_ns <= gap.start)
          .sort((a, b) => b.end_offset_ns - a.end_offset_ns)[0];
        const after = [...meaningful]
          .filter((span) => span.start_offset_ns >= gap.end)
          .sort((a, b) => a.start_offset_ns - b.start_offset_ns)[0];
        return {
          duration: gap.end - gap.start,
          between: `${before ? labelById.get(before.span_id) : "Run Start"} → ${after ? labelById.get(after.span_id) : "Run End"}`
        };
      })
      .sort((a, b) => b.duration - a.duration)
      .slice(0, 5);
  }

  function renderActivityBreakdown(view, target) {
    const rows = activityRows(view);
    const chart = chartNode("Elapsed build time by user-facing activity. A table follows.");
    const narrow = window.innerWidth <= 620;
    target.append(chart);
    initChart(chart, {
      grid: {left: narrow ? 132 : 180, right: narrow ? 55 : 85, top: 10, bottom: 45},
      tooltip: {trigger: "item", renderMode: "richText", formatter: (item) => {
        const row = rows[item.dataIndex];
        return `${row.label}\n${ns(row.value)} · ${pct(row.value / (view.makespan_ns || 1))}`;
      }},
      xAxis: {type: "value", name: "Minutes", splitNumber: narrow ? 3 : 5, axisLabel: {formatter: axisMinutes}},
      yAxis: {type: "category", inverse: true, data: rows.map((row) => row.label), axisLabel: {width: narrow ? 120 : 165, overflow: "truncate"}},
      series: [{
        type: "bar",
        data: rows.map((row) => ({
          value: nsToMinutes(row.value),
          itemStyle: {color: palette[row.key], borderRadius: [0, 5, 5, 0]}
        })),
        label: {show: true, position: "right", formatter: (item) => ns(rows[item.dataIndex].value)}
      }]
    });
    target.append(detailsTable(
      "Exact activity values",
      ["Activity", "Elapsed Time", "Share"],
      rows.map((row) => [row.label, ns(row.value), pct(row.value / (view.makespan_ns || 1))])
    ));
    const gaps = unmeasuredGaps(view);
    if (gaps.length) {
      target.append(
        el("h3", {class: "table-title", text: "Largest Unmeasured Gaps"}),
        el("p", {class: "subtitle", text: "These intervals are real elapsed time between measured activities. They identify missing instrumentation or orchestration delay; the telemetry cannot safely claim which."}),
        table(["Between", "Elapsed Time"], gaps.map((gap) => [gap.between, ns(gap.duration)]))
      );
    }
  }

  function renderGateBreakdown(view, target) {
    const rows = view.gate_breakdown;
    if (!rows.length) {
      target.append(el("p", {class: "empty", text: "No automated checks were recorded in this view."}));
      return;
    }
    const chartRows = rows.slice(0, 12);
    if (chartRows.length === 1) {
      target.append(el("p", {class: "callout", text: `${gateLabel(chartRows[0].operation)} took ${ns(chartRows[0].exclusive_duration_ns)}. Older telemetry recorded this as one aggregate check, so no finer breakdown is available.`}));
    } else {
      const chart = chartNode("Automated checks ranked by exclusive elapsed time. A table follows.");
      const narrow = window.innerWidth <= 620;
      target.append(chart);
      initChart(chart, {
        grid: {left: narrow ? 105 : 185, right: narrow ? 55 : 75, top: 15, bottom: 45},
        tooltip: {trigger: "item", renderMode: "richText", formatter: (item) => {
          const row = chartRows[item.dataIndex];
          return `${gateLabel(row.operation)}\n${row.attempt_count} run${row.attempt_count === 1 ? "" : "s"} · ${row.failed_attempts} unsuccessful\n${ns(row.exclusive_duration_ns)}`;
        }},
        xAxis: {type: "value", name: "Minutes", splitNumber: narrow ? 3 : 5, axisLabel: {formatter: axisMinutes}},
        yAxis: {type: "category", inverse: true, data: chartRows.map((row) => gateLabel(row.operation)), axisLabel: {width: 170, overflow: "truncate"}},
        series: [{
          type: "bar",
          data: chartRows.map((row) => ({
            value: nsToMinutes(row.exclusive_duration_ns),
            itemStyle: {color: palette.automated_checks, borderRadius: [0, 5, 5, 0]}
          })),
          label: {show: true, position: "right", formatter: (item) => ns(chartRows[item.dataIndex].exclusive_duration_ns)}
        }]
      });
    }
    target.append(detailsTable(
      "Exact check values",
      ["Automated Check", "Runs", "Unsuccessful", "Elapsed Time"],
      rows.map((row) => [gateLabel(row.operation), row.attempt_count, row.failed_attempts, ns(row.exclusive_duration_ns)])
    ));
  }

  function renderWaterfall(trace, target) {
    const candidates = labeledActivities(trace).filter(
      (item) => item.span.duration_ns >= 5e9 || item.span.outcome !== "success"
    );
    const selectedIds = new Set(
      [...candidates]
        .sort((a, b) => b.span.duration_ns - a.span.duration_ns)
        .slice(0, 40)
        .map((item) => item.span.span_id)
    );
    const selected = candidates
      .filter((item) => selectedIds.has(item.span.span_id))
      .sort((a, b) => a.span.start_offset_ns - b.span.start_offset_ns || b.span.duration_ns - a.span.duration_ns);
    const spans = selected.map((item) => item.span);
    const labels = selected.map((item) => item.label);
    const chart = chartNode(
      "Chronological build timeline. Horizontal position is elapsed time; rows show material agent work and automated checks.",
      spans.length <= 4 ? "compact" : "tall"
    );
    target.append(chart);
    const values = spans.map((span, lane) => [
      lane,
      nsToMinutes(span.start_offset_ns),
      nsToMinutes(span.end_offset_ns),
      activityKey(span)
    ]);
    initChart(chart, {
      grid: {left: 225, right: 35, top: 20, bottom: 75},
      tooltip: {
        trigger: "item",
        renderMode: "richText",
        formatter: (item) => {
          const span = spans[item.dataIndex];
          return `${labels[item.dataIndex]}\n${span.outcome === "success" ? "Completed" : titleCase(span.outcome)}\n${ns(span.duration_ns)}`;
        }
      },
      xAxis: {type: "value", name: "Elapsed Minutes", nameLocation: "middle", nameGap: 30, axisLabel: {formatter: axisMinutes}},
      yAxis: {type: "category", inverse: true, data: labels, axisLabel: {width: 205, overflow: "truncate"}},
      dataZoom: [{type: "slider", xAxisIndex: 0, bottom: 15, height: 22}, {type: "inside", xAxisIndex: 0}],
      series: [{
        type: "custom",
        encode: {x: [1, 2], y: 0},
        data: values,
        renderItem: (params, api) => {
          const start = api.coord([api.value(1), api.value(0)]);
          const end = api.coord([api.value(2), api.value(0)]);
          const height = Math.max(5, api.size([0, 1])[1] * .58);
          const key = api.value(3);
          return {
            type: "rect",
            shape: {x: start[0], y: start[1] - height / 2, width: Math.max(2, end[0] - start[0]), height, r: 3},
            style: {fill: palette[key] || palette.agent_work, opacity: .9}
          };
        }
      }]
    });
    target.append(detailsTable("Timeline values", ["Activity", "Outcome", "Elapsed Time"], spans.map((span, index) => [
      labels[index], span.outcome === "success" ? "Completed" : titleCase(span.outcome), ns(span.duration_ns)
    ])));
  }

  function renderSlowest(trace, target) {
    const rows = labeledActivities(trace)
      .sort((a, b) => b.span.duration_ns - a.span.duration_ns || a.label.localeCompare(b.label))
      .slice(0, 8);
    if (rows.length < 2) {
      target.append(table(["Activity", "Outcome", "Elapsed Time"], rows.map((row) => [
        row.label, row.span.outcome === "success" ? "Completed" : titleCase(row.span.outcome), ns(row.span.duration_ns)
      ])));
      return;
    }
    const chart = chartNode("Longest individual agent activities and automated checks. A table follows.");
    target.append(chart);
    initChart(chart, {
      grid: {left: 175, right: 35, top: 15, bottom: 45},
      tooltip: {trigger: "item", renderMode: "richText", formatter: (item) => `${rows[item.dataIndex].label}\n${ns(rows[item.dataIndex].span.duration_ns)}`},
      xAxis: {type: "value", name: "Minutes", axisLabel: {formatter: axisMinutes}},
      yAxis: {type: "category", inverse: true, data: rows.map((row) => row.label), axisLabel: {width: 160, overflow: "truncate"}},
      series: [{type: "bar", data: rows.map((row) => ({
        value: nsToMinutes(row.span.duration_ns),
        itemStyle: {color: palette[activityKey(row.span)] || palette.agent_work, borderRadius: [0, 5, 5, 0]}
      })), label: {show: true, position: "right", formatter: (item) => ns(rows[item.dataIndex].span.duration_ns)}}]
    });
    target.append(detailsTable("Longest activity values", ["Activity", "Outcome", "Elapsed Time"], rows.map((row) => [
      row.label, row.span.outcome === "success" ? "Completed" : titleCase(row.span.outcome), ns(row.span.duration_ns)
    ])));
  }

  function renderRework(trace, target) {
    const failed = meaningfulSpans(trace).filter((span) => span.outcome !== "success");
    const roleFollowups = trace.role_breakdown.filter((row) => row.attempt_count > 1);
    if (!failed.length && !roleFollowups.length) {
      target.append(el("p", {class: "empty", text: "No unsuccessful operations or role follow-up passes were recorded in this view."}));
      return;
    }
    if (failed.length) {
      const grouped = new Map();
      failed.forEach((span) => {
        const label = activityLabel(span);
        const key = `${label}\u0000${span.outcome}`;
        const row = grouped.get(key) || {
          activity: label,
          outcome: span.outcome,
          count: 0,
          duration_ns: 0
        };
        row.count += 1;
        row.duration_ns += span.duration_ns;
        grouped.set(key, row);
      });
      const rows = [...grouped.values()].sort((a, b) => b.duration_ns - a.duration_ns || a.activity.localeCompare(b.activity));
      target.append(
        el("h3", {class: "table-title", text: "Unsuccessful operations"}),
        table(
          ["Activity", "Outcome", "Count", "Elapsed Time"],
          rows.map((row) => [row.activity, titleCase(row.outcome), row.count, ns(row.duration_ns)])
        )
      );
    }
    if (roleFollowups.length) {
      target.append(
        el("h3", {class: "table-title", text: "Agent Follow-Up Passes"}),
        table(
          ["Activity", "Total Passes", "Follow-Up Passes", "Unsuccessful", "Agent Work"],
          roleFollowups.map((row) => [
            row.label,
            row.attempt_count,
            row.attempt_count - 1,
            row.failed_attempts,
            ns(row.total_duration_ns)
          ])
        )
      );
    }
  }

  function renderConvergence(trace, target) {
    const rows = trace.review_convergence || [];
    if (!rows.length) {
      target.append(el("p", {class: "empty", text: "Review convergence was not recorded for this historical phase."}));
      return;
    }
    ["reviewer", "critic"].forEach((role) => {
      const passes = rows.filter((row) => row.role === role);
      if (!passes.length) return;
      const remaining = passes.map((row) => row.actionable_findings);
      const increasedAt = remaining.findIndex((value, index) => index && value > remaining[index - 1]);
      const stalledAt = remaining.findIndex((value, index) => index && value > 0 && value === remaining[index - 1]);
      let result = `${passes[0].label}: ${remaining.join(" → ")} actionable issues`;
      if (remaining.at(-1) === 0) result += ` · converged in ${passes.length} pass${passes.length === 1 ? "" : "es"}`;
      else if (increasedAt > 0) result += ` · increased at pass ${increasedAt + 1}`;
      else if (stalledAt > 0) result += ` · stalled at pass ${stalledAt + 1}`;
      else result += " · did not reach zero";
      target.append(el("p", {class: "callout", text: result}));
    });
    target.append(table(
      ["Review", "Pass", "Reported This Pass", "Actionable After Pass", "Review Time"],
      rows.map((row) => [
        row.label,
        row.pass,
        row.findings_reported,
        row.actionable_findings,
        ns(row.duration_ns)
      ])
    ));
  }

  function renderConcurrency(trace, target) {
    const entries = Object.entries(trace.concurrency_groups);
    if (!entries.length) {
      target.append(el("p", {class: "empty", text: "N/A — no concurrency group is recorded for this view, so overlap and speedup have no valid denominator."}));
      return;
    }
    target.append(table(["Group", "Members", "Peak", "Overlap", "Work ÷ window"], entries.map(([name, value]) => [
      name, value.member_count, value.peak_concurrency, ns(value.overlap_ns), `${value.work_to_window_ratio.toFixed(2)}×`
    ])));
    target.append(el("p", {class: "subtitle", text: "Work ÷ window is observed overlap efficiency, not an inferred causal critical-path speedup."}));
  }

  function card(label, value, note, kind) {
    return el("div", {class: `card ${kind}`}, [
      el("span", {class: "label", text: label}),
      el("strong", {class: "value", text: value}),
      el("span", {class: "note", text: note})
    ]);
  }

  function renderHandoff() {
    const handoff = phaseData.handoff;
    const section = el("section", {class: "handoff", "aria-labelledby": "phase-handoff-title"}, [
      el("h2", {id: "phase-handoff-title", text: "Phase handoff"}),
      el("p", {class: "subtitle", text: "What changed, how to inspect it, what follows, and whether anything needs your attention."})
    ]);
    const grid = el("div", {class: "handoff-grid"});

    const landed = el("section", {class: "handoff-card landed"}, [
      el("h3", {text: "What Just Landed"})
    ]);
    const landedList = el("ul", {class: "handoff-list"});
    handoff.what_just_landed.forEach((item) => landedList.append(el("li", {}, [
      el("strong", {text: item.title}),
      el("p", {text: item.detail})
    ])));
    landed.append(landedList);

    const demo = el("section", {class: "handoff-card demo"}, [
      el("h3", {text: "See For Yourself"})
    ]);
    if (!handoff.see_for_yourself.length) {
      demo.append(el("p", {class: "empty", text: "No separate user demo is needed for this phase."}));
    } else {
      handoff.see_for_yourself.forEach((item) => {
        const block = el("section", {class: "demo-block"}, [el("h4", {text: item.title})]);
        const steps = el("ol");
        item.steps.forEach((step) => steps.append(el("li", {}, el("code", {text: step}))));
        block.append(steps, el("p", {class: "expected"}, [
          el("strong", {text: "Expected: "}),
          document.createTextNode(item.expected)
        ]));
        demo.append(block);
      });
    }

    const next = el("section", {class: "handoff-card next"}, [
      el("h3", {text: "Coming Up Next"})
    ]);
    if (handoff.coming_up_next) {
      next.append(
        el("span", {class: "phase-pill", text: `Phase ${handoff.coming_up_next.phase_id}`}),
        el("h4", {text: handoff.coming_up_next.title}),
        el("p", {text: handoff.coming_up_next.summary})
      );
    } else {
      next.append(el("p", {class: "empty", text: "No next kickoff phase is scheduled."}));
    }

    const recommended = el("section", {class: "handoff-card steps"}, [
      el("h3", {text: "Recommended Steps"})
    ]);
    if (!handoff.recommended_steps.length) {
      recommended.append(el("p", {class: "empty", text: "Nothing requires your attention before the next kickoff."}));
    } else {
      const list = el("ul", {class: "handoff-list"});
      handoff.recommended_steps.forEach((item) => list.append(el("li", {}, [
        el("strong", {}, [
          el("span", {class: `recommendation-kind ${item.kind}`, text: item.kind}),
          document.createTextNode(item.title)
        ]),
        el("p", {text: item.detail})
      ])));
      recommended.append(list);
    }
    grid.append(landed, demo, next, recommended);
    section.append(grid);
    return section;
  }

  function renderOperatorParks(parks, target) {
    if (!parks.intervals.length) {
      target.append(el("p", {class: "empty", text: "No operator-input parks were recorded."}));
      return;
    }
    const basis = (item) => {
      if (item.method === "monotonic") return "Exact monotonic";
      if (item.method === "calendar-cross-boot") return "Calendar · cross-boot · non-exact";
      if (item.method === "open") return "Open · duration unavailable";
      return "Unavailable · clock order invalid";
    };
    target.append(table(
      ["Reason", "Opened (UTC)", "Closed (UTC)", "Duration", "Basis"],
      parks.intervals.map((item) => [
        titleCase(item.reason),
        item.opened_at,
        item.closed_at || "Still open",
        ns(item.duration_ns),
        basis(item)
      ])
    ));
  }

  function renderPhase() {
    if (!phaseData || phaseData.schema !== "agentic_starter.execution_dashboard.v1") throw new Error("Missing or invalid phase data");
    const phaseView = phaseData.phase_view;
    let active = phaseView;
    document.title = `Phase ${phaseData.phase_id} execution`;
    document.getElementById("crumb-date").textContent = `${phaseData.utc_date} UTC`;
    document.getElementById("crumb-phase").textContent = `Phase ${phaseData.phase_id}`;
    if (indexData) {
      const summary = indexData.phases.find((item) => item.phase_id === phaseData.phase_id);
      [["previous-phase", summary?.previous_href], ["next-phase", summary?.next_href]].forEach(([id, href]) => {
        if (!href) return;
        const anchor = document.getElementById(id);
        anchor.href = `../../${href}`;
        anchor.hidden = false;
      });
    }
    const header = el("section", {}, [
      el("p", {class: "eyebrow", text: `${phaseData.utc_date} UTC · exact monotonic telemetry`}),
      el("h1", {text: `Phase ${phaseData.phase_id}`}),
      el("p", {class: "lede", text: "A user-facing account of what made this build take as long as it did: agent work, automated checks, rework, and gaps in measurement."})
    ]);
    const traceSelect = el("select", {"aria-label": "Displayed execution view"});
    traceSelect.append(el("option", {
      value: "phase",
      text: "Complete accepted phase"
    }));
    phaseData.traces.forEach((trace, index) => {
      const label = trace.accepted
        ? "Accepted recovery run"
        : trace.unsuccessful
          ? `${index === 0 ? "Primary" : `Run ${index + 1}`} · issues found`
          : `${index === 0 ? "Primary" : `Run ${index + 1}`} · superseded`;
      traceSelect.append(el("option", {value: trace.trace_id, text: label}));
    });
    traceSelect.value = "phase";
    const exactButton = el("button", {type: "button", "aria-pressed": "false", text: "Show exact nanoseconds"});
    const toolbar = el("div", {class: "toolbar"}, [
      el("label", {}, [el("span", {text: "View"}), traceSelect]),
      exactButton
    ]);
    const content = el("div");
    const redraw = () => {
      charts.splice(0).forEach((chart) => chart.dispose());
      content.replaceChildren();
      const isPhase = active.view_type === "phase";
      const activities = activityRows(active);
      const automatedChecks = activities.find((row) => row.key === "automated_checks")?.value || 0;
      const unmeasured = activities.find((row) => row.key === "orchestration_unmeasured")?.value || 0;
      const failedActivities = meaningfulSpans(active).filter((span) => span.outcome !== "success").length;
      const summaryCards = [
        card(isPhase ? "Outcome" : "Run Outcome", active.unsuccessful ? "Issues found" : "Accepted", isPhase ? `${phaseData.trace_count} recorded run${phaseData.trace_count === 1 ? "" : "s"}` : "Final recorded outcome", active.unsuccessful ? "bad" : "good"),
        card("Elapsed Time", ns(active.calendar_elapsed_ns), isPhase ? "First start to accepted finish" : "Start to finish", "neutral"),
        card("Automated Checks", ns(automatedChecks), `${active.gate_run_count} run${active.gate_run_count === 1 ? "" : "s"} · ${active.failed_gate_count} unsuccessful`, "neutral"),
        card("Follow-Up Passes", String(active.role_followup_count), `${failedActivities} unsuccessful measured activit${failedActivities === 1 ? "y" : "ies"}`, "neutral"),
        card("Orchestration / Unmeasured", ns(unmeasured), `${pct(unmeasured / (active.makespan_ns || 1))} of recorded execution`, unmeasured ? "bad" : "good")
      ];
      if (isPhase) {
        const parks = active.operator_parks;
        const detail = parks.open
          ? `${parks.intervals.length} interval${parks.intervals.length === 1 ? "" : "s"} · an interval is still open`
          : parks.total_exact
            ? `${parks.intervals.length} interval${parks.intervals.length === 1 ? "" : "s"} · exact monotonic union`
            : `${parks.intervals.length} interval${parks.intervals.length === 1 ? "" : "s"} · calendar union · non-exact`;
        summaryCards.push(card("Awaiting User Input", parks.open ? "Open" : ns(parks.total_duration_ns), detail, parks.open ? "bad" : "neutral"));
      }
      content.append(el("section", {class: "cards", "aria-label": "Outcome summary"}, summaryCards), renderHandoff());
      const grid = el("div", {class: "grid"});
      const activity = panel("Where the Build Time Went", "Mutually exclusive elapsed time for the four agent activities, automated checks, integration, and genuine measurement gaps. Wait mirrors are deliberately excluded.", true);
      renderActivityBreakdown(active, activity);
      const slow = panel("Longest Activities", "The individual agent passes and automated checks most likely to contain an actionable bottleneck.");
      renderSlowest(active, slow);
      const gates = panel("Automated Checks", "Repeated and slow validation runs show whether test execution—not agent work—is extending the build.");
      renderGateBreakdown(active, gates);
      const waterfall = panel("Build Timeline", "Material agent activities and automated checks in chronological order. Internal IDs, root wrappers, wait mirrors, and successful activities under five seconds are omitted.", true);
      renderWaterfall(active, waterfall);
      const hasConvergence = Boolean(active.review_convergence?.length);
      const attempts = hasConvergence
        ? panel("Review Convergence", "Actionable findings should fall toward zero on successive Plan Review and Code Review passes; increases and stalls expose non-converging rework.", true)
        : panel("Rework", "Additional Planning, Plan Review, Implementation, and Code Review passes are separated from unsuccessful automated checks.", true);
      if (hasConvergence) renderConvergence(active, attempts);
      else renderRework(active, attempts);
      grid.append(activity, slow, gates, waterfall, attempts);
      if (isPhase) {
        const parks = panel("Awaiting User Input", "Each phase-level park is separate from agent work, automated checks, and orchestration gaps. Cross-boot durations are visibly non-exact.", true);
        renderOperatorParks(active.operator_parks, parks);
        grid.append(parks);
      }
      if (Object.keys(active.concurrency_groups).length) {
        const concurrency = panel("Parallel Work", "Observed overlap appears only when the telemetry contains a valid concurrency denominator.", true);
        renderConcurrency(active, concurrency);
        grid.append(concurrency);
      }
      content.append(grid);
      charts.forEach((chart) => chart.resize());
    };
    traceSelect.addEventListener("change", () => {
      active = traceSelect.value === "phase"
        ? phaseView
        : phaseData.traces.find((trace) => trace.trace_id === traceSelect.value);
      redraw();
    });
    exactButton.addEventListener("click", () => {
      exact = !exact;
      exactButton.setAttribute("aria-pressed", String(exact));
      exactButton.textContent = exact ? "Use readable durations" : "Show exact nanoseconds";
      redraw();
    });
    app.replaceChildren(header, toolbar, content);
    redraw();
  }

  function renderTrend(phases, target) {
    const chart = chartNode("Cross-phase elapsed build time. A table follows.");
    target.append(chart);
    initChart(chart, {
      grid: {left: 60, right: 35, top: 25, bottom: 55},
      tooltip: {trigger: "axis", renderMode: "richText"},
      xAxis: {type: "category", data: phases.map((item) => `Phase ${item.phase_id}`), axisLabel: {interval: 0, rotate: 28}},
      yAxis: {type: "value", name: "Minutes", axisLabel: {formatter: axisMinutes}},
      series: [{
        name: "Elapsed Time",
        type: "bar",
        data: phases.map((item) => nsToMinutes(item.calendar_elapsed_ns)),
        itemStyle: {color: palette.implementation, borderRadius: [4, 4, 0, 0]},
        label: {show: true, position: "top", formatter: (item) => ns(phases[item.dataIndex].calendar_elapsed_ns)}
      }]
    });
    target.append(detailsTable("Cross-phase values", ["Phase", "Elapsed Time", "Awaiting User Input", "Follow-Up Passes", "Automated Check Runs", "Unsuccessful Checks"], phases.map((item) => [
      item.phase_id, ns(item.calendar_elapsed_ns), ns(item.awaiting_user_input_ns), item.role_followup_count, item.gate_run_count, item.failed_gate_count
    ])));
  }

  function renderIndex() {
    if (!indexData || indexData.schema !== "agentic_starter.execution_dashboard_index.v1") throw new Error("Missing or invalid archive data");
    document.title = "Execution dashboard archive";
    const header = el("section", {}, [
      el("p", {class: "eyebrow", text: "Offline execution archive · UTC"}),
      el("h1", {text: "Phase execution"}),
      el("p", {class: "lede", text: "Chronological, exact wall-clock telemetry for completed kickoff phases. No cost or inferred historical data appears here."})
    ]);
    const phases = indexData.phases;
    if (!phases.length) { app.replaceChildren(header, el("p", {class: "empty", text: "No exact phase dashboards are available."})); return; }
    const grid = el("div", {class: "grid"});
    const trend = panel("Cross-Phase Build Time", "Elapsed time is the primary user cost; follow-up passes and automated-check runs remain available in the table.", true);
    renderTrend(phases, trend);
    grid.append(trend);
    const archive = el("section", {class: "archive-group"}, [el("h2", {text: "Chronological archive"})]);
    indexData.dates.forEach((date) => {
      const group = el("section", {class: "archive-group"}, [el("h3", {text: `${date.utc_date} UTC`})]);
      const list = el("ul", {class: "archive-list"});
      date.phases.forEach((phaseId) => {
        const item = phases.find((phase) => phase.phase_id === phaseId);
        const anchor = el("a", {class: `archive-link${item.failed_trace_count ? " has-failure" : ""}`, href: item.href}, [
          outcomeMark(item.outcome),
          el("span", {}, [
            el("span", {class: "phase", text: `Phase ${item.phase_id}`}),
            el("span", {class: "meta", text: ` · ${item.trace_count} recorded run${item.trace_count === 1 ? "" : "s"} · ${item.failed_trace_count} required recovery`})
          ]),
          el("strong", {text: ns(item.calendar_elapsed_ns)})
        ]);
        list.append(el("li", {}, anchor));
      });
      group.append(list);
      archive.append(group);
    });
    app.replaceChildren(header, grid, archive);
    charts.forEach((chart) => chart.resize());
  }

  try {
    if (document.body.dataset.view === "phase") renderPhase();
    else renderIndex();
    window.addEventListener("resize", () => charts.forEach((chart) => chart.resize()));
  } catch (error) {
    app.replaceChildren(el("section", {class: "panel"}, [
      el("h1", {text: "Dashboard unavailable"}),
      el("p", {text: "The local dashboard data failed validation or rendering."}),
      el("pre", {text: String(error)})
    ]));
  }
})();
