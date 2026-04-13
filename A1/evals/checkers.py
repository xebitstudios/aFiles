"""
Checkers — automated evaluation functions for each scoring dimension.

Each checker takes the SAS input and Python output and returns a DimensionScore.
"""

import ast
import re
import logging

import anthropic

from evals.scoring import Dimension, DimensionScore

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 1. SYNTAX CHECKER — can Python parse the code?
# ---------------------------------------------------------------------------

def check_syntax(python_code: str) -> DimensionScore:
    """Check if the generated Python code is syntactically valid."""
    try:
        ast.parse(python_code)
        return DimensionScore(
            dimension=Dimension.SYNTAX,
            score=1.0,
            details="Code parses successfully.",
        )
    except SyntaxError as e:
        return DimensionScore(
            dimension=Dimension.SYNTAX,
            score=0.0,
            details=f"SyntaxError at line {e.lineno}: {e.msg}",
        )


# ---------------------------------------------------------------------------
# 2. COMPLETENESS CHECKER — are all SAS constructs accounted for?
# ---------------------------------------------------------------------------

def check_completeness(sas_code: str, python_code: str) -> DimensionScore:
    """
    Check that every meaningful SAS construct appears in the Python output
    (as code or as an explicit comment/TODO).

    Uses heuristic keyword matching — not a full semantic check.
    """
    # Extract SAS constructs present in the input
    sas_constructs = _extract_sas_constructs(sas_code)
    if not sas_constructs:
        return DimensionScore(
            dimension=Dimension.COMPLETENESS,
            score=1.0,
            details="No SAS constructs detected to check.",
        )

    python_lower = python_code.lower()
    found = 0
    missing = []

    for construct_name, indicators in sas_constructs.items():
        # Check if any indicator appears in the Python output
        matched = any(ind.lower() in python_lower for ind in indicators)
        if matched:
            found += 1
        else:
            missing.append(construct_name)

    score = found / len(sas_constructs) if sas_constructs else 1.0
    details = ""
    if missing:
        details = f"Missing constructs: {', '.join(missing)}"
    else:
        details = f"All {len(sas_constructs)} constructs accounted for."

    return DimensionScore(
        dimension=Dimension.COMPLETENESS,
        score=score,
        details=details,
        sub_scores={c: (0.0 if c in missing else 1.0) for c in sas_constructs},
    )


def _extract_sas_constructs(sas_code: str) -> dict[str, list[str]]:
    """
    Identify which SAS constructs are present and what Python indicators
    should appear for each.
    """
    constructs: dict[str, list[str]] = {}
    sas_lower = sas_code.lower()

    checks = [
        ("data_step", r"\bdata\s+\w+", ["pd.", "dataframe", "df", "pandas"]),
        ("set_statement", r"\bset\s+\w+", ["read", "pd.", "df", "="]),
        ("merge_statement", r"\bmerge\b", ["merge", "join", "pd.merge"]),
        ("by_statement", r"\bby\b", ["sort_values", "groupby", "by=", "on="]),
        ("where_clause", r"\bwhere\b", ["query", "loc[", "boolean", "filter", "where"]),
        ("if_then", r"\bif\b.*\bthen\b", ["if ", "np.where", "np.select"]),
        ("do_loop", r"\bdo\b", ["for ", "while ", "range("]),
        ("retain", r"\bretain\b", ["retain", "shift", "cumsum", "iterrows", "state"]),
        ("array", r"\barray\b", ["list", "array", "np.array", "[]"]),
        ("proc_sort", r"\bproc\s+sort\b", ["sort_values", "drop_duplicates"]),
        ("proc_means", r"\bproc\s+means\b", ["describe", "agg", "mean", "groupby"]),
        ("proc_freq", r"\bproc\s+freq\b", ["value_counts", "crosstab", "freq"]),
        ("proc_print", r"\bproc\s+print\b", ["print(", "to_string", "head("]),
        ("proc_sql", r"\bproc\s+sql\b", ["sql", "query", "merge", "select"]),
        ("proc_report", r"\bproc\s+report\b", ["report", "style", "tabulate"]),
        ("proc_transpose", r"\bproc\s+transpose\b", ["transpose", "pivot", "melt", ".T"]),
        ("proc_export", r"\bproc\s+export\b", ["to_csv", "to_excel", "to_parquet"]),
        ("proc_import", r"\bproc\s+import\b", ["read_csv", "read_excel", "read_sas"]),
        ("proc_format", r"\bproc\s+format\b", ["dict", "mapping", "format"]),
        ("macro_def", r"%macro\b", ["def "]),
        ("macro_let", r"%let\b", ["="]),
        ("macro_call", r"%\w+\(", ["(", "def "]),
        ("macro_if", r"%if\b", ["if "]),
        ("macro_do", r"%do\b", ["for ", "while ", "range("]),
        ("libname", r"\blibname\b", ["path", "engine", "connect", "Path("]),
        ("filename", r"\bfilename\b", ["path", "open(", "Path("]),
        ("include", r"%include\b", ["import", "exec(", "open("]),
        ("ods", r"\bods\b", ["html", "pdf", "csv", "to_", "ods"]),
        ("options", r"\boptions\b", ["option", "set_option", "logging", "#"]),
        ("title", r"\btitle\b", ["title", "report_title"]),
        ("format_assign", r"\bformat\b", ["format", "strftime", "f'"]),
        ("global", r"%global\b", ["global", "="]),
        ("email", r"\bemail\b", ["smtp", "email", "MIMEText"]),
        ("sql_join", r"\bjoin\b", ["merge", "join", "pd.merge"]),
        ("sql_case", r"\bcase\b.*\bwhen\b", ["np.where", "np.select", "if", "case"]),
        ("sql_union", r"\bunion\b", ["concat", "union"]),
        ("sql_subquery", r"\(select\b", ["query", "merge", "df"]),
        ("output_stmt", r"\boutput\b", ["append", "concat", "loc["]),
        ("drop_keep", r"\b(drop|keep)\b", ["drop", "filter", "columns", "["]),
        ("rename", r"\brename\b", ["rename"]),
        ("label", r"\blabel\b", ["label", "comment", "#"]),
        ("informat", r"\binformat\b", ["informat", "parse", "to_datetime", "astype"]),
    ]

    for name, pattern, indicators in checks:
        if re.search(pattern, sas_lower):
            constructs[name] = indicators

    return constructs


