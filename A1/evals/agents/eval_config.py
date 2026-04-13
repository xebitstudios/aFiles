"""
Eval for the Config Agent.
"""

from agents.config_agent import ConfigAgent
from evals.base_eval import BaseEval


class ConfigEval(BaseEval):
    agent_name = "config"

    def __init__(self, model: str = "claude-sonnet-4-6"):
        super().__init__(model=model)
        self.agent = ConfigAgent(model=model)

    def run_agent(self, sas_input: str, context: dict | None = None) -> str:
        result = self.agent.convert(sas_input, context)
        return result.python_code
