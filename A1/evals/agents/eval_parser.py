"""
Eval for the Parser Agent.

The parser is evaluated differently — it doesn't produce Python code.
Instead we check: block count accuracy, block type accuracy, and
dependency detection.
"""

import logging

from agents.parser_agent import ParserAgent
from evals.scoring import Dimension, DimensionScore, EvalResult
from tools.sas_tokenizer import BlockType

logger = logging.getLogger(__name__)


class ParserEval:
    agent_name = "parser"

    def __init__(self, model: str = "claude-sonnet-4-6"):
        self.model = model
        self.agent = ParserAgent(model=model)

    def evaluate(
        self,
        test_case_id: str,
        sas_input: str,
        expected_block_types: list[str],
        expected_block_count: int | None = None,
    ) -> EvalResult:
        """
        Evaluate the parser on a test case.

        Args:
            test_case_id:         Unique test ID.
            sas_input:            SAS source code.
            expected_block_types: Ordered list of expected BlockType values.
            expected_block_count: Expected number of blocks (optional).
        """
        logger.info("[parser] Evaluating test case: %s", test_case_id)

        try:
            blocks, analysis = self.agent.parse(sas_input)
        except Exception as e:
            logger.error("[parser] Failed: %s", e)
            return EvalResult(
                test_case_id=test_case_id,
                agent_name="parser",
                sas_input=sas_input,
                python_output="",
                dimension_scores=[DimensionScore(Dimension.CORRECTNESS, 0.0, details=str(e))],
                overall_score=0.0,
            )

        scores: list[DimensionScore] = []

        # Score 1: Block count accuracy
        actual_count = len(blocks)
        exp_count = expected_block_count or len(expected_block_types)
        count_score = 1.0 if actual_count == exp_count else max(0.0, 1.0 - abs(actual_count - exp_count) / max(exp_count, 1))
        scores.append(DimensionScore(
            dimension=Dimension.COMPLETENESS,
            score=count_score,
            details=f"Expected {exp_count} blocks, got {actual_count}.",
        ))

        # Score 2: Block type accuracy
        actual_types = [b.block_type.value for b in blocks]
        matches = 0
        total = max(len(expected_block_types), len(actual_types))
        for i in range(min(len(expected_block_types), len(actual_types))):
            if expected_block_types[i] == actual_types[i]:
                matches += 1
        type_score = matches / total if total > 0 else 1.0
        scores.append(DimensionScore(
            dimension=Dimension.CORRECTNESS,
            score=type_score,
            details=f"Type match: {matches}/{total}. Expected: {expected_block_types}, Got: {actual_types}",
        ))

        # Score 3: Analysis quality — did the LLM return valid analysis?
        analysis_score = 1.0 if len(analysis) == len(blocks) else 0.5
        scores.append(DimensionScore(
            dimension=Dimension.QUALITY,
            score=analysis_score,
            details=f"Analysis entries: {len(analysis)}, blocks: {len(blocks)}.",
        ))

        result = EvalResult(
            test_case_id=test_case_id,
            agent_name="parser",
            sas_input=sas_input,
            python_output=str(actual_types),
            dimension_scores=scores,
        )
        result.compute_overall()
        return result
