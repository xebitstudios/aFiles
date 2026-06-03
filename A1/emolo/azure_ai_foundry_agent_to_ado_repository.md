Q: how can my Azure AI Foundry agent get repository details and files in a ADO project repository?
--
Your **Azure AI Foundry agent** can access **Azure DevOps (ADO) repositories** in several ways, ranging from simple REST API integration to a full enterprise code intelligence platform. For modernization, code analysis, and architecture discovery use cases, I recommend treating ADO as a tool-enabled source rather than letting the LLM directly browse repositories.

---

# Architecture Overview

```text
Azure AI Foundry Agent
          |
          v
Tool / Function Calling
          |
          v
Repository Service
          |
          v
Azure DevOps REST APIs
          |
          v
Git Repository
```

The agent invokes tools that retrieve repository metadata, file contents, commit history, pull requests, pipelines, and branch information.

---

# Option 1: Azure DevOps REST API (Most Common)

Azure DevOps exposes comprehensive REST APIs.

Using:

* Azure DevOps Repos API
* Git API
* Pull Request API
* Pipelines API

Official documentation:

[Azure DevOps REST API Documentation](https://learn.microsoft.com/en-us/rest/api/azure/devops/?utm_source=chatgpt.com)

---

## Get Repositories

Example:

```http
GET https://dev.azure.com/{organization}/{project}/_apis/git/repositories?api-version=7.1
```

Returns:

```json
{
  "id": "repo-id",
  "name": "ClaimsModernization",
  "defaultBranch": "refs/heads/main"
}
```

---

## Get Repository Files

Example:

```http
GET https://dev.azure.com/{organization}/{project}/_apis/git/repositories/{repoId}/items
```

Returns:

```json
{
  "path": "/src/main.py",
  "gitObjectType": "blob"
}
```

---

## Get File Content

Example:

```http
GET https://dev.azure.com/{organization}/{project}/_apis/git/repositories/{repoId}/items?path=/src/main.py
```

Agent tool:

```python
get_file_content(
    repo_name,
    branch,
    file_path
)
```

---

# Option 2: Clone Repository into an Analysis Workspace

This is the preferred approach for modernization programs.

```text
ADO Repository
       |
       v
Git Clone
       |
       v
Analysis Workspace
       |
       +-- Architecture Agent
       +-- Dependency Agent
       +-- Migration Agent
       +-- Documentation Agent
```

Benefits:

* Full repository analysis
* Dependency graph generation
* Code lineage
* Cross-file analysis
* Faster repeated queries

---

# Option 3: Create a Repository Index

For large repositories (millions of lines of code), create a searchable index.

```text
ADO Repo
    |
    v
Indexer
    |
    v
Azure AI Search
    |
    v
Foundry Agent
```

Store:

* File paths
* Source code chunks
* Metadata
* Symbols
* Functions
* Classes
* APIs

Benefits:

* RAG-based code retrieval
* Fast semantic search
* Lower token consumption

---

# Repository Information Your Agent Can Retrieve

## Repository Metadata

```json
{
  "repository": "ClaimsModernization",
  "defaultBranch": "main",
  "size": "4.2 GB",
  "lastCommit": "2026-05-30"
}
```

---

## Branches

Tool:

```python
get_branches(repo)
```

Returns:

```json
[
  "main",
  "develop",
  "feature/api-redesign"
]
```

---

## Commits

Tool:

```python
get_recent_commits(repo)
```

Returns:

```json
[
  {
    "author": "John Smith",
    "message": "Added retry logic",
    "date": "2026-05-29"
  }
]
```

---

## Pull Requests

Tool:

```python
get_open_pull_requests(repo)
```

Useful for:

* Code review analysis
* Release readiness
* Change impact analysis

---

## Pipeline Definitions

Repositories often have:

```text
azure-pipelines.yml
```

Agent can retrieve:

* Build pipelines
* Deployment pipelines
* Test stages
* Release stages

---

# Recommended Tool Set for AI Foundry

## Repository Discovery Tool

```python
discover_repositories(project)
```

Returns:

* Repository list
* Owners
* Languages
* Size

---

## File Retrieval Tool

```python
get_file(
    repo,
    path
)
```

Returns file contents.

---

## Search Tool

```python
search_repository(
    repo,
    query
)
```

Examples:

```text
Find all Oracle connections

Find all REST endpoints

Find all retry configurations
```

---

## Dependency Analysis Tool

```python
analyze_dependencies(repo)
```

Returns:

```json
{
  "databases": [
    "Oracle",
    "Postgres"
  ],
  "queues": [
    "Kafka"
  ],
  "apis": [
    "CustomerService"
  ]
}
```

---

# Modernization Use Case

For your SAS-to-Python or COBOL modernization platform:

```text
ADO Repository
       |
       v
Repository Agent
       |
       +-- File Inventory Agent
       +-- Dependency Agent
       +-- Architecture Agent
       +-- Migration Agent
       +-- Test Generation Agent
       +-- Documentation Agent
```

Artifacts generated automatically:

* Application inventory
* Dependency maps
* Architecture blueprints
* Data lineage
* API catalog
* Technical debt report
* Migration complexity assessment

---

# Authentication Options

Use one of:

### Microsoft Entra ID (Recommended)

```text
Managed Identity
       |
       v
Azure DevOps
```

Benefits:

* No stored secrets
* Enterprise-grade security

---

### Personal Access Token (PAT)

```text
AI Agent
      |
      v
PAT
      |
      v
ADO APIs
```

Good for prototypes, but less desirable for production.

---

### Service Principal

```text
AI Agent
      |
      v
Service Principal
      |
      v
Azure DevOps
```

Common in enterprise deployments.

---

# Enterprise Architecture Recommendation

For a production AI Foundry implementation focused on application discovery and modernization:

```text
Azure AI Foundry Agent
          |
          +----------------+
          |                |
          v                v
ServiceNow Tool      ADO Repository Tool
          |                |
          +----------------+
                   |
                   v
        Knowledge Graph
                   |
                   v
      Architecture Agents
                   |
                   v
      Modernization Agents
```

In this model:

* **ServiceNow CMDB** provides application ownership, criticality, support groups, and infrastructure relationships.
* **Azure DevOps repositories** provide the actual source code, pipelines, and deployment artifacts.
* A **knowledge graph** links CMDB applications to repositories, services, databases, APIs, and cloud resources.

This gives your Azure AI Foundry agents a complete view of the application estate and enables advanced capabilities such as architecture reconstruction, dependency analysis, migration planning, and automated blueprint generation.

