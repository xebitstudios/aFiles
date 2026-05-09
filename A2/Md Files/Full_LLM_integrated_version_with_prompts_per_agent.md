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

Now you’ve got a **fully LLM-integrated multi-agent pipeline** in the canvas.

But here’s the reality check: this version is powerful, yet still *fragile* in production unless you harden a few critical areas.

---

## What you just gained

This upgrade turns your system into a true **cognitive migration engine**:

* Each agent now has:

  * A **clear role**
  * A **dedicated prompt**
  * A **bounded responsibility**
* The pipeline is no longer rule-based—it’s **reasoning-driven**
* You can now handle:

  * Complex SAS macros
  * Non-trivial transformations
  * Messy enterprise codebases

---

## Where this will break (and how to fix it)

### 1. JSON parsing will fail (guaranteed)

Right now:

```python
ir[k] = json.loads(call_llm(...))
```

This will crash when the LLM:

* Adds commentary
* Produces invalid JSON

### Fix:

Wrap with:

```python
def safe_json_parse(text):
    try:
        return json.loads(text)
    except:
        # fallback: extract JSON block
        import re
        match = re.search(r\"\\{.*\\}\", text, re.DOTALL)
        return json.loads(match.group())
```

---

### 2. Prompts are too generic

Current prompts work—but they’re not **enterprise-grade deterministic**.

Example upgrade:

Instead of:

```
Convert this IR into Python code
```

Use:

```
Convert IR into production-grade Python.

STRICT REQUIREMENTS:
- Use pandas unless dataset > 10M rows → use PySpark
- Preserve column names exactly
- No placeholder logic
- Output ONLY executable Python code
- No explanations
```

---

### 3. No feedback loop yet (this is huge)

Right now:

```
Validation → AutoFix → STOP
```

You actually want:

```
Validation → AutoFix → Conversion → Validation → (loop)
```

Until:

* PASS
* or retry limit hit

---

### 4. No memory / learning

Every run starts from zero.

You should add:

* Vector DB (FAISS / Chroma)
* Store:

  * SAS pattern → Python mapping
  * Common fixes

Then inject into prompts:

```
Here are similar past conversions:
...
```

---

### 5. Cost will explode without control

Each agent = multiple LLM calls.

Add:

* Token tracking per agent
* Budget guardrails
* Caching layer

---

## What this system now enables (this is the big leap)

You’ve effectively built a foundation for:

### 1. Self-healing migration system

* Detects errors
* Fixes itself
* Re-validates

### 2. Migration at scale

* Parallelize per SAS file
* Run across thousands of scripts

### 3. Certification layer (next step)

* Attach confidence score
* Produce audit logs

---

## If you want to push this further (high impact options)

I’d recommend one of these next:

### Option A — Production Hardening

* Retry logic
* JSON guards
* Structured outputs (function calling)
* Logging + observability

### Option B — Parallel + Distributed

* Convert to `asyncio` or Ray
* File-level parallel execution

### Option C — DAG Orchestration

* Convert into Airflow / Prefect pipeline
* Add retries, branching, scheduling

### Option D — Enterprise Validation Layer (most valuable)

* Actually run:

  * SAS outputs
  * Python outputs
* Compare datasets statistically

---

## My honest take

You’re now beyond “prototype”—this is the **core of a real product**.

What separates this from a market-ready system is:

* robustness
* observability
* validation depth

---

If you want, I can next:

* Add **AutoFix feedback loop with retry strategy**
* Convert this into a **distributed Ray-based system**
* Or build a **certification + audit report generator (SOX-ready)**

Pick one direction and I’ll take it all the way.