# ---------------------------------------------------------------------------
# 3. CORRECTNESS CHECKER — LLM-as-judge semantic comparison
# ---------------------------------------------------------------------------

def check_correctness(
    sas_code: str,
    python_code: str,
    model: str = "claude-sonnet-4-6",
) -> DimensionScore:
    """
    Use an LLM as a judge to evaluate whether the Python code correctly
    reproduces the SAS logic.
    """
    client = anthropic.Anthropic()

    prompt = f"""\
You are evaluating a SAS-to-Python code conversion. Score the Python code's
correctness on a scale of 0 to 10.

ORIGINAL SAS:
```sas
{sas_code}
```

GENERATED PYTHON:
```python
{python_code}
```

Evaluate these aspects and give a sub-score (0-10) for each:
1. DATA FLOW: Are datasets read, transformed, and written correctly?
2. LOGIC: Do conditionals, loops, and branching match?
3. FUNCTIONS: Are SAS functions mapped to correct Python equivalents?
4. AGGREGATIONS: Do GROUP BY, summary stats, and calculations match?
5. JOINS/MERGES: Are merge/join operations equivalent?
6. VARIABLE HANDLING: Are variable names, types, and missing values correct?
7. OUTPUT: Does the Python produce equivalent output/results?

Respond in this EXACT format (no other text):
DATA_FLOW: <score>
LOGIC: <score>
FUNCTIONS: <score>
AGGREGATIONS: <score>
JOINS: <score>
VARIABLES: <score>
OUTPUT: <score>
OVERALL: <score>
ISSUES: <one-line summary of problems, or "none">
"""

    try:
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            temperature=0.0,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text
        return _parse_correctness_response(raw)
    except Exception as e:
        logger.error("Correctness checker LLM call failed: %s", e)
        return DimensionScore(
            dimension=Dimension.CORRECTNESS,
            score=0.0,
            details=f"LLM evaluation failed: {e}",
        )


def _parse_correctness_response(raw: str) -> DimensionScore:
    """Parse the structured LLM judge response."""
    sub_scores: dict[str, float] = {}
    overall = 0.0
    issues = ""

    for line in raw.strip().splitlines():
        line = line.strip()
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        key = key.strip().lower()
        val = val.strip()

        if key == "issues":
            issues = val
            continue

        try:
            score = float(val) / 10.0  # normalise to 0-1
            score = max(0.0, min(1.0, score))
        except ValueError:
            continue

        if key == "overall":
            overall = score
        else:
            sub_scores[key] = score

    # If no overall was parsed, average the sub-scores
    if overall == 0.0 and sub_scores:
        overall = sum(sub_scores.values()) / len(sub_scores)

    return DimensionScore(
        dimension=Dimension.CORRECTNESS,
        score=overall,
        details=issues if issues else "No issues reported.",
        sub_scores=sub_scores,
    )


