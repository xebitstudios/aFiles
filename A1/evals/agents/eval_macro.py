"""
Eval for the Macro Agent.
"""

from agents.macro_agent import MacroAgent
from evals.base_eval import BaseEval


class MacroEval(BaseEval):
    agent_name = "macro"

    def __init__(self, model: str = "claude-sonnet-4-6"):
        super().__init__(model=model)
        self.agent = MacroAgent(model=model)

    def run_agent(self, sas_input: str, context: dict | None = None) -> str:
        result = self.agent.convert(sas_input, context)
        return result.python_code
