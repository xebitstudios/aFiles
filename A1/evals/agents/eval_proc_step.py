"""
Eval for the Proc Step Agent.
"""

from agents.proc_step_agent import ProcStepAgent
from evals.base_eval import BaseEval


class ProcStepEval(BaseEval):
    agent_name = "proc_step"

    def __init__(self, model: str = "claude-sonnet-4-6"):
        super().__init__(model=model)
        self.agent = ProcStepAgent(model=model)

    def run_agent(self, sas_input: str, context: dict | None = None) -> str:
        result = self.agent.convert(sas_input, context)
        return result.python_code
