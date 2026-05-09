## what will Auto-fix agent (patch Python when diff detected) do?

The **Auto-fix Agent** is the component that closes the loop in your system: it doesn’t just *detect* SAS → Python mismatches, it actively **repairs the generated Python code to restore semantic equivalence**.

Think of it as a combination of:

* a **compiler optimizer**
* a **debugger “fix-it” assistant**
* a **unit-test failure resolver**
* and a **targeted GPT-5 patch generator**

---

# 🧠 1. What triggers the Auto-fix Agent

It activates when the **Diff Engine** detects:

* row count mismatches
* aggregation differences
* join mismatches
* filter logic drift
* missing transformations
* lineage inconsistencies

Example trigger:

```json id="tr1"
{
  "step": 2,
  "sas_rows": 420,
  "python_rows": 418,
  "diff": "row_mismatch"
}
```

---

# ⚙️ 2. What the Auto-fix Agent actually does

It performs a **4-stage repair loop**:

---

## 🧩 Stage 1: Diagnose root cause (not symptom)

It analyzes the diff + lineage + AST:

* Did a filter change?
* Did a join key mismatch?
* Was macro expansion incomplete?
* Was grouping logic lost?
* Was a null-handling rule dropped?

---

## 🧩 Stage 2: Localize bug in transformation pipeline

It identifies *where the error was introduced*:

```text id="loc1"
SAS → AST ✔
AST → Macro expansion ✔
Macro → Python translation ❌ HERE
```

---

## 🧩 Stage 3: Generate minimal patch (not full rewrite)

Instead of regenerating the whole file, it produces a **surgical fix**:

* fix filter condition
* fix join keys
* fix aggregation logic
* fix datatype coercion
* fix null handling

---

## 🧩 Stage 4: Validate fix against lineage

It re-runs:

* diff engine
* execution trace comparison
* optional statistical tests

Only then is patch accepted.

---

# 🧠 3. Auto-fix Agent architecture

```text id="arch_fix_01"
Diff Engine
     ↓
Root Cause Analyzer (LLM + rules)
     ↓
Patch Generator (GPT-5)
     ↓
Code Rewriter (AST-based)
     ↓
Re-execution Validator
     ↓
Time-travel Lineage Update
```

---

# ⚙️ 4. Core implementation (Python)

```python id="fix_agent_01"
class AutoFixAgent:
    def __init__(self, diff_engine, llm_router):
        self.diff_engine = diff_engine
        self.llm = llm_router

    def fix(self, sas_trace, py_trace, python_code, ast_context):

        # 1. detect diff
        diff = self.diff_engine.align_traces(sas_trace, py_trace)

        issues = self._extract_issues(diff)

        if not issues:
            return python_code  # already correct

        # 2. root cause analysis
        root_cause = self._analyze_root_cause(issues, ast_context)

        # 3. generate patch via GPT-5
        patch = self._generate_patch(python_code, root_cause)

        # 4. apply patch
        fixed_code = self._apply_patch(python_code, patch)

        return {
            "original": python_code,
            "patched": fixed_code,
            "patch": patch,
            "root_cause": root_cause
        }

    def _extract_issues(self, diff):
        return [d for d in diff if not d["diff"]["semantic_match"]]

    def _analyze_root_cause(self, issues, context):
        prompt = f"""
        Analyze why SAS and Python differ.

        Issues:
        {issues}

        AST Context:
        {context}

        Identify root cause in transformation logic.
        """

        return self.llm.call(
            model="gpt-5",
            system="You are a compiler debugging engine.",
            user=prompt
        )

    def _generate_patch(self, code, root_cause):
        prompt = f"""
        Fix the following Python code so it matches SAS semantics.

        Root Cause:
        {root_cause}

        Code:
        {code}

        Return ONLY a minimal patch (diff-style or corrected block).
        """

        return self.llm.call(
            model="gpt-5",
            system="You are a precision code repair engine.",
            user=prompt
        )

    def _apply_patch(self, code, patch):
        # simplified placeholder (real system would use AST rewriting)
        return patch
```

---

# 🧠 5. What makes this powerful (key insight)

Unlike normal “code regeneration”, this agent:

## ❌ Does NOT:

* rewrite entire Python file
* guess fixes blindly
* ignore lineage context

## ✔ DOES:

* isolates exact transformation failure
* uses SAS as ground truth
* patches minimal logic only
* validates using execution traces

---

# 🔗 6. How it fits your system

```text id="flow_fix_01"
SAS Code
   ↓
CFG Parser
   ↓
Macro AST Engine
   ↓
Python Generator
   ↓
Execution Trace (SAS vs Python)
   ↓
Diff Engine
   ↓
🔴 Auto-Fix Agent
   ↓
Patched Python Code
   ↓
Re-validation (Time-travel lineage update)
```

---

# 🧪 7. Example fix scenario

### SAS:

```sas id="s1"
where amount > 0 and region = 'US'
```

### Python (incorrect):

```python id="p1"
df[df.amount > 0]
```

---

### Diff detects:

* missing filter condition (`region = 'US'`)

---

### Auto-fix output:

```python id="p2"
df[(df.amount > 0) & (df.region == "US")]
```

---

# 🧠 8. Why this is a major upgrade

This turns your system into:

> 🧠 A **self-healing compiler for legacy SAS migration**

You now have:

| Capability    | Description                |
| ------------- | -------------------------- |
| Detection     | find mismatch              |
| Explanation   | why mismatch occurred      |
| Correction    | fix Python automatically   |
| Verification  | confirm correctness        |
| Learning loop | improve future conversions |

---

# 🚀 9. Final system evolution

```text id="final_fix_01"
SAS → CFG Parser → AST
       ↓
Macro + Dependency Engine
       ↓
Python Generator (GPT-5)
       ↓
Diff Engine (SAS vs Python)
       ↓
🔴 Auto-Fix Agent
       ↓
Verified Python Output
       ↓
Time-travel Lineage Update
```

---

# 🔥 If you want next upgrades

I can extend this into:

### ⚙️ 1. Multi-agent debate fixer (3 GPT models vote on best patch)

### 🧠 2. Statistical correction engine (fixes numeric drift automatically)

### 📊 3. Learning system (improves future translations from past fixes)

### 🔐 4. Audit-safe patch history (compliance-grade change logs)

### 💰 5. Cost-aware fix batching (bulk SAS repo correction optimization)

Just tell me—this is now a **self-correcting compiler system for enterprise SAS modernization**, not just a migration pipeline.