# ---------------------------------------------------------------------------
# 4. QUALITY CHECKER — code quality and best practices
# ---------------------------------------------------------------------------

def check_quality(python_code: str, model: str = "claude-sonnet-4-6") -> DimensionScore:
    """
    Use an LLM to evaluate the code quality of the generated Python.
    """
    client = anthropic.Anthropic()

    prompt = f"""\
Rate the following Python code (converted from SAS) on code quality.
Score each aspect 0-10:

```python
{python_code}
```

1. READABILITY: Clear variable names, logical structure, comments
2. IDIOMATIC: Uses pandas/numpy idiomatically (vectorised ops vs loops)
3. IMPORTS: All imports present, no unused imports
4. STRUCTURE: Proper function decomposition, no excessive nesting
5. PEP8: Follows Python style conventions

Respond in this EXACT format (no other text):
READABILITY: <score>
IDIOMATIC: <score>
IMPORTS: <score>
STRUCTURE: <score>
PEP8: <score>
OVERALL: <score>
NOTES: <one-line summary>
"""

    try:
        response = client.messages.create(
            model=model,
            max_tokens=512,
            temperature=0.0,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text
        return _parse_quality_response(raw)
    except Exception as e:
        logger.error("Quality checker LLM call failed: %s", e)
        return DimensionScore(
            dimension=Dimension.QUALITY,
            score=0.0,
            details=f"LLM evaluation failed: {e}",
        )


def _parse_quality_response(raw: str) -> DimensionScore:
    """Parse the structured quality judge response."""
    sub_scores: dict[str, float] = {}
    overall = 0.0
    notes = ""

    for line in raw.strip().splitlines():
        line = line.strip()
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        key = key.strip().lower()
        val = val.strip()

        if key == "notes":
            notes = val
            continue

        try:
            score = float(val) / 10.0
            score = max(0.0, min(1.0, score))
        except ValueError:
            continue

        if key == "overall":
            overall = score
        else:
            sub_scores[key] = score

    if overall == 0.0 and sub_scores:
        overall = sum(sub_scores.values()) / len(sub_scores)

    return DimensionScore(
        dimension=Dimension.QUALITY,
        score=overall,
        details=notes,
        sub_scores=sub_scores,
    )


# ---------------------------------------------------------------------------
# 5. EXECUTABILITY CHECKER — can the code run without crashing?
# ---------------------------------------------------------------------------

def check_executability(python_code: str) -> DimensionScore:
    """
    Check if the generated Python code can be executed without import
    or immediate runtime errors.

    This does a dry-run: compiles the code and checks that all imported
    modules are available. It does NOT execute data operations (no data files).
    """
    sub_scores: dict[str, float] = {}
    issues: list[str] = []

    # Check 1: Compilation
    try:
        compile(python_code, "<eval>", "exec")
        sub_scores["compilation"] = 1.0
    except SyntaxError as e:
        sub_scores["compilation"] = 0.0
        issues.append(f"Compilation failed: {e.msg} (line {e.lineno})")

    # Check 2: Import availability
    import_lines = re.findall(
        r"^(?:import|from)\s+([\w.]+)", python_code, re.MULTILINE
    )
    importable = 0
    total_imports = len(import_lines)

    for module_name in import_lines:
        top_level = module_name.split(".")[0]
        try:
            __import__(top_level)
            importable += 1
        except ImportError:
            issues.append(f"Module not installed: {top_level}")

    if total_imports > 0:
        sub_scores["imports_available"] = importable / total_imports
    else:
        sub_scores["imports_available"] = 1.0

    # Check 3: No obvious runtime traps
    traps = [
        (r"\bexec\(", "Uses exec() — potential runtime risk"),
        (r"\beval\(", "Uses eval() — potential runtime risk"),
        (r"open\(.+\)\.read\(\)", "Reads file inline — may fail if file missing"),
    ]
    trap_score = 1.0
    for pattern, msg in traps:
        if re.search(pattern, python_code):
            trap_score -= 0.15
            issues.append(msg)
    sub_scores["no_runtime_traps"] = max(0.0, trap_score)

    # Overall
    overall = sum(sub_scores.values()) / len(sub_scores) if sub_scores else 0.0

    return DimensionScore(
        dimension=Dimension.EXECUTABILITY,
        score=overall,
        details="; ".join(issues) if issues else "No executability issues.",
        sub_scores=sub_scores,
    )
