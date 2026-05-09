## classification agent

The **agent responsible for generating SAS program classification is the *Classification Agent***.

---

# 🧭 Classification Agent (Core Responsibility)

### 🎯 What it does

It determines the **business purpose of each SAS program**.

In your workflow, it answers:

> “What kind of program is this in a modern data architecture?”

---

# 🧠 Input

It typically consumes:

* Parsed SAS metadata from the **Parser Agent**
* Sometimes raw code snippets for context

Example input:

```json
{
  "file": "etl/join_sales_customers.sas",
  "has_proc_sql": true,
  "tables_in": ["stg_sales", "stg_customers"],
  "tables_out": ["fct_sales"]
}
```

---

# 📤 Output (Classification Artifact)

It generates:

```json
classification.json
```

Example output:

```json
[
  {
    "file": "etl/load_sales.sas",
    "category": "etl",
    "confidence": 0.96
  },
  {
    "file": "analytics/customer_segmentation.sas",
    "category": "analytics",
    "confidence": 0.91
  },
  {
    "file": "reports/monthly_sales_report.sas",
    "category": "reporting",
    "confidence": 0.98
  }
]
```

---

# 🧩 Categories it produces

Typically:

* **ETL** → data prep, cleansing, joins
* **Analytics** → modeling, clustering, forecasting
* **Reporting** → KPI tables, summaries, dashboards
* **Orchestration** → macros, workflow control logic

---

# 🧠 Where it sits in the pipeline

```text
Parser Agent
      ↓
Classification Agent   ← YOU ARE HERE
      ↓
Transformation Agents (SQL / DAX / Python)
```

---

# ⚠️ Important design note

In your LLM-enhanced version:

* This agent should use **gpt-5-nano or gpt-5-mini**
* Not full GPT-5 (classification is lightweight but high-volume)
* It is a **routing-critical agent**, because it determines downstream processing:

### Example routing logic it enables:

* ETL → SQL Generator Agent
* Analytics → Python Conversion Agent
* Reporting → DAX Generator Agent

---

# 🚀 In short

> The **Classification Agent is the “traffic controller” of your entire SAS migration pipeline**, deciding how every program flows through the system.

---

If you want, I can next:

* upgrade it into a **multi-label classifier (ETL + analytics hybrid detection)**
* or turn it into a **self-learning classifier that improves from human review feedback**
