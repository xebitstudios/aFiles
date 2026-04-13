"""
Eval for the IO Agent.
"""

from agents.io_agent import IOAgent
from evals.base_eval import BaseEval


class IOEval(BaseEval):
    agent_name = "io"

    def __init__(self, model: str = "claude-sonnet-4-6"):
        super().__init__(model=model)
        self.agent = IOAgent(model=model)

    def run_agent(self, sas_input: str, context: dict | None = None) -> str:
        result = self.agent.convert(sas_input, context)
        return result.python_code
