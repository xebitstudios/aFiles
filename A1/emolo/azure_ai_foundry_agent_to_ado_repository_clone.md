For an Azure AI Foundry-based code analysis platform, the service that holds cloned repositories depends on the scale, persistence requirements, and analysis patterns. In practice, enterprises typically use one of four patterns.

## Option 1: Azure Container Apps or AKS Local Workspace (Best for Active Analysis)

```text
ADO Repository
      |
      v
Git Clone
      |
      v
Container Workspace
      |
      +-- Code Analysis Agent
      +-- Dependency Agent
      +-- Migration Agent
```

Repositories are cloned into:

```text
/workspaces/repositories/
```

inside a container running on:

* Azure Container Apps
* Azure Kubernetes Service

Advantages:

* Fast analysis
* Supports AST parsing
* Supports dependency graph generation
* Supports code compilation/testing

Disadvantages:

* Workspace disappears when container is recycled unless persisted

Best for:

* On-demand analysis
* Agentic workflows
* Migration assessments

---

## Option 2: Azure Files (Most Common Enterprise Choice)

```text
ADO
 |
 v
Clone Service
 |
 v
Azure Files
 |
 v
AI Agents
```

Use:

[Azure Files](https://azure.microsoft.com/products/storage/files/?utm_source=chatgpt.com)

Example:

```text
/code-repositories/
    claims-app/
    billing-app/
    customer-api/
```

Advantages:

* Shared storage
* Multiple agents can access simultaneously
* Persistent
* Easy mounting into containers

Best for:

* Medium-sized modernization programs
* Teams analyzing hundreds of repositories

---

## Option 3: Azure Blob Storage + Extracted Metadata (Large Scale)

Instead of repeatedly cloning repositories:

```text
ADO
 |
 v
Repository Extractor
 |
 +---- Raw Files
 |
 +---- Metadata
 |
 +---- AST
 |
 +---- Dependency Graph
 |
 v
Blob Storage
```

Store:

* Source files
* Documentation
* Build files
* Configurations

in:

[Azure Blob Storage](https://azure.microsoft.com/products/storage/blobs/?utm_source=chatgpt.com)

Advantages:

* Extremely scalable
* Cheap
* Long-term retention

Disadvantages:

* Not ideal for active Git operations

Best for:

* Thousands of repositories
* Enterprise code intelligence platforms

---

## Option 4: Dedicated Knowledge Layer (Recommended for AI)

Most mature AI platforms do **not** repeatedly analyze raw repositories.

Instead:

```text
ADO Repository
        |
        v
Repository Scanner
        |
        +---- File Inventory
        +---- AST
        +---- Symbols
        +---- APIs
        +---- Dependencies
        +---- Data Flows
        |
        v
Knowledge Store
```

Possible stores:

* Azure AI Search
* Azure Cosmos DB
* Neo4j
* Azure SQL Database

The agent queries the knowledge layer rather than re-reading source files every time.

---

## What I Would Build for Your Modernization Platform

Given your SAS-to-Python, COBOL modernization, architecture discovery, and blueprint-generation goals:

```text
Azure DevOps
      |
      v
Repository Acquisition Service
      |
      +---------------------+
      |                     |
      v                     v
Azure Files         Blob Storage
(raw clone)         (archive)
      |
      v
Analysis Pipeline
      |
      +---- AST Extraction
      +---- Dependency Mapping
      +---- Data Lineage
      +---- Architecture Discovery
      +---- Migration Analysis
      |
      v
Knowledge Graph
      |
      +---- Application Nodes
      +---- Repository Nodes
      +---- Service Nodes
      +---- Database Nodes
      +---- API Nodes
      |
      v
Azure AI Foundry Agents
```

### Recommended Storage Responsibilities

| Purpose                    | Service                  |
| -------------------------- | ------------------------ |
| Active cloned repositories | Azure Files              |
| Repository archives        | Azure Blob Storage       |
| Metadata                   | Azure SQL Database       |
| Dependency graph           | Neo4j or Azure Cosmos DB |
| Semantic code search       | Azure AI Search          |
| Agent orchestration        | Azure AI Foundry         |

For an enterprise-scale repository intelligence platform, the cloned repository itself is usually only a temporary working copy. The long-term value comes from the extracted artifacts—ASTs, dependency graphs, lineage, architecture models, APIs, and embeddings—which are stored in databases, graph stores, and search indexes that AI agents can query efficiently.
