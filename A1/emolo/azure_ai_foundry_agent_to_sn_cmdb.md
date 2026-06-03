Q: how can my Azure AI Foundry agent get information details about an application from ServiceNow CMDB?
--
An **Azure AI Foundry agent** can retrieve application information from **[ServiceNow](https://www.servicenow.com?utm_source=chatgpt.com)** CMDB by treating ServiceNow as a tool-enabled enterprise data source. The architecture you choose depends on your requirements for security, latency, governance, and how much autonomy you want the agent to have.

---

# Recommended Enterprise Architecture

```text
Azure AI Foundry Agent
          |
          v
Tool / Function Calling
          |
          v
API Gateway
          |
          v
ServiceNow CMDB APIs
          |
          v
CMDB Tables
  - cmdb_ci_appl
  - cmdb_ci_service
  - cmdb_rel_ci
  - cmdb_ci_server
```

The agent does **not** directly query the CMDB database. Instead, it calls approved APIs that return only the data it is authorized to access.

---

# What Information Can Be Retrieved?

Typical application metadata stored in CMDB includes:

| Information       | CMDB Source         |
| ----------------- | ------------------- |
| Application Name  | Application CI      |
| Business Owner    | Application CI      |
| Technical Owner   | Application CI      |
| Support Group     | Application CI      |
| Environment       | Application CI      |
| Criticality       | Application CI      |
| Servers           | Related CIs         |
| Databases         | Related CIs         |
| Interfaces        | Relationships       |
| Dependencies      | Relationship Tables |
| Business Services | Service Mapping     |
| Cloud Resources   | Related CIs         |

Example:

```json
{
  "application": "Claims Processing",
  "businessOwner": "Operations",
  "technicalOwner": "Platform Team",
  "criticality": "Tier 1",
  "environment": "Production",
  "servers": 42,
  "databases": 3
}
```

---

# Option 1: ServiceNow REST API (Most Common)

ServiceNow exposes REST APIs.

Example endpoint:

```text
/api/now/table/cmdb_ci_appl
```

Search by application name:

```http
GET /api/now/table/cmdb_ci_appl
?sysparm_query=name=Claims Processing
```

Agent flow:

```text
User
  ↓
Agent
  ↓
Tool Call
  ↓
ServiceNow REST API
  ↓
CMDB Result
  ↓
Agent Response
```

---

# Option 2: Azure Function as a CMDB Tool

This is usually the preferred enterprise pattern.

```text
Azure AI Foundry Agent
          ↓
Azure Function
          ↓
ServiceNow API
          ↓
CMDB
```

Benefits:

* Secrets remain hidden
* RBAC enforcement
* Audit logging
* Result normalization
* Data filtering

Example tool:

```python
get_application_details(app_name)
```

Agent invocation:

```text
"Tell me about the Claims Processing application."
```

Tool call:

```json
{
  "app_name": "Claims Processing"
}
```

---

# Option 3: Build a CMDB Knowledge Index

For large-scale enterprise use cases, periodically synchronize CMDB data into:

* Azure AI Search
* Azure Data Explorer
* Azure SQL
* Knowledge Graph

Architecture:

```text
ServiceNow
     ↓
ETL Pipeline
     ↓
Azure AI Search
     ↓
AI Foundry Agent
```

Benefits:

* Faster retrieval
* Semantic search
* Reduced ServiceNow load
* Better RAG performance

This is often the best approach when users ask questions such as:

* "Which applications depend on Oracle?"
* "Which systems are Tier 1?"
* "What applications are owned by Finance?"

---

# Option 4: Create a CMDB Knowledge Graph

For modernization and architecture analysis programs, create a graph model.

```text
Application
     |
     +---- Server
     |
     +---- Database
     |
     +---- API
     |
     +---- Business Service
```

Store in:

* [Azure Cosmos DB](https://azure.microsoft.com/products/cosmos-db/?utm_source=chatgpt.com) (Gremlin API)
* [Neo4j](https://neo4j.com/?utm_source=chatgpt.com)
* Graph databases

Then the agent can answer:

> "Show all downstream dependencies of Claims Processing."

> "What breaks if Oracle PROD is unavailable?"

> "Which applications are connected to SAP?"

These questions are difficult to answer efficiently using standard CMDB table queries.

---

# ServiceNow Tables Most Useful for Agents

| Table                  | Purpose           |
| ---------------------- | ----------------- |
| cmdb_ci_appl           | Applications      |
| cmdb_ci_service        | Business Services |
| cmdb_ci_server         | Servers           |
| cmdb_ci_database       | Databases         |
| cmdb_rel_ci            | Relationships     |
| cmdb_ci_cloud_resource | Cloud Assets      |
| cmdb_ci_endpoint       | APIs              |
| sys_user_group         | Support Teams     |

---

# Example Agent Tools

### Get Application

```python
get_application(app_name)
```

Returns:

```json
{
  "name": "Claims Processing",
  "owner": "Operations",
  "criticality": "Tier 1"
}
```

---

### Get Dependencies

```python
get_application_dependencies(app_name)
```

Returns:

```json
{
  "databases": [
    "Oracle Claims"
  ],
  "services": [
    "Customer API"
  ],
  "servers": [
    "app-prod-01"
  ]
}
```

---

### Get Application Health Context

```python
get_application_context(app_name)
```

Combines:

* CMDB
* Monitoring
* Incident data

Sources may include:

* [Dynatrace](https://www.dynatrace.com/?utm_source=chatgpt.com)
* [Azure Monitor](https://azure.microsoft.com/products/monitor/?utm_source=chatgpt.com)
* ServiceNow

Result:

```json
{
  "application": "Claims Processing",
  "criticality": "Tier 1",
  "openIncidents": 3,
  "availability": "99.98%",
  "dependencies": 14
}
```

---

# Ideal Architecture for Your AI-Driven Modernization Platform

Since you've been working on AI-assisted application discovery and modernization, a strong pattern is:

```text
ServiceNow CMDB
        |
        v
CMDB Extraction Agent
        |
        v
Knowledge Graph
        |
        +---- Dependency Agent
        |
        +---- Architecture Agent
        |
        +---- Migration Agent
        |
        +---- Risk Analysis Agent
        |
        v
Azure AI Foundry
```

The CMDB becomes the authoritative source for:

* Application inventory
* Ownership
* Dependencies
* Infrastructure mappings
* Business criticality

and your Foundry agents can use that information to generate architecture blueprints, dependency maps, modernization assessments, migration waves, and operational risk analyses automatically.
