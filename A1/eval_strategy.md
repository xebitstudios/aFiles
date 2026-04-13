# SAS-to-Python Migration — Evaluation Strategy

This document defines the evaluation framework used to measure and improve the performance of each AI agent in the SAS-to-Python conversion workflow. It covers what we measure, how we measure it, the test case design, the scoring model, and how to interpret and act on results.

---

## Table of Contents

1. [Why Evaluate](#1-why-evaluate)
2. [Evaluation Dimensions](#2-evaluation-dimensions)
3. [Scoring Model](#3-scoring-model)
4. [Test Case Design](#4-test-case-design)
5. [Per-Agent Evaluation Strategy](#5-per-agent-evaluation-strategy)
6. [End-to-End Evaluation](#6-end-to-end-evaluation)
7. [Eval Implementation Architecture](#7-eval-implementation-architecture)
8. [Running Evals](#8-running-evals)
9. [Interpreting Results](#9-interpreting-results)
10. [Continuous Improvement Loop](#10-continuous-improvement-loop)
11. [Known Limitations](#11-known-limitations)

---

## 1. Why Evaluate

The workflow uses 10 AI agents making LLM calls to convert SAS code. Without systematic evaluation we cannot answer:

- **Is the converted Python code correct?** — Does it reproduce the SAS logic faithfully?
- **Is anything being dropped?** — Are all SAS constructs accounted for?
- **Which agents are weak?** — Where should we invest in prompt engineering or model upgrades?
- **Are we regressing?** — Does a prompt change improve one area while breaking another?
- **Is the system production-ready?** — What's the overall quality bar?

Evals give us a quantitative, repeatable, and automated way to answer these questions.

---

## 2. Evaluation Dimensions

Every conversion (both per-agent and end-to-end) is scored on **five dimensions**:

### 2.1 Syntax (Weight: 15%)

> Does the generated Python code parse without errors?

**Method:** Automated — `ast.parse()` on the generated code.

**Scoring:** Binary — 1.0 if it parses, 0.0 if it has a `SyntaxError`.

**Why 15%:** Syntax is necessary but not sufficient. A syntactically valid program can be completely wrong. This is table stakes.

### 2.2 Completeness (Weight: 20%)

> Are all SAS constructs from the input accounted for in the output?

**Method:** Automated heuristic — extract SAS constructs from the input (DATA steps, PROCs, macros, IF/THEN, MERGE, etc.) and check that corresponding Python indicators appear in the output. A construct can be "accounted for" as either converted code or an explicit TODO comment.

**Scoring:** 0.0 – 1.0 proportional to the fraction of constructs matched. Each construct is also tracked as a sub-score for granular analysis.

**Example:**
- SAS input has: DATA step, PROC SORT, %LET, MERGE → 4 constructs
- Python output has indicators for: DATA step, PROC SORT, %LET → 3 found
- Completeness score: 3/4 = 0.75

**Why 20%:** A conversion that silently drops a MERGE or a WHERE clause is dangerous — the output looks right but produces wrong results.

### 2.3 Correctness (Weight: 35%)

> Does the Python logic faithfully reproduce the SAS logic?

**Method:** LLM-as-judge — send both the original SAS and generated Python to Claude with a structured rubric. The judge scores seven sub-dimensions:

| Sub-dimension | What it checks |
|---|---|
| Data Flow | Datasets read, transformed, and written correctly |
| Logic | Conditionals, loops, branching match the SAS |
| Functions | SAS functions mapped to correct Python equivalents |
| Aggregations | GROUP BY, summary stats, calculations match |
| Joins/Merges | Merge/join operations are equivalent |
| Variables | Names, types, missing value handling correct |
| Output | Python produces equivalent results |

**Scoring:** Each sub-dimension is scored 0-10 by the LLM, normalised to 0-1. The overall correctness score is the mean of all sub-dimensions.

**Why 35%:** This is the most important dimension. A syntactically valid, complete, beautifully written program that calculates the wrong answer is a failure.

### 2.4 Quality (Weight: 10%)

> Is the generated Python idiomatic, readable, and well-structured?

**Method:** LLM-as-judge — evaluate readability, idiomatic pandas usage, import completeness, structure, and PEP 8 adherence.

**Scoring:** Five sub-dimensions (readability, idiomatic, imports, structure, PEP8), each 0-10 normalised to 0-1.

**Why 10%:** Quality matters for maintainability, but a correct-but-ugly conversion is better than an elegant-but-wrong one. This dimension rewards agents that produce code humans can understand and maintain.

### 2.5 Executability (Weight: 20%)

> Can the code actually run without crashing?

**Method:** Automated three-part check:
1. **Compilation** — `compile()` succeeds
2. **Import availability** — all imported modules are installed
3. **Runtime traps** — no dangerous patterns like `exec()`, `eval()`, or inline file reads that will fail without data

**Scoring:** Average of the three sub-checks.

**Why 20%:** A program that can't run is useless, even if it's syntactically valid and logically correct on paper.

---

## 3. Scoring Model

### Weighted Overall Score

```
overall = (0.15 × syntax) + (0.20 × completeness) + (0.35 × correctness)
        + (0.10 × quality) + (0.20 × executability)
```

### Pass/Fail Threshold

| Level | Threshold | Meaning |
|-------|-----------|---------|
| **PASS** | ≥ 0.70 | Conversion is usable with minor manual review |
| **MARGINAL** | 0.50 – 0.69 | Conversion needs significant manual review |
| **FAIL** | < 0.50 | Conversion is unreliable; agent needs improvement |

### System-Level Metric

The **system average** is the mean of all individual test case overall scores across all agents. The CI pipeline should fail if the system average drops below 0.50.

---

## 4. Test Case Design

### 4.1 Test Case Structure

Each test case is a Python dict:

```python
{
    "id": "ds_001_simple_set",       # Unique, descriptive ID
    "agent": "data_step",             # Target agent
    "category": "data_step",          # SAS construct category
    "difficulty": "easy",             # easy / medium / hard
    "description": "Simple DATA...",  # What this tests
    "sas_input": "data work.x; ...", # The SAS source code
}
```

### 4.2 Difficulty Tiers

| Tier | Description | Example |
|------|-------------|---------|
| **Easy** | Single construct, no nesting, no dependencies | `%LET x = 5;` |
| **Medium** | Multiple constructs, some nesting, basic dependencies | DATA step with MERGE + BY + IF/THEN |
| **Hard** | Complex nesting, cross-block dependencies, edge cases | Nested macros generating dynamic PROC SQL with ODS |

### 4.3 Coverage Matrix

Test cases are designed to cover every agent × construct combination:

| Agent | # Easy | # Medium | # Hard | Total |
|-------|-------:|--------:|------:|------:|
| Data Step | 1 | 2 | 2 | 5 |
| Proc Step | 1 | 2 | 2 | 5 |
| Macro | 1 | 1 | 2 | 4 |
| SQL | 1 | 2 | 1 | 4 |
| IO | 2 | 1 | 1 | 4 (+ 1 easy) |
| Config | 2 | 1 | 0 | 3 |
| Parser | 1 | 0 | 1 | 2 |
| End-to-End | 0 | 1 | 1 | 2 |

**Total: 30 test cases** in the initial suite.

### 4.4 Adding New Test Cases

When you encounter a SAS construct that an agent handles poorly:

1. Isolate the minimal SAS snippet that triggers the failure
2. Add it to the appropriate list in `evals/test_cases/test_cases.py`
3. Run the eval for that agent: `python run_evals.py --agent <name>`
4. If the score is low, improve the agent's system prompt
5. Re-run to confirm the fix doesn't regress other cases

---

## 5. Per-Agent Evaluation Strategy

### 5.1 Parser Agent

The parser is evaluated differently — it doesn't produce Python code.

**What we measure:**

| Metric | Method |
|--------|--------|
| Block count accuracy | Compare expected vs. actual block count |
| Block type accuracy | Compare expected vs. actual ordered block types |
| Analysis quality | Did the LLM return valid analysis for every block? |

**Why it matters:** If the parser mis-classifies a block, it gets routed to the wrong conversion agent. A PROC SQL block sent to the Data Step Agent will produce garbage.

### 5.2 Data Step Agent

**Focus areas:**
- SET/MERGE/BY logic → correct pd.merge() calls
- IF/THEN/ELSE → correct conditional logic
- First./Last. → correct groupby + shift/transform patterns
- RETAIN → correct state accumulation
- ARRAY + DO loop → correct vectorised or iterative equivalent
- Multiple OUTPUT datasets → correct conditional routing

**High-risk edge cases:**
- Implicit RETAIN on variables created in the DATA step
- First./Last. with multiple BY variables
- Missing value (.) handling in comparisons

### 5.3 Proc Step Agent

**Focus areas:**
- Correct library mapping (PROC MEANS → pandas agg, PROC REG → statsmodels)
- BY/CLASS/VAR/WHERE option translation
- OUTPUT dataset creation
- Statistical option flags (NODUPKEY, NOPRINT, etc.)

**High-risk edge cases:**
- PROC REPORT with COMPUTE blocks
- PROC TABULATE with complex row/column structures
- Statistical PROCs with model output tables

### 5.4 Macro Agent

**Focus areas:**
- Macro parameters (positional + keyword with defaults)
- %IF/%THEN/%ELSE → Python conditionals
- %DO loops → Python loops
- Macro variable references (&var) → f-strings or variables
- No unnecessary exec()/eval()

**High-risk edge cases:**
- Macros that generate SAS code dynamically (truly need exec())
- Nested macro calls
- %SYSFUNC with complex SAS functions

### 5.5 SQL Agent

**Focus areas:**
- JOIN types (LEFT/RIGHT/INNER/FULL)
- CALCULATED keyword handling
- SELECT INTO :macro_var
- Subqueries → intermediate DataFrames
- CASE WHEN → np.where/np.select

**High-risk edge cases:**
- Correlated subqueries
- CONNECT TO pass-through SQL
- UNION with different column sets

### 5.6 IO Agent

**Focus areas:**
- LIBNAME file path → Path()
- LIBNAME database → sqlalchemy engine
- ODS destination → correct output method
- FILENAME EMAIL → smtplib setup
- %INCLUDE → import or exec

**High-risk edge cases:**
- Database-specific LIBNAME options (Oracle, Teradata)
- ODS with nested PROC output
- Email with MIME attachments

### 5.7 Config Agent

**Focus areas:**
- OPTIONS → Python equivalents or meaningful comments
- PROC FORMAT VALUE → Python dict
- PROC FORMAT with ranges → Python function
- TITLE/FOOTNOTE → report variables

**High-risk edge cases:**
- PROC FORMAT PICTURE statement
- INVALUE (reverse mapping)
- Nested format references

---

## 6. End-to-End Evaluation

End-to-end evals test the **full pipeline** — from reading a `.sas` file to writing a `.py` file.

### What we test beyond individual agents:

| Concern | What can go wrong |
|---------|-------------------|
| **Block routing** | Parser sends a block to the wrong agent |
| **Context propagation** | A macro variable defined in block 1 isn't available in block 5 |
| **Cross-block naming** | Dataset named `work.clean` in block 2 but referenced as `clean` in block 4 |
| **Import assembly** | Duplicate imports, missing imports after merge |
| **Execution order** | Blocks reordered incorrectly during assembly |
| **Validator fixes** | Validator "fix" introduces new errors |

### E2E test cases use complete SAS programs that exercise:

1. **Basic ETL** — LIBNAME, %LET, DATA step, PROC SORT, PROC MEANS, PROC EXPORT, PROC PRINT, TITLE
2. **Macro-driven reporting** — OPTIONS, %GLOBAL, PROC FORMAT, %MACRO with PROC SQL + PROC PRINT, ODS PDF, multiple macro calls

---

## 7. Eval Implementation Architecture

### File Structure

```
evals/
├── __init__.py
├── scoring.py              # Dimension, DimensionScore, EvalResult, AgentEvalSummary
├── checkers.py             # 5 checker functions (syntax, completeness, correctness, quality, executability)
├── base_eval.py            # BaseEval class — shared evaluate() flow
├── e2e_eval.py             # EndToEndEval — full pipeline evaluation
├── reporter.py             # Console, JSON, and Markdown report generators
├── agents/
│   ├── __init__.py
│   ├── eval_data_step.py   # DataStepEval
│   ├── eval_proc_step.py   # ProcStepEval
│   ├── eval_macro.py       # MacroEval
│   ├── eval_sql.py         # SQLEval
│   ├── eval_io.py          # IOEval
│   ├── eval_config.py      # ConfigEval
│   └── eval_parser.py      # ParserEval (custom scoring)
├── test_cases/
│   └── test_cases.py       # All 30 test cases organised by agent
└── results/                # Generated reports (JSON + Markdown)

run_evals.py                # CLI entry point for running evals
```

### Data Flow

```
                  ┌──────────────────┐
                  │   run_evals.py   │  ← CLI flags: --agent, --fast, --e2e
                  └────────┬─────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
     ┌──────────────┐ ┌────────┐ ┌──────────┐
     │ Agent Evals  │ │ Parser │ │ E2E Eval │
     │ (per-agent)  │ │ Eval   │ │          │
     └──────┬───────┘ └───┬────┘ └─────┬────┘
            │              │            │
            ▼              ▼            ▼
     ┌──────────────────────────────────────┐
     │         base_eval.evaluate()          │
     │  1. Run agent on SAS input            │
     │  2. check_syntax()                    │
     │  3. check_completeness()              │
     │  4. check_correctness()  [LLM judge]  │
     │  5. check_quality()      [LLM judge]  │
     │  6. check_executability()             │
     │  7. Compute weighted overall score    │
     └──────────────┬───────────────────────┘
                    │
                    ▼
     ┌──────────────────────────────────────┐
     │           reporter.py                 │
     │  • Console table                      │
     │  • JSON file (programmatic analysis)  │
     │  • Markdown report (sharing)          │
     └──────────────────────────────────────┘
```

### LLM Call Budget Per Eval Run

| Component | LLM Calls | Notes |
|-----------|----------:|-------|
| Agent under test | 1 per case | Runs the conversion |
| Correctness checker | 1 per case | LLM-as-judge |
| Quality checker | 1 per case | LLM-as-judge |
| **Total per case** | **3** | |
| **Full suite (30 cases)** | **~90** | With `--fast`: 30 (no judge calls) |
| **E2E (2 cases)** | **~30+** | 2N+3 pipeline calls + 6 judge calls |

Use `--fast` mode during development to skip the LLM judge calls and only run the automated checks (syntax, completeness, executability). Save full eval runs for pre-release validation.

---

## 8. Running Evals

### All agents + end-to-end

```bash
python run_evals.py
```

### Single agent

```bash
python run_evals.py --agent data_step
python run_evals.py --agent macro
python run_evals.py --agent parser
```

### Fast mode (no LLM judge — automated checks only)

```bash
python run_evals.py --fast
```

### Filter by difficulty

```bash
python run_evals.py --difficulty easy        # Only easy cases
python run_evals.py --agent sql --difficulty hard  # Hard SQL cases
```

### End-to-end only

```bash
python run_evals.py --e2e
```

### Verbose logging

```bash
python run_evals.py --verbose
```

### Custom model

```bash
python run_evals.py --model claude-opus-4-6
```

### Output

Every run generates three outputs:

1. **Console table** — immediate visual summary
2. **`evals/results/eval_results_YYYYMMDD_HHMMSS.json`** — full machine-readable results
3. **`evals/results/eval_report_YYYYMMDD_HHMMSS.md`** — formatted Markdown report

### Example Console Output

```
==========================================================================================
  SAS-TO-PYTHON EVALUATION REPORT
  Generated: 2026-04-13 14:30:00
==========================================================================================

Agent              Cases  Pass%  Overall   Syntax Complete  Correct  Quality     Exec
------------------------------------------------------------------------------------------
data_step              5    80%     0.82     1.00     0.85     0.78     0.72     0.88
proc_step              5    80%     0.79     1.00     0.80     0.74     0.70     0.85
macro                  4    75%     0.76     0.95     0.78     0.71     0.68     0.82
sql                    4   100%     0.85     1.00     0.88     0.82     0.75     0.90
io                     5    80%     0.78     1.00     0.82     0.70     0.72     0.80
config                 3   100%     0.88     1.00     0.90     0.85     0.80     0.92
parser                 2   100%     0.90     -        0.90     0.90     0.85     -
orchestrator_e2e       2    50%     0.72     0.95     0.75     0.68     0.65     0.78
------------------------------------------------------------------------------------------
SYSTEM AVERAGE                82%     0.81
==========================================================================================
```

---

## 9. Interpreting Results

### Reading Dimension Scores

| If this is low... | It means... | Action |
|---|---|---|
| **Syntax** < 1.0 | Agent is generating unparseable Python | Fix the agent's output parsing or system prompt instructions about code format |
| **Completeness** < 0.8 | SAS constructs are being silently dropped | Check the completeness sub-scores to find which constructs are missed; add explicit rules to the agent's system prompt |
| **Correctness** < 0.7 | Logic doesn't match the SAS | Read the correctness sub-scores (data_flow, logic, functions, etc.) to pinpoint the category; add examples to the system prompt |
| **Quality** < 0.6 | Code is functional but ugly/non-idiomatic | Add "prefer vectorised pandas operations" and PEP 8 rules to the prompt |
| **Executability** < 0.8 | Code will crash at runtime | Check which imports are missing or which runtime traps were flagged |

### Comparing Agents

If one agent scores significantly lower than others, it's the bottleneck. The end-to-end score will be dragged down by the weakest agent because a single bad block can break the assembled script.

### Regression Detection

Compare JSON reports over time. If a dimension score drops after a prompt change:

1. Identify which test cases regressed (compare `overall_score` per case)
2. Look at the correctness sub-scores to find the specific failure mode
3. Decide whether to revert, adjust, or accept the tradeoff

---

## 10. Continuous Improvement Loop

```
   ┌─────────────────────────────┐
   │  1. Run eval suite          │
   │     python run_evals.py     │
   └─────────────┬───────────────┘
                 │
                 ▼
   ┌─────────────────────────────┐
   │  2. Identify weak spots     │
   │  • Lowest-scoring agent     │
   │  • Lowest dimension         │
   │  • Specific failing cases   │
   └─────────────┬───────────────┘
                 │
                 ▼
   ┌─────────────────────────────┐
   │  3. Root cause analysis     │
   │  • Read the agent output    │
   │  • Compare to SAS input     │
   │  • Check correctness subs   │
   └─────────────┬───────────────┘
                 │
                 ▼
   ┌─────────────────────────────┐
   │  4. Improve                 │
   │  • Update system prompt     │
   │  • Add mapping table entry  │
   │  • Adjust temperature       │
   │  • Try a different model    │
   └─────────────┬───────────────┘
                 │
                 ▼
   ┌─────────────────────────────┐
   │  5. Re-run evals            │
   │  • Confirm improvement      │
   │  • Check for regressions    │
   └─────────────┬───────────────┘
                 │
                 ▼
   ┌─────────────────────────────┐
   │  6. Add edge case           │
   │  • Write new test case      │
   │  • Expand coverage          │
   └─────────────────────────────┘
          │
          └──── back to step 1
```

### Prompt Engineering Workflow

When an agent scores low on correctness:

1. **Read the failing output** — look at the JSON results for the specific test case
2. **Identify the pattern** — is it always the same sub-dimension (e.g., "joins" or "functions")?
3. **Add a targeted rule** — add a specific rule to the agent's system prompt for the failing pattern
4. **Add an example** — if the rule alone doesn't help, add a few-shot example to the prompt
5. **Re-run** — confirm the fix, check for regressions

### Model Comparison

Run the same eval suite with different models to compare:

```bash
python run_evals.py --model claude-sonnet-4-6 --output evals/results/sonnet
python run_evals.py --model claude-opus-4-6 --output evals/results/opus
```

Then compare the JSON outputs to see which model performs better per agent/dimension.

---

## 11. Known Limitations

### What the evals DON'T measure

| Gap | Why | Mitigation |
|-----|-----|------------|
| **Data equivalence** | We don't run both SAS and Python on real data and compare outputs | Future: add data-driven evals with sample datasets |
| **Performance** | We don't measure execution speed of the generated Python | Out of scope — correctness first |
| **Edge case exhaustiveness** | 30 test cases can't cover every SAS program structure | Continuously add cases as failures are discovered |
| **Macro expansion context** | Evals test macros in isolation; in real programs they interact with surrounding code | E2E evals partially cover this |
| **Database connectivity** | LIBNAME database conversions can't be tested without real DB connections | IO evals check code structure, not runtime connectivity |

### LLM-as-judge limitations

- The correctness and quality judges are themselves LLM calls, so they can be wrong
- To mitigate: use low temperature (0.0), structured output format, specific rubric
- For high-stakes validation, supplement with human review of the judge outputs
- The JSON results include the judge's sub-scores and details for human auditing

### Completeness checker limitations

- Uses keyword heuristics, not true semantic analysis
- A false positive (claiming a construct is covered when it's actually wrong) is possible
- The correctness checker (LLM judge) catches cases that the completeness heuristic misses
