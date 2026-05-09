# ==========================================================
# SAS → Python Multi-Agent Migration Pipeline (LLM-Integrated)
# ==========================================================

import os
import json
from typing import Dict, Any, List
from openai import OpenAI

client = OpenAI()

# -----------------------------
# LLM Utility
# -----------------------------
def call_llm(system_prompt: str, user_prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-5-3",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0
    )
    return response.choices[0].message.content

# -----------------------------
# Artifact Store
# -----------------------------
class ArtifactStore:
    def __init__(self, base_path="artifacts"):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)

    def save(self, name: str, data: Any):
        path = os.path.join(self.base_path, name)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        return path

    def load(self, name: str):
        path = os.path.join(self.base_path, name)
        with open(path, "r") as f:
            return json.load(f)

# -----------------------------
# Base Agent
# -----------------------------
class Agent:
    def __init__(self, name: str):
        self.name = name

    def run(self, context: Dict[str, Any], store: ArtifactStore):
        raise NotImplementedError

# -----------------------------
# Agents with LLM Prompts
# -----------------------------
class MacroExpansionAgent(Agent):
    def run(self, context, store):
        repo_path = context["repo_path"]
        expanded = {}

        for file in os.listdir(repo_path):
            if file.endswith(".sas"):
                with open(os.path.join(repo_path, file)) as f:
                    content = f.read()

                system = "You are a SAS macro expansion engine. Expand all macros and includes fully."
                user = f"Expand this SAS code fully:\n{content}"

                expanded[file] = call_llm(system, user)

        store.save("expanded_sas.json", expanded)
        return expanded

class SemanticParserAgent(Agent):
    def run(self, context, store):
        expanded = store.load("expanded_sas.json")
        ir = {}

        for k, v in expanded.items():
            system = "You convert SAS code into structured intermediate representation JSON."
            user = f"Extract transformations, inputs, outputs, joins, aggregations:\n{v}"

            ir[k] = json.loads(call_llm(system, user))

        store.save("logic_ir.json", ir)
        return ir

class ConversionAgent(Agent):
    def run(self, context, store):
        ir = store.load("logic_ir.json")
        code = {}

        for k, v in ir.items():
            system = "You convert structured IR into production-grade Python using pandas or pyspark."
            user = f"Convert this IR into Python code:\n{json.dumps(v, indent=2)}"

            code[k.replace('.sas', '.py')] = call_llm(system, user)

        store.save("converted_code.json", code)
        return code

class TestGenerationAgent(Agent):
    def run(self, context, store):
        ir = store.load("logic_ir.json")

        system = "Generate test cases with input and expected outputs for data pipelines."
        user = f"Create test cases for:\n{json.dumps(ir, indent=2)}"

        tests = call_llm(system, user)
        store.save("test_cases.json", {"content": tests})
        return tests

class ValidationAgent(Agent):
    def run(self, context, store):
        code = store.load("converted_code.json")

        system = "Compare expected vs actual outputs logically."
        user = f"Validate correctness of this converted code:\n{json.dumps(code, indent=2)}"

        report = call_llm(system, user)
        store.save("validation_report.json", {"content": report})
        return report

class AutoFixAgent(Agent):
    def run(self, context, store):
        report = store.load("validation_report.json")
        code = store.load("converted_code.json")

        system = "Fix Python code based on validation errors. Return corrected code only."
        user = f"Fix issues:\nReport:{report}\nCode:{json.dumps(code, indent=2)}"

        fixed = call_llm(system, user)
        store.save("patched_code.json", {"content": fixed})
        return fixed

class ReportingAgent(Agent):
    def run(self, context, store):
        system = "Generate a migration summary report."
        user = "Summarize all migration steps and outcomes."

        report = call_llm(system, user)
        store.save("final_report.json", {"content": report})
        return report

# -----------------------------
# Orchestrator
# -----------------------------
class PipelineOrchestrator:
    def __init__(self, agents: List[Agent], store: ArtifactStore):
        self.agents = agents
        self.store = store

    def run(self, context: Dict[str, Any]):
        for agent in self.agents:
            print(f"Running {agent.name}...")
            agent.run(context, self.store)

# -----------------------------
# Run Pipeline
# -----------------------------
if __name__ == "__main__":
    store = ArtifactStore()

    agents = [
        MacroExpansionAgent("Macro Expansion"),
        SemanticParserAgent("Semantic Parser"),
        ConversionAgent("Conversion"),
        TestGenerationAgent("Test Generation"),
        ValidationAgent("Validation"),
        AutoFixAgent("Auto Fix"),
        ReportingAgent("Reporting")
    ]

    orchestrator = PipelineOrchestrator(agents, store)

    context = {
        "repo_path": "./sas_repo"
    }

    orchestrator.run(context)

# ==========================================================
# NOTES
# ==========================================================
# - Replace model with your deployed LLM endpoint if needed
# - Add retry + guardrails for JSON parsing
# - Add cost tracking per agent
# - Add memory (vector DB) for reuse across runs
# ==========================================================
