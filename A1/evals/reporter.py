"""
Reporter — generates human-readable and machine-readable eval reports.

Outputs:
  - Console summary table
  - JSON results file for programmatic analysis
  - Markdown report for sharing
"""

import json
import logging
from datetime import datetime
from pathlib import Path

from evals.scoring import AgentEvalSummary, Dimension, EvalResult, summarise_results

logger = logging.getLogger(__name__)


def print_console_report(summaries: list[AgentEvalSummary]):
    """Print a formatted summary table to the console."""
    print("\n" + "=" * 90)
    print("  SAS-TO-PYTHON EVALUATION REPORT")
    print(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 90)

    # Header
    print(f"\n{'Agent':<18} {'Cases':>5} {'Pass%':>6} {'Overall':>8} "
          f"{'Syntax':>8} {'Complete':>8} {'Correct':>8} {'Quality':>8} {'Exec':>8}")
    print("-" * 90)

    for s in summaries:
        dims = s.avg_by_dimension
        print(
            f"{s.agent_name:<18} {s.num_cases:>5} {s.pass_rate:>5.0%} "
            f"{s.avg_overall:>8.2f} "
            f"{dims.get('syntax', 0):>8.2f} "
            f"{dims.get('completeness', 0):>8.2f} "
            f"{dims.get('correctness', 0):>8.2f} "
            f"{dims.get('quality', 0):>8.2f} "
            f"{dims.get('executability', 0):>8.2f}"
        )

    print("-" * 90)

    # Overall system score
    if summaries:
        system_avg = sum(s.avg_overall for s in summaries) / len(summaries)
        system_pass = sum(s.pass_rate for s in summaries) / len(summaries)
        print(f"{'SYSTEM AVERAGE':<18} {'':>5} {system_pass:>5.0%} {system_avg:>8.2f}")

    print("=" * 90)

    # Worst cases
    all_worst = []
    for s in summaries:
        if s.worst_cases:
            all_worst.extend([(wc, s.agent_name) for wc in s.worst_cases])
    if all_worst:
        print("\n  Lowest-scoring test cases:")
        for case_id, agent in all_worst[:10]:
            print(f"    - {case_id} ({agent})")

    print()


def save_json_report(summaries: list[AgentEvalSummary], results: list[EvalResult], output_path: str):
    """Save detailed results as JSON."""
    report = {
        "generated_at": datetime.now().isoformat(),
        "summaries": [],
        "results": [],
    }

    for s in summaries:
        report["summaries"].append({
            "agent_name": s.agent_name,
            "num_cases": s.num_cases,
            "avg_overall": round(s.avg_overall, 4),
            "avg_by_dimension": {k: round(v, 4) for k, v in s.avg_by_dimension.items()},
            "pass_rate": round(s.pass_rate, 4),
            "worst_cases": s.worst_cases,
        })

    for r in results:
        report["results"].append({
            "test_case_id": r.test_case_id,
            "agent_name": r.agent_name,
            "overall_score": round(r.overall_score, 4),
            "dimension_scores": {
                ds.dimension.value: {
                    "score": round(ds.score, 4),
                    "details": ds.details,
                    "sub_scores": {k: round(v, 4) for k, v in ds.sub_scores.items()},
                }
                for ds in r.dimension_scores
            },
            "warnings": r.warnings,
        })

    Path(output_path).write_text(json.dumps(report, indent=2), encoding="utf-8")
    logger.info("JSON report saved to %s", output_path)


def save_markdown_report(summaries: list[AgentEvalSummary], results: list[EvalResult], output_path: str):
    """Save a Markdown report."""
    lines = [
        "# SAS-to-Python Evaluation Report",
        f"",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"",
        "## Summary",
        "",
        "| Agent | Cases | Pass Rate | Overall | Syntax | Completeness | Correctness | Quality | Executability |",
        "|-------|------:|----------:|--------:|-------:|-------------:|------------:|--------:|--------------:|",
    ]

    for s in summaries:
        d = s.avg_by_dimension
        lines.append(
            f"| {s.agent_name} | {s.num_cases} | {s.pass_rate:.0%} | {s.avg_overall:.2f} | "
            f"{d.get('syntax', 0):.2f} | {d.get('completeness', 0):.2f} | "
            f"{d.get('correctness', 0):.2f} | {d.get('quality', 0):.2f} | "
            f"{d.get('executability', 0):.2f} |"
        )

    if summaries:
        sys_avg = sum(s.avg_overall for s in summaries) / len(summaries)
        lines.append(f"| **SYSTEM** | | | **{sys_avg:.2f}** | | | | | |")

    lines.append("")
    lines.append("## Dimension Scoring Weights")
    lines.append("")
    lines.append("| Dimension | Weight | Description |")
    lines.append("|-----------|-------:|-------------|")
    lines.append("| Syntax | 15% | Python code parses without errors |")
    lines.append("| Completeness | 20% | All SAS constructs accounted for |")
    lines.append("| Correctness | 35% | Logic faithfully reproduces SAS |")
    lines.append("| Quality | 10% | Idiomatic, readable Python code |")
    lines.append("| Executability | 20% | Code can run without import/runtime errors |")

    # Per-agent details
    lines.append("")
    lines.append("## Per-Agent Details")
    for s in summaries:
        lines.append(f"")
        lines.append(f"### {s.agent_name}")
        lines.append(f"")
        if s.worst_cases:
            lines.append(f"**Lowest-scoring cases:** {', '.join(s.worst_cases)}")
            lines.append("")

        agent_results = [r for r in results if r.agent_name == s.agent_name]
        if agent_results:
            lines.append("| Test Case | Overall | Syntax | Complete | Correct | Quality | Exec |")
            lines.append("|-----------|--------:|-------:|---------:|--------:|--------:|-----:|")
            for r in agent_results:
                ds = {d.dimension.value: d.score for d in r.dimension_scores}
                lines.append(
                    f"| {r.test_case_id} | {r.overall_score:.2f} | "
                    f"{ds.get('syntax', 0):.2f} | {ds.get('completeness', 0):.2f} | "
                    f"{ds.get('correctness', 0):.2f} | {ds.get('quality', 0):.2f} | "
                    f"{ds.get('executability', 0):.2f} |"
                )

    # Warnings section
    all_warnings = []
    for r in results:
        for w in r.warnings:
            all_warnings.append(f"- **{r.test_case_id}**: {w}")
    if all_warnings:
        lines.append("")
        lines.append("## Warnings")
        lines.append("")
        lines.extend(all_warnings)

    Path(output_path).write_text("\n".join(lines), encoding="utf-8")
    logger.info("Markdown report saved to %s", output_path)
