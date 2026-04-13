"""
Base Eval — abstract base class for all agent evaluators.

Provides the common evaluate() flow:
  1. Run the agent on the test input
  2. Run all five checkers on the output
  3. Compute the weighted overall score
  4. Return an EvalResult
"""

import logging
from abc import ABC, abstractmethod

from evals.scoring import Dimension, DimensionScore, EvalResult
from evals.checkers import (
    check_completeness,
    check_correctness,
    check_executability,
    check_quality,
    check_syntax,
)

logger = logging.getLogger(__name__)


class BaseEval(ABC):
    """Abstract base for agent-specific evaluators."""

    agent_name: str = "base"

    def __init__(self, model: str = "claude-sonnet-4-6"):
        self.model = model

    @abstractmethod
    def run_agent(self, sas_input: str, context: dict | None = None) -> str:
        """
        Run the agent under test on the given SAS input.
        Returns the generated Python code string.
        """
        ...

    def evaluate(
        self,
        test_case_id: str,
        sas_input: str,
        context: dict | None = None,
        expected_python: str | None = None,
        skip_llm_checks: bool = False,
    ) -> EvalResult:
        """
        Full evaluation of one test case.

        Args:
            test_case_id:    Unique identifier for the test case.
            sas_input:       The SAS code to convert.
            context:         Optional context dict passed to the agent.
            expected_python: Optional reference Python for comparison.
            skip_llm_checks: If True, skip LLM-based correctness/quality checks
                             (useful for fast local iteration).
        """
        # Step 1: Run the agent
        logger.info("[%s] Running agent on test case: %s", self.agent_name, test_case_id)
        try:
            python_output = self.run_agent(sas_input, context)
        except Exception as e:
            logger.error("[%s] Agent failed on %s: %s", self.agent_name, test_case_id, e)
            return EvalResult(
                test_case_id=test_case_id,
                agent_name=self.agent_name,
                sas_input=sas_input,
                python_output="",
                dimension_scores=[
                    DimensionScore(Dimension.SYNTAX, 0.0, details=f"Agent error: {e}"),
                    DimensionScore(Dimension.COMPLETENESS, 0.0),
                    DimensionScore(Dimension.CORRECTNESS, 0.0),
                    DimensionScore(Dimension.QUALITY, 0.0),
                    DimensionScore(Dimension.EXECUTABILITY, 0.0),
                ],
                overall_score=0.0,
                warnings=[f"Agent raised exception: {e}"],
            )

        # Step 2: Run checkers
        scores: list[DimensionScore] = []

        # Always run syntax (no LLM needed)
        scores.append(check_syntax(python_output))

        # Always run completeness (heuristic, no LLM)
        scores.append(check_completeness(sas_input, python_output))

        # Always run executability (no LLM needed)
        scores.append(check_executability(python_output))

        # LLM-based checks
        if skip_llm_checks:
            scores.append(DimensionScore(Dimension.CORRECTNESS, 0.5, details="Skipped (--fast mode)"))
            scores.append(DimensionScore(Dimension.QUALITY, 0.5, details="Skipped (--fast mode)"))
        else:
            scores.append(check_correctness(sas_input, python_output, model=self.model))
            scores.append(check_quality(python_output, model=self.model))

        # Step 3: Build result
        result = EvalResult(
            test_case_id=test_case_id,
            agent_name=self.agent_name,
            sas_input=sas_input,
            python_output=python_output,
            dimension_scores=scores,
            metadata={"expected_python": expected_python} if expected_python else {},
        )
        result.compute_overall()

        logger.info(
            "[%s] %s — overall: %.2f  (syntax=%.2f, complete=%.2f, correct=%.2f, quality=%.2f, exec=%.2f)",
            self.agent_name, test_case_id, result.overall_score,
            *[ds.score for ds in scores],
        )

        return result
