Alright—this is a perfect use case for turning your consulting workflow into a **repeatable, semi-automated system**.

Below is a **working Python generator** that:

* Takes structured **discovery input (JSON)**
* Produces:

  * SOW
  * Architecture Doc
  * Assessment Report
  * Proposal
  * ROI Model
* Outputs them as **Markdown files** (easy to convert to Word/PDF later)

---

# 🧠 Design Approach

* Keep inputs structured → `discovery.json`
* Use **templated generation (Jinja-style via f-strings)**
* Modular generators per document
* Easy to plug into LLM later if needed

---

# 📁 Project Structure

```id="k8z4pl"
consulting_doc_generator/
│
├── generator.py
├── discovery_sample.json
└── outputs/
```

---

# 📥 1. Sample Discovery Input (`discovery_sample.json`)

```json
{
  "client_name": "Acme Retail Corp",
  "industry": "E-commerce",
  "incident_per_month": 60,
  "mttr_hours": 4.5,
  "downtime_cost_per_hour": 5000,
  "annual_ops_cost": 1200000,
  "pain_points": [
    "Manual incident triage",
    "High MTTR",
    "No AI automation"
  ],
  "tech_stack": [
    "AWS",
    "Splunk",
    "AppDynamics",
    "Microservices"
  ],
  "objectives": [
    "Reduce MTTR",
    "Automate incident response",
    "Lower operational cost"
  ]
}
```

---

# ⚙️ 2. Python Generator (`generator.py`)

```python
import json
import os
from datetime import datetime

OUTPUT_DIR = "outputs"


def load_input(path="discovery_sample.json"):
    with open(path, "r") as f:
        return json.load(f)


def ensure_output_dir():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)


def save_file(filename, content):
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w") as f:
        f.write(content)
    print(f"Generated: {path}")


# -----------------------------
# SOW GENERATOR
# -----------------------------
def generate_sow(data):
    return f"""
# Statement of Work (SOW)

## Client: {data['client_name']}
## Date: {datetime.today().strftime('%Y-%m-%d')}

## Executive Summary
689 Labs will implement an AI-driven incident intelligence platform to address:
{', '.join(data['pain_points'])}

## Objectives
{chr(10).join([f"- {o}" for o in data['objectives']])}

## Scope
- Discovery & Assessment
- Architecture Design
- AI Agent Development
- Deployment

## Key Metrics
- Current MTTR: {data['mttr_hours']} hrs
- Incidents/month: {data['incident_per_month']}

## Deliverables
- Assessment Report
- Architecture Blueprint
- AI Agent MVP
- Production Deployment

## Estimated Timeline
12 Weeks

## Pricing Estimate
$400k - $600k (depending on scope finalization)
"""


# -----------------------------
# ARCHITECTURE DOC
# -----------------------------
def generate_architecture(data):
    return f"""
# Solution Architecture

## Overview
AI-powered incident analysis platform for {data['client_name']}

## Current Stack
{chr(10).join([f"- {tech}" for tech in data['tech_stack']])}

## Target Architecture

### Layers
1. Ingestion Layer (Splunk, AppDynamics)
2. AI Agent Layer (Triage + RCA)
3. Data Layer (DynamoDB, S3)
4. API Layer (Lambda, API Gateway)

## Key Features
- Automated root cause detection
- Knowledge-based reasoning
- Continuous learning loop

## Scalability
- Serverless architecture
- Event-driven processing
"""


# -----------------------------
# ASSESSMENT REPORT
# -----------------------------
def generate_assessment(data):
    maturity_ai = 1
    maturity_automation = 2

    return f"""
# Current State Assessment

## Client: {data['client_name']}

## Summary
The organization shows low maturity in AI-driven operations.

## Key Metrics
- MTTR: {data['mttr_hours']} hrs
- Incidents/month: {data['incident_per_month']}

## Pain Points
{chr(10).join([f"- {p}" for p in data['pain_points']])}

## Maturity Scores
| Area | Score |
|------|------|
| AI Adoption | {maturity_ai} |
| Automation | {maturity_automation} |

## Risks
- High downtime cost
- Operational inefficiencies
"""


# -----------------------------
# PROPOSAL
# -----------------------------
def generate_proposal(data):
    return f"""
# Solution Proposal

## Vision
AI-powered autonomous operations platform

## Proposed Solution
- Incident triage agents
- Root cause analysis automation
- Knowledge integration

## Expected Outcomes
- MTTR reduction from {data['mttr_hours']} → ~1.5 hrs
- Incident reduction by ~40%

## Implementation Phases
1. Foundation
2. Agent Deployment
3. Scaling
"""


# -----------------------------
# ROI MODEL
# -----------------------------
def generate_roi(data):
    current_downtime_cost = (
        data["incident_per_month"]
        * data["mttr_hours"]
        * data["downtime_cost_per_hour"]
        * 12
    )

    reduced_mttr = 1.5
    reduced_incidents = int(data["incident_per_month"] * 0.6)

    new_cost = (
        reduced_incidents
        * reduced_mttr
        * data["downtime_cost_per_hour"]
        * 12
    )

    savings = current_downtime_cost - new_cost
    investment = 500000

    roi = (savings - investment) / investment * 100

    return f"""
# ROI Analysis

## Current Annual Downtime Cost
${current_downtime_cost:,.0f}

## Projected Cost After Solution
${new_cost:,.0f}

## Annual Savings
${savings:,.0f}

## Investment
${investment:,.0f}

## ROI
{roi:.2f}%
"""


# -----------------------------
# MAIN PIPELINE
# -----------------------------
def run():
    ensure_output_dir()
    data = load_input()

    save_file("SOW.md", generate_sow(data))
    save_file("Architecture.md", generate_architecture(data))
    save_file("Assessment.md", generate_assessment(data))
    save_file("Proposal.md", generate_proposal(data))
    save_file("ROI.md", generate_roi(data))


if __name__ == "__main__":
    run()
```

---

# ▶️ 3. How to Run

```bash
python generator.py
```

Output:

```id="b0r7xm"
outputs/
├── SOW.md
├── Architecture.md
├── Assessment.md
├── Proposal.md
└── ROI.md
```

---

# 🔥 What You Now Have

This is already powerful, but more importantly:

### ✅ You can:

* Reuse for every client
* Customize inputs → generate full proposal in seconds
* Plug into UI / internal tool

---

# 🚀 High-Impact Next Steps (Worth Doing)

If you want to turn this into a **serious competitive advantage**, I can help you extend it into:

### 1. LLM-Enhanced Version

* Auto-expand sections with GPT
* Generate richer narratives

### 2. Docx / PPT Export

* Client-ready deliverables (not markdown)

### 3. Agent-Based Generator (fits your earlier work)

* One agent per document:

  * SOW Agent
  * Architecture Agent
  * ROI Agent

### 4. Web App (Internal Tool)

* Upload discovery → download full proposal pack

---

If you want, I can next:
👉 Convert this into a **multi-agent system with prompts (aligned to your SAS/agentic architecture work)**
👉 Or generate **actual .docx / PowerPoint outputs automatically**

Just tell me which direction.
