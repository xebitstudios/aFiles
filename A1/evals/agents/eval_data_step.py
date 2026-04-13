"""
Eval for the Data Step Agent.
"""

from agents.data_step_agent import DataStepAgent
from evals.base_eval import BaseEval


class DataStepEval(BaseEval):
    agent_name = "data_step"

    def __init__(self, model: str = "claude-sonnet-4-6"):
        super().__init__(model=model)
        self.agent = DataStepAgent(model=model)

    def run_agent(self, sas_input: str, context: dict | None = None) -> str:
        result = self.agent.convert(sas_input, context)
        return result.python_code
