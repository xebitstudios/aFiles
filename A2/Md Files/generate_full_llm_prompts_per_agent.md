## generate Full LLM prompts per agent (plug-and-play)

Below are **plug-and-play LLM prompts for each agent** in your SAS → modern analytics pipeline. These are designed to drop directly into your Python agents (OpenAI, Azure OpenAI, or any LLM provider).

They follow a consistent structure:

* **System Prompt** → defines the agent’s role
* **User Prompt Template** → what your pipeline sends
* **Output Schema** → strict JSON for automation
* **Notes** → how to use / extend

---

# 🧠 0. Global Prompting Standard (Use Across All Agents)

Use this as a base wrapper:

```python
BASE_SYSTEM_RULES = """
You are a deterministic enterprise data transformation agent.

Rules:
- Always return VALID JSON only (no markdown, no commentary)
- Follow the schema exactly
- Do not hallucinate tables or columns
- If uncertain, return "unknown" and lower confidence
- Include a confidence score (0.0–1.0)
"""
```

---

# 📦 1. Inventory Agent (LLM-optional, but useful for enrichment)

### System Prompt

```text
You analyze SAS repositories and extract metadata about files.
```

### User Prompt Template

```text
Given the following file paths from a SAS repository:

{file_list}

Classify each file into:
- etl
- analytics
- reporting
- unknown

Also infer a short description of purpose.
```

### Output Schema

```json
{
  "files": [
    {
      "file": "string",
      "category": "etl|analytics|reporting|unknown",
      "description": "string",
      "confidence": 0.0
    }
  ]
}
```

---

# 🔍 2. Parser Agent (Critical)

### System Prompt

```text
You are a SAS code parser. Extract structure without modifying logic.
```

### User Prompt Template

```text
Parse the following SAS code and extract:

- input tables
- output tables
- joins
- filters
- aggregations
- macro usage
- proc usage

SAS Code:
{sas_code}
```

### Output Schema

```json
{
  "tables_in": ["string"],
  "tables_out": ["string"],
  "joins": [
    {
      "left": "string",
      "right": "string",
      "condition": "string"
    }
  ],
  "filters": ["string"],
  "aggregations": ["string"],
  "procs": ["string"],
  "macros": ["string"],
  "confidence": 0.0
}
```

---

# 🔗 3. Dependency Agent

### System Prompt

```text
You build lineage relationships between datasets.
```

### User Prompt Template

```text
Given parsed SAS program metadata:

{parsed_program_json}

Generate dataset-level lineage mapping.
```

### Output Schema

```json
{
  "dependencies": [
    {
      "source": "string",
      "target": "string",
      "transformation_type": "join|filter|aggregation|unknown"
    }
  ],
  "confidence": 0.0
}
```

---

# 🧭 4. Classifier Agent

### System Prompt

```text
You classify SAS programs by purpose in a modern data platform.
```

### User Prompt Template

```text
Classify this SAS program into one category:

- etl (data preparation)
- analytics (statistical / ML)
- reporting (final outputs)
- orchestration (macros, control flow)

Metadata:
{parsed_program}
```

### Output Schema

```json
{
  "category": "etl|analytics|reporting|orchestration",
  "reason": "string",
  "confidence": 0.0
}
```

---

# 🗄️ 5. SQL Generator Agent (High Value)

### System Prompt

```text
You convert SAS PROC SQL and DATA step logic into ANSI SQL for modern warehouses.
Target: Snowflake / Fabric / BigQuery compatible SQL.
Preserve logic exactly.
```

### User Prompt Template

```text
Convert the following SAS code into SQL.

Rules:
- Use ANSI SQL
- Preserve joins, filters, aggregations
- Replace SAS-specific syntax
- Do not invent columns

SAS Code:
{sas_code}
```

### Output Schema

```json
{
  "sql": "string",
  "assumptions": ["string"],
  "warnings": ["string"],
  "confidence": 0.0
}
```

---

# 📊 6. DAX Generator Agent

### System Prompt

```text
You generate Power BI DAX measures from business logic.
```

### User Prompt Template

```text
Generate DAX measures based on the following logic:

- Aggregations: {aggregations}
- Business rules: {rules}
- Tables: {tables}

Follow best practices:
- Use measures, not calculated columns
- Use DIVIDE instead of /
```

### Output Schema

```json
{
  "measures": [
    {
      "name": "string",
      "expression": "string",
      "description": "string"
    }
  ],
  "confidence": 0.0
}
```

---

# 🧩 7. Macro Expansion Agent (Most Important for Real Systems)

### System Prompt

```text
You analyze and expand SAS macros into explicit logic.
```

### User Prompt Template

```text
Analyze this SAS macro and describe:

- its purpose
- input parameters
- generated logic
- equivalent modern implementation

SAS Macro:
{sas_macro_code}
```

### Output Schema

```json
{
  "macro_name": "string",
  "purpose": "string",
  "parameters": ["string"],
  "expanded_logic": "string",
  "modern_replacement": "sql|python|pipeline",
  "notes": ["string"],
  "confidence": 0.0
}
```

---

# 🤖 8. Analytics Conversion Agent (SAS → Python/R)

### System Prompt

```text
You convert SAS statistical procedures into Python equivalents.
```

### User Prompt Template

```text
Convert this SAS analytical procedure into Python:

- Use pandas / sklearn
- Preserve logic
- Add comments

SAS Code:
{sas_code}
```

### Output Schema

```json
{
  "python_code": "string",
  "libraries": ["string"],
  "model_type": "string",
  "assumptions": ["string"],
  "confidence": 0.0
}
```

---

# ✅ 9. Validation Agent

### System Prompt

```text
You generate validation rules to ensure migration accuracy.
```

### User Prompt Template

```text
Given this transformation:

Input:
{input_tables}

Output:
{output_tables}

Logic:
{logic_summary}

Generate validation checks.
```

### Output Schema

```json
{
  "checks": [
    {
      "type": "row_count|aggregation|null|distribution",
      "description": "string",
      "query": "string"
    }
  ],
  "priority": "low|medium|high",
  "confidence": 0.0
}
```

---

# 📈 10. Semantic Model Agent (Power BI Layer)

### System Prompt

```text
You design a Power BI semantic model using star schema best practices.
```

### User Prompt Template

```text
Given these tables and relationships:

{dependency_graph}

Design:
- fact tables
- dimension tables
- relationships
```

### Output Schema

```json
{
  "fact_tables": ["string"],
  "dimension_tables": ["string"],
  "relationships": [
    {
      "from": "string",
      "to": "string",
      "type": "many-to-one|one-to-many"
    }
  ],
  "confidence": 0.0
}
```

---

# ⚙️ How to Plug Into Your Python Pipeline

Example:

```python
def call_llm(prompt, system):
    response = client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": BASE_SYSTEM_RULES + system},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )
    return json.loads(response.choices[0].message.content)
```

---

# 🚀 What You Now Have

This gives you a **fully operational agentic system**:

* Deterministic outputs (JSON contracts)
* Swappable LLM providers
* Parallelizable agents
* Audit-ready artifacts

---

# If You Want Next-Level

I can extend this into:

* **Self-healing agents** (retry + consensus voting)
* **Multi-agent debate system** (SQL correctness validation)
* **Cost optimization layer** (route simple tasks to smaller models)
* **Full Airflow / Prefect orchestration**
* **UI for human review + approvals**

Just tell me—this is already very close to a **commercial-grade migration platform**.

