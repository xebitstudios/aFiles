"""
End-to-End Eval — tests the full orchestrator pipeline on complete SAS programs.

Evaluates: does the orchestrator correctly parse, route, convert, validate,
assemble, and produce a runnable Python script?
"""

import logging
import tempfile
from pathlib import Path

from agents.orchestrator import Orchestrator
from evals.scoring import Dimension, DimensionScore, EvalResult
from evals.checkers import (
    check_completeness,
    check_correctness,
    check_executability,
    check_quality,
    check_syntax,
)

logger = logging.getLogger(__name__)


class EndToEndEval:
    """Evaluate the full SAS-to-Python conversion pipeline."""

    agent_name = "orchestrator_e2e"

    def __init__(self, config_path: str | None = None, model: str = "claude-sonnet-4-6"):
        self.model = model
        self.orchestrator = Orchestrator(config_path=config_path)

    def evaluate(
        self,
        test_case_id: str,
        sas_input: str,
        skip_llm_checks: bool = False,
    ) -> EvalResult:
        """
        Run the full pipeline on a SAS program and evaluate the output.
        """
        logger.info("[e2e] Evaluating: %s", test_case_id)

        # Write SAS to temp file, run orchestrator, read output
        python_output = ""
        pipeline_error = None

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                sas_path = Path(tmpdir) / "test_input.sas"
                py_path = Path(tmpdir) / "test_output.py"
                sas_path.write_text(sas_input, encoding="utf-8")

                self.orchestrator.convert_file(
                    sas_file=str(sas_path),
                    output_file=str(py_path),
                )
                python_output = py_path.read_text(encoding="utf-8")
        except Exception as e:
            pipeline_error = str(e)
            logger.error("[e2e] Pipeline failed on %s: %s", test_case_id, e)

        # If pipeline failed entirely, score 0
        if pipeline_error:
            return EvalResult(
                test_case_id=test_case_id,
                agent_name=self.agent_name,
                sas_input=sas_input,
                python_output="",
                dimension_scores=[
                    DimensionScore(Dimension.SYNTAX, 0.0, details=f"Pipeline error: {pipeline_error}"),
                    DimensionScore(Dimension.COMPLETENESS, 0.0),
                    DimensionScore(Dimension.CORRECTNESS, 0.0),
                    DimensionScore(Dimension.QUALITY, 0.0),
                    DimensionScore(Dimension.EXECUTABILITY, 0.0),
                ],
                overall_score=0.0,
                warnings=[f"Pipeline error: {pipeline_error}"],
            )

        # Run all checkers
        scores: list[DimensionScore] = [
            check_syntax(python_output),
            check_completeness(sas_input, python_output),
            check_executability(python_output),
        ]

        if skip_llm_checks:
            scores.append(DimensionScore(Dimension.CORRECTNESS, 0.5, details="Skipped"))
            scores.append(DimensionScore(Dimension.QUALITY, 0.5, details="Skipped"))
        else:
            scores.append(check_correctness(sas_input, python_output, model=self.model))
            scores.append(check_quality(python_output, model=self.model))

        result = EvalResult(
            test_case_id=test_case_id,
            agent_name=self.agent_name,
            sas_input=sas_input,
            python_output=python_output,
            dimension_scores=scores,
        )
        result.compute_overall()

        logger.info(
            "[e2e] %s — overall: %.2f  (syn=%.2f, comp=%.2f, corr=%.2f, qual=%.2f, exec=%.2f)",
            test_case_id, result.overall_score,
            *[ds.score for ds in scores],
        )

        return result
