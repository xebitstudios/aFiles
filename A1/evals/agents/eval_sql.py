"""
Eval for the SQL Agent.
"""

from agents.sql_agent import SQLAgent
from evals.base_eval import BaseEval


class SQLEval(BaseEval):
    agent_name = "sql"

    def __init__(self, model: str = "claude-sonnet-4-6"):
        super().__init__(model=model)
        self.agent = SQLAgent(model=model)

    def run_agent(self, sas_input: str, context: dict | None = None) -> str:
        result = self.agent.convert(sas_input, context)
        return result.python_code
