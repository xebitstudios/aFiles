"""
Scoring Framework — defines the metrics used to evaluate SAS-to-Python conversions.

Five evaluation dimensions, each scored 0.0 – 1.0:

1. SYNTAX      — Does the Python code parse without errors?
2. COMPLETENESS — Are all SAS constructs accounted for in the output?
3. CORRECTNESS  — Does the Python logic match the SAS logic?
4. QUALITY      — Is the code idiomatic, readable, and well-structured?
5. EXECUTABILITY — Can the Python code run without import/runtime errors?

An overall weighted score combines all five.
"""

from dataclasses import dataclass, field
from enum import Enum


class Dimension(Enum):
    SYNTAX = "syntax"
    COMPLETENESS = "completeness"
    CORRECTNESS = "correctness"
    QUALITY = "quality"
    EXECUTABILITY = "executability"


# Default weights — correctness matters most, syntax is table stakes
DEFAULT_WEIGHTS: dict[Dimension, float] = {
    Dimension.SYNTAX: 0.15,
    Dimension.COMPLETENESS: 0.20,
    Dimension.CORRECTNESS: 0.35,
    Dimension.QUALITY: 0.10,
    Dimension.EXECUTABILITY: 0.20,
}


@dataclass
class DimensionScore:
    dimension: Dimension
    score: float  # 0.0 – 1.0
    max_score: float = 1.0
    details: str = ""
    sub_scores: dict[str, float] = field(default_factory=dict)


@dataclass
class EvalResult:
    """Complete evaluation result for one test case."""
    test_case_id: str
    agent_name: str
    sas_input: str
    python_output: str
    dimension_scores: list[DimensionScore]
    overall_score: float = 0.0
    warnings: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def compute_overall(self, weights: dict[Dimension, float] | None = None):
        """Compute the weighted overall score."""
        w = weights or DEFAULT_WEIGHTS
        total_weight = sum(w.get(ds.dimension, 0) for ds in self.dimension_scores)
        if total_weight == 0:
            self.overall_score = 0.0
            return
        self.overall_score = sum(
            ds.score * w.get(ds.dimension, 0) for ds in self.dimension_scores
        ) / total_weight


@dataclass
class AgentEvalSummary:
    """Aggregated eval results across multiple test cases for one agent."""
    agent_name: str
    num_cases: int
    avg_overall: float
    avg_by_dimension: dict[str, float]
    pass_rate: float  # fraction of cases scoring above threshold
    worst_cases: list[str]  # test case IDs with lowest scores
    results: list[EvalResult]


def summarise_results(results: list[EvalResult], pass_threshold: float = 0.7) -> AgentEvalSummary:
    """Aggregate a list of EvalResults into a summary."""
    if not results:
        return AgentEvalSummary(
            agent_name="unknown", num_cases=0, avg_overall=0.0,
            avg_by_dimension={}, pass_rate=0.0, worst_cases=[], results=[],
        )

    agent_name = results[0].agent_name

    # Average overall
    avg_overall = sum(r.overall_score for r in results) / len(results)

    # Average by dimension
    dim_totals: dict[str, list[float]] = {}
    for r in results:
        for ds in r.dimension_scores:
            dim_totals.setdefault(ds.dimension.value, []).append(ds.score)
    avg_by_dimension = {k: sum(v) / len(v) for k, v in dim_totals.items()}

    # Pass rate
    passing = sum(1 for r in results if r.overall_score >= pass_threshold)
    pass_rate = passing / len(results)

    # Worst cases
    sorted_results = sorted(results, key=lambda r: r.overall_score)
    worst_cases = [r.test_case_id for r in sorted_results[:3]]

    return AgentEvalSummary(
        agent_name=agent_name,
        num_cases=len(results),
        avg_overall=avg_overall,
        avg_by_dimension=avg_by_dimension,
        pass_rate=pass_rate,
        worst_cases=worst_cases,
        results=results,
    )
