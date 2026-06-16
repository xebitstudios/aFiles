# Application Resiliency — Feature Specification

> A rebuild-grade specification of the **Application Resiliency** product: every sidebar page, its features and data flows, the multi-agent workflows and the verbatim LLM prompts that drive them. Companion to `sre_observability_features.md`. Written so an engineer with no prior context can reconstruct the product.

---

## 1. Product Overview

Application Resiliency is the sibling product to **SRE Observability** in the same React 18 + Vite 5 + TypeScript (strict) app; the header **⇄ product switch** toggles between them. Where SRE Observability watches running services, Application Resiliency **hardens the code and config behind them**: it audits repositories for resiliency gaps, scans for vulnerabilities, tunes resilience config from live traffic, auto-remediates via PRs, and captures the learnings in a knowledge base.

The product is **localStorage-backed** and uses **local Ollama** LLMs (`ollamaClient.ts`, default `qwen3-coder:30b`) for all agent reasoning, each workflow with **deterministic fallbacks** when Ollama is offline. Live reads (GitHub content, Dynatrace metrics, AWS) go through the Vite dev-server middleware `/api/*` endpoints so secrets stay server-side. Root container: `ResiliencyConsole.tsx`.

### 1.1 Shared concepts

- **`ResiliencyTicket` (Gap Tickets):** the common currency. Auditor, Tuner, Vulnerability Detective, and the SRE Investigation pipeline all produce these; they are persisted by `resiliencyStore.ts` (key `sre.resiliency.tickets.v1`) and shown on the Gap Tickets page. Number prefix encodes the source: `RGAP` (audit gap), `TUNE` (tuner), `VULN` (vulnerability), `INC`/`CHG` (SRE investigation).
- **Severity → priority:** `SEV_PRIORITY` maps `critical/high/medium/low` → `{priority 1-4, impact 1-3, urgency 1-3}`.
- **Category → routing:** `CATEGORY_GROUP` maps each resiliency category to a default assignment group; overridden by the service's ServiceIdentity (`resolveByRepo`/`resolveByServiceName`) when mapped.
- **Repo access:** local folder via the **File System Access API** (`showDirectoryPicker`, real read + write-back) or **remote** via the GitHub API (`fetchGithubBundle` → `/api/github-fetch-bundle`, read-only). `repoHandles` remembers a picked folder for later fix-apply.
- **`SourceBadge`** labels every surface (Repo / GH / DT / DTLIVE / SN / Ollama / AWS …) to mark mock-vs-live seams.

---

## 2. Sidebar Navigation

Defined in `ResiliencyConsole.tsx` (`NAV`, type `ResView`):

| # | id | Label | Icon | Hint |
|---|---|---|---|---|
| 1 | `auditor` | Resiliency Auditor | ◎ | Scan a repo |
| 2 | `history` | Audit History | ▤ | Past audits |
| 3 | `tickets` | Gap Tickets | 🎫 | Resiliency gaps |
| 4 | `agent` | Resiliency Agent | 🤖 | Auto-remediate a ticket |
| 5 | `tuner` | Resiliency Tuner | 🎚 | Tune settings from live traffic |
| 6 | `vulnerability` | Vulnerability Detective | 🛡 | Scan repo for vulnerabilities |
| 7 | `vulnfixer` | Vulnerability Fixer | 🩹 | Patch a vulnerability ticket |
| 8 | `prs` | Pull Requests | ⎘ | Review fixes |
| 9 | `checks` | Resiliency Checks | ☑ | Cloud resource checks |
| 10 | `knowledge` | KnowledgeHub | 📚 | Patterns from prior resolutions |
| 11 | `integrations` | Configure Integrations | ⚙ | Connect real systems |

`ResiliencyConsole` holds: `view`, `openAuditId`, `openTicketId`, pagination (`ticketPage`/`auditPage`), `sevFilter`, `ticketQuery`, `assignedTicketId` (Resiliency Agent), `vulnFixTicketId` (Vulnerability Fixer), and batch-resolution state.

---

## 3. Page Specifications

### 3.1 Resiliency Auditor (`ResiliencyAuditor.tsx` + `AuditResult.tsx`)

Points a **4-agent workflow** at a repo to evaluate resiliency patterns and file gap tickets.

**Form:** Repository URL/path (or `📁 Browse local…` via File System Access API; example repos provided), Branch, Provider (`github`/`gitlab`/`azure-devops`/`local`), Language (auto-detected on folder pick via `detectLanguage`). **Engine:** Ollama health (`checking…`/`● connected v{ver}`/`● not reachable`) + model picker.

**Three run modes** (a colored `res-mode` card explains which is active):
- **Real audit** — local folder + Ollama: Scanner reads real files (`scanDirectory`), agents run the model over the actual source. Button **▶ Run real resiliency audit**. Remembers the handle (`rememberRepoHandle`) for later fixes.
- **Remote audit** — GitHub PAT configured + a `github.com/org/repo` URL: `fetchGithubBundle` pulls the repo over the API; same agents, read-only. Button **▶ Run remote audit (GitHub)**.
- **Demo (mock)** — URL-only / Ollama down: `buildAudit` synthesizes deterministic findings; animated steps. Button **▶ Run resiliency audit (demo)**.

**Workflow stream — 4 agents** (`workflowSteps`): Orchestrator (plan & dispatch) → Repository Scanner (clone & scan source tree) → Repository Resiliency Analyzer (evaluate resiliency patterns) → Resiliency Gap Ticket Creator (file gap tickets) → Guardrail Validator (verify guardrail enforcement). Each `StepRow` shows an agent-colored dot, label, detail, status.

**Resiliency dimensions checked (10):** retries-backoff, timeouts, circuit-breaker, bulkhead-isolation, rate-limiting, health-checks, graceful-degradation, idempotency, observability, dependency-failover.

**`AuditResult`:** resiliency **score** (0–100, color by threshold ≥80/≥60/≥40), severity bar, **agent reports** (summary + bullets per agent), workflow trace, **resiliency strengths** (positive patterns found), **findings** (severity pill, category, description, evidence code, fix), and the **gap tickets** created. Findings that are critical/high/medium become tickets (`isTicketWorthy` → `commitAudit`): id `TCK-{audit}-{n}`, number `RGAP7…`, routed via `resolveByRepo(repo.url)`.

**Verbatim LLM prompts** (system persona: *You are a senior reliability/SRE engineer. You reason ONLY from the provided source — never invent files, lines, or behavior you cannot see. Be precise and cite file:line.*):

- **Orchestrator:** `You are the ORCHESTRATOR agent of a resiliency audit. Given the repository's file inventory, plan the audit: identify the service's likely entry points, the dependency-interaction surface to focus on, and which resiliency dimensions matter most for this codebase.` … returns `{ "summary", "bullets": [...] }` (≤5 bullets).
- **Repository Scanner:** `You are the REPOSITORY SCANNER agent. From the source below, describe the architecture relevant to resiliency: what external dependencies/IO the code talks to (HTTP, DB, queues, caches), how calls are made, and where the failure-prone boundaries are. Do NOT judge quality yet — just map the dependency surface.` … returns `{ "summary", "bullets" }` (≤6).
- **Repository Resiliency Analyzer:** `You are the REPOSITORY RESILIENCY ANALYZER agent. Evaluate how the source handles dependency failures and load.` Reports both `findings` (gaps, each with category/severity/title/description/file/line/evidence/recommendation) **and** `strengths` (positive patterns), max 12 findings / 8 strengths; *If there are no gaps, return findings: [] but STILL list the strengths.*
- **Resiliency Gap Ticket Creator:** `You are the RESILIENCY GAP TICKET CREATOR agent. Given these confirmed resiliency gaps (JSON), write a concise engineering ticket body for each (problem, impact, acceptance criteria). Also give a one-line triage summary.` … returns `{ "summary", "bullets" }`.

**Stores:** `resiliencyStore.ts` keys `sre.resiliency.audits.v1` / `sre.resiliency.tickets.v1`; `listAudits`, `saveAudit`, `buildAudit`, `commitAudit`, `isTicketWorthy`, `nextAuditId` (`AUD-YYYYMMDD-###`). Score = `max(5, 100 − Σ penalty)` with penalties critical 25 / high 14 / medium 7 / low 3.

---

### 3.2 Audit History (`view === 'history'`)

Paginated list of past audits (`listAudits`, **15 per page**). Each row: large resiliency score (colored), repo URL, meta (branch, language, findings, tickets, files, timestamp); click → detail.

**Detail view:** back link, the `AuditResult` (with `showSteps`), plus a **bulk-assign bar** when the audit produced tickets: **▦ Send all to ServiceNow** (`bulkToServiceNow`) and **🤖 Send all to Resiliency Agent (sequential)** (`runBatchResolution` over eligible tickets, with a live progress bar and Stop). On completion: "✓ Batch complete — N resolved (PR created)…".

---

### 3.3 Gap Tickets (`view === 'tickets'`)

ITSM-style list of every `ResiliencyTicket`.

- **Severity dashboard:** All / Critical / High / Medium / Low filter buttons (counts), plus a display-only **Open** count.
- **Search:** by number (RGAP/TUNE/VULN/INC/CHG), ticket id (TCK…), finding id (RF…), or description.
- **Columns (25/page):** Number (with **record-type chip** via `ticketKind`: GAP / VULN / TUNE / INC / CHG) · Ticket id · Pri (P1–P4) · Short description · Assignee · State (New/In Progress/Closed) · **Actions**.
- **Row actions:** **▦ ServiceNow** (route to ServiceNow — mock write: status `in-progress`, `assignedTo: 'In ServiceNow'`, work note); then either **🛡 Fixer** (VULN tickets → Vulnerability Fixer) or **🤖 Agent** (others → Resiliency Agent). Click a row → **TicketDetail** drawer.

**TicketDetail (`TicketDetail.tsx`):** ServiceNow-faithful record — state flow (New→In Progress→Closed), number, priority/impact/urgency, category, configuration item (repo), assignment group, assigned-to (editable), caller, opened; description `<pre>` + evidence `<code>`; **activity stream** with Work notes / Additional comments tabs (`onAddNote`) and a newest-first note list. Header actions: **🤖 Assign to Resiliency Agent** / **🛡 Assign to Vulnerability Fixer**, **Accept/Work**, **Resolve**, **Reopen**.

---

### 3.4 Resiliency Agent (`ResiliencyAgentView.tsx` + `resolutionWorkflow.ts`)

Autonomous remediation of a gap ticket → a reviewed **pull request**. Shows an **AgentDashboard** (PR stats, recent tasks) and a **work queue** of assigned tickets. For the active ticket: summary, resolution engine (Ollama + model), **▶ Run resolution workflow**, the live workflow stream, validation results, **proposed fix** (full file), **✍ Apply fix to repository** (writes via File System Access API, backs up `.bak`), unit tests, and the PR-created confirmation.

**Workflow — 10 steps (`STEP_DEFS`), two ≤3-iteration correction loops:**
0 Resiliency Agent · locate → 1 Resiliency Agent · plan → 2 Resiliency Coder · code → 3 Resiliency Validator · validate-fix → 4 Resiliency Agent · correct (hand-back) → 5 Unit Test Validator · write-tests → 6 Unit Test Validator · validate-tests → 7 Resiliency Agent · correct → 8 Guardrail Validator · guardrail → 9 Resiliency Agent · pr.

**Verbatim prompts** (persona: *You are a software reliability engineer fixing resiliency gaps in source code. Produce minimal, correct, idiomatic changes. Reason only from the given context.* — temp 0.2, json, 180 s):

- **Resiliency Coder:**
```
You are the RESILIENCY CODER agent. Fix this resiliency gap with a concrete code change.
Gap: {title}
Category: {category}
Severity: {severity}
Affected location (evidence): {evidence}
Description: {body}
Recommended approach: {recommendation}{correction if retrying}{CURRENT FULL CONTENT if available}

Return ONLY JSON:
{ "file": "<affected file path>", "language": "<lang>", "patch": "<a short readable snippet of the key change>", "fullContent": "<the COMPLETE updated file content, ready to write to disk — preserve all unrelated code>", "explanation": "<why this resolves the gap>" }
The fullContent MUST be the entire file with your fix applied, not a diff or fragment.
```
- **Resiliency Validator:** `You are the RESILIENCY VALIDATOR agent. Review this proposed fix for the resiliency gap. Check that it actually resolves the gap, is correct, idiomatic, and doesn't introduce regressions or break the public contract.` … `{ "passed", "issues": [...], "summary" }`.
- **Unit Test Validator (writer):** `You are the UNIT TEST VALIDATOR agent. Write unit tests that verify the resiliency fix works and the gap can't regress (e.g. assert retry/timeout/circuit-breaker behavior).` … `{ "file", "code", "summary", "passed", "issues" }`.
- **PR author:** `You are the RESILIENCY AGENT preparing a pull request. Write a clear PR title and body for this resiliency fix.` … `{ "title", "description" }`.

On success, fires KnowledgeHub doc authoring (§3.10). Stores: `resolutionStore.ts` keys `sre.resolution.tasks.v1` / `sre.resolution.prs.v1`; `runResolution`, `applyFixToRepo`, `runBatchResolution`.

---

### 3.5 Resiliency Tuner (`ResiliencyTunerView.tsx` + `tunerWorkflow.ts`)

Multi-agent **config tuning from live Dynatrace signals** — flags resilience settings that are **too-tight** (causing avoidable failures) or **too-loose** (masking instability), with human approval and schedules.

**Tabs:** **Run a Check** (select onboarded/typed service + model → **▶ Run tuning check**), **Schedules** (per-service cadence hourly/daily/weekly/monthly; ▶ Run now / Enable / Disable / Delete), **History** (past `TuningRun`s).

**Workflow — 8 steps (`STEP_DEFS`):** Resiliency Tuner · pull (plan) → Telemetry Analyst · pull (Dynatrace observability) → Latency & Timeout Tuner · tune → Retry & Backoff Tuner · tune → Circuit Breaker & Bulkhead Tuner · tune → Tuning Reviewer · review (de-dup & validate) → Guardrail Validator · guardrail → Resiliency Tuning Scorer · report.

**Live metrics** (`tunerMetrics.ts` `pullServiceMetricsLive`): resolve service → `dtEntityId` (ServiceIdentity), `pullDynatraceMetrics(entity, window)` → `ServiceMetricsSnapshot` (p99/p95 latency, error %, traffic rps, CPU %, derived retry volume & timeout rate); falls back to deterministic per-service-type mock (`source: 'mock'`).

**Recommendations (`TuningRecommendation`):** `{ category, parameter, currentValue, recommendedValue, flag: 'too-tight'|'too-loose'|'optimal', rationale, expectedOutcome, confidence, priority, evidence, decision }`. Each gets **✓ Approve / ✕ Reject**. Approved ones → the **Apply** panel: repo name/location/branch/config-path, then **✓ Apply to local repo & create PR**, **🤖 Assign to Resiliency Agent**, or **📨 Post Tuner ticket to ServiceNow** (`fileTunerTickets` → `TUNE…` tickets).

**Verbatim specialist prompt** (persona: *You are a senior SRE specializing in resilience tuning… Reason ONLY from the provided metrics. Prefer minimal, well-justified changes…* — temp 0.2, json, 120 s):
```
Service "{service}" already has resilience patterns in place but likely uses default/stale values chosen at design time. Using ONLY these live traffic patterns, recommend SPECIFIC tuned config values for {focus}.

For each setting decide whether it is:
- "too-tight": causing avoidable failures (e.g. a timeout that cuts off healthy slow calls → premature timeouts), OR
- "too-loose": masking instability (e.g. a breaker/timeout/retry budget so lax that failures hide and amplify, e.g. retry storms), OR
- "optimal": already matches the observed behavior (omit these).

METRICS ({window}):
{metricsLines}

Return STRICT JSON: {"recommendations":[{"category":"<one of: {categories}>","parameter":"<config key>","currentValue":"<likely current/default value>","recommendedValue":"<SPECIFIC tuned value…>","flag":"too-tight|too-loose","rationale":"…","expectedOutcome":"…","confidence":"low|medium|high","priority":"low|medium|high|critical","evidence":"<the metric(s) that justify it>"}]}
Base every value on the actual numbers above, not design-time guesses. If nothing should change for this area, return an empty array. Do not invent metrics.
```
The three tuners differ by `focus`: timeouts & deadlines; retry counts & backoff; circuit-breaker thresholds & bulkhead/pool sizing. Heuristic fallbacks recommend e.g. `timeout ≈ p99 × 1.3` when p99>800 ms, fewer retries + backoff on retry storms, tighter breaker thresholds on high error rate. Score = `max(15, 100 − Σ weight)` (critical 26 / high 16 / medium 8 / low 3). Stores: tuner runs/schedules + `tunerTickets.ts` `fileTunerTickets` / `nextTunerTicketNumber`.

---

### 3.6 Vulnerability Detective (`VulnerabilityDetectiveView.tsx` + `vulnWorkflow.ts`)

A **10-agent** repo scan covering **security + malicious + resilience**, producing prioritized findings with patches → VULN tickets. Local-folder or remote-GitHub source; each scanner runs an **LLM pass + a deterministic regex pattern scan** alongside.

**Workflow — 10 steps:** Repository Discovery → Dependency Security (SCA/CVE) → Static Security (SAST) → Malicious Pattern → Secrets → Resilience → Infrastructure (IaC/container) → Risk Prioritizer (P0–P4) → Patch Generation → Patch Validation.

**Persona:** *You are a principal application-security engineer and threat researcher. You reason ONLY from the provided source — never invent files, lines, or behavior you cannot see. Flag real, evidenced issues and cite file:line. Cover security vulnerabilities, malicious/suspicious code, and operational-resilience weaknesses.*

**Verbatim scanner prompt** (per role, temp 0.15, json, 120 s, ≤8 findings):
```
You are the {role}. {focus}
Report ONLY real, evidenced issues you can see in the source. Cite the exact file and line.
Return ONLY JSON:
{ "findings": [ { "vulnClass": "security"|"malicious"|"resilience"|"secrets"|"dependency"|"infrastructure", "category": "<short-kebab-case>", "severity": "critical"|"high"|"medium"|"low", "title": "<=90 chars", "description": "...", "file": "<exact path>", "line": <int>, "evidence": "<one offending code line>", "recommendation": "...", "cwe": "<optional CWE-id>" } ] }
Max 8 findings. If none, return { "findings": [] }.

SOURCE:
{bundle}
```
Roles/focus: **Dependency Security** (known-vulnerable/EOL/typosquatting/dependency-confusion from manifests); **Static Security/SAST** (injection SQL/command/path/SSRF, auth bypass, broken access control, weak crypto, unsafe serialization via taint/data-flow); **Malicious Pattern** (exfiltration, dynamic code exec, obfuscation `eval(atob(...`, logic bombs, persistence); **Secrets** (API keys, cloud creds, DB passwords, private keys); **Resilience** (missing timeouts/retries/breakers/bulkheads, SPOFs, observability gaps); **Infrastructure** (privileged containers, missing network policies, weak RBAC in Docker/K8s/Terraform/Helm).

**Patch Generation prompt** (temp 0.2, json, 180 s, ≤12 findings):
```
You are the PATCH GENERATION AGENT. Produce a concrete fix for this finding.
Finding: {title} ({category}, {severity}) in {file}:{line}
Offending code: {evidence}
Recommendation: {recommendation}
Return ONLY JSON: { "fixedSnippet": "<the corrected code>", "diff": "<short before/after>", "explanation": "<why this resolves it, 1-2 sentences>" }
```

**Prioritization (P0–P4):** malicious → P0; injection (sql/command/ssrf/unsafe-deserialization) → P0/P1; auth-bypass/broken-access-control → P1; dependency/infrastructure → P1/P2; secrets → P2; resilience → P2/P3. **Risk score** = `max(5, 100 − Σ SEV_WEIGHT × (malicious ? 1.5 : 1))`, weights critical 25 / high 14 / medium 7 / low 3.

**Result UI:** risk score, P0–P4 counts, findings grouped by priority (each: checkbox, title, evidence, description, recommendation, expandable validated patch diff), then **🎫 Open N gap ticket(s)** → `fileVulnTickets` → `VULN…` tickets (title `[P0] …`, body carries the patch diff + CWE; routed by vulnClass → security team; left unassigned for Gap-Tickets routing).

---

### 3.7 Vulnerability Fixer (`VulnerabilityFixerView.tsx` + `vulnFixWorkflow.ts`)

Applies the **patch already embedded in a VULN ticket** (no fix-generation loop). UI is built from **collapsible cards** (`CollapsibleCard`, ▸/▾): ticket summary, fix engine (Ollama + model + **▶ Run vulnerability fix**), workflow stream, validation results, **patched file** (full content + **⇆ See Diff**), **✍ Apply fix to repository** (File System Access write + `.bak`), and PR-created.

**Workflow — 3 steps:** Vulnerability Fixer · locate (resolve repo + file, extract the embedded patch from the ticket body) → Patch Applier · code → Security Validator · validate-fix → Vulnerability Fixer · pr (branch `security/{number}`).

**Verbatim prompts** (persona: *You are a senior application-security engineer remediating a vulnerability. Apply the proposed patch correctly and minimally, preserving the rest of the file. Return only what is asked.* — temp 0.2, json, 180 s):
- **Patch Applier:** `Apply this security PATCH to the FILE, changing only what the patch requires and preserving everything else.` … `{ "fullContent", "patch", "explanation" }`.
- **Security Validator:** `Review this fix for the vulnerability "{title}". Does it resolve the issue without introducing a regression?` … `{ "passed", "issues": [...], "summary" }`.
- **PR author:** `Write a pull-request title and body for this security fix. Cover: the vulnerability, the fix, and the risk if unpatched.` … `{ "title", "description" }`.

Reuses `applyFixToRepo` from `resolutionWorkflow.ts`; opens a `PullRequest` and marks the ticket In Progress.

---

### 3.8 Pull Requests (`PullRequestsView.tsx`)

Review surface for PRs created by the Resiliency Agent / Tuner / Vulnerability Fixer. Each `PullRequest`: `{ id (PR-YYYYMMDD-###), number (from #42 up), ticketId, ticketNumber, repo, branch, title, description (markdown), fix: FixArtifact{file, language, patch, fullContent, explanation}, test?, status: 'open'|'approved'|'denied'|'merged', iterations, createdAt, reviewedBy? }`. The view lists PRs with status, the ticket they resolve, the diff/full file, and **approve / deny / merge** actions (merge/clone is recorded; real Git push is the live-impl seam). Store: `resolutionStore.ts` (`sre.resolution.prs.v1`; `listPRs`, `savePR`, `nextPRId`, `nextPRNumber`).

---

### 3.9 Resiliency Checks (`ResiliencyChecksView.tsx`)

**Cloud-resource** resilience checks (distinct from code audits). Each `CloudCheck` targets a resource (e.g. `resourceType: 's3-bucket'`) and reports a **score**, **strengths** (✓ title + evidence), and **findings** (title, description, **Fix:** recommendation). A check can be re-run (`rerun` → e.g. `runS3ResiliencyCheck(resource)`), and an item opens a `CheckDetail` view. Live reads go through `/api/aws-resiliency-check` (AWS) and `/api/github-resiliency-check` (repo k8s/mesh/Dockerfile config); mock results when an integration isn't configured. Checks look for multi-AZ/replication, backups/versioning, autoscaling, health checks, and the like.

---

### 3.10 KnowledgeHub (`KnowledgeHub.tsx` + `knowledgeStore.ts` + `knowledgeAgent.ts`)

A self-populating knowledge base: every successful audit/remediation/tuning/fix **auto-authors a doc** (fire-and-forget from the workflows), and a **KB Agent** answers questions over them.

- **Tree:** `buildKnowledgeTree` groups docs **language/service-type → repo → docs** (`repoLabel`, `inferServiceType`). Facets and full-text search via `searchKnowledgeDocs` / `knowledgeFacets`.
- **`KnowledgeDoc`:** `{ id, title, source, repo, language, serviceType, category?, summary, body (markdown), tags[], refs, authoredBy, createdAt }`. Store key `sre.knowledge.docs.v1`.
- **Persona (both prompts):** *You are the KnowledgeHub Agent — a documentation librarian for an SRE/resiliency engineering org. You write clear, reusable, vendor-neutral engineering notes that help future engineers repeat what worked and avoid what didn't. Be specific and practical; never invent details not present in the input.*
- **Author prompt (`authorKnowledgeDoc`, json, 60 s):**
```
Write a concise, reusable KnowledgeHub entry capturing what was learned, so future engineers working on similar code can reuse it.

Repository: {repoLabel}
Language: {language}
Service type: {serviceType}
Resiliency area: {category}
Work type: {source}

CONTEXT (the agent's actual output):
{facts}

Return STRICT JSON:
{ "title": "<= 90 chars, specific (pattern + language/service when relevant)", "summary": "1-2 sentence abstract for search results", "body": "markdown: ## Problem / ## What we did / ## Why it works / ## Reusable pattern / ## Watch out for — grounded ONLY in the context", "tags": ["lowercase keywords incl. language, service type, resiliency pattern"] }
```
- **Q&A (`askKnowledgeHub`):** retrieval (`rankDocs`, keyword-overlap, language/service/category/title weighted ×2, top 6) + LLM synthesis with cited `[n]` sources: `Answer the engineer's question using ONLY the KnowledgeHub excerpts below. Cite the sources you used as [n]. If the excerpts don't cover it, say so and suggest what to look for. Be concrete: name the patterns, languages, and service types involved.` Returns `{ ok, answer, sources[], message? }`; never throws.

---

### 3.11 Configure Integrations (`integrationsStore.ts`)

The catalog that moves the app from mock → live. Each integration is a `{ id, name, category, fields[], … }` whose values persist to `sre.integrations.v1`. **Test connection** for live ones runs server-side (e.g. `/api/dynatrace-test`, `/api/github-test`, `/api/test-aws`); the browser never holds the secret. `getConfig(id).values`, `dynatraceLiveConfigured()`, and `agentRuntimeBadge()` (Foundry-live vs Ollama) read from here.

**Catalog (by category):** observability — **Dynatrace** (envUrl, oauthClientId, oauthClientSecret, accountUrn, apiToken), **Datadog**; itsm — **ServiceNow**; scm — **GitHub** (pat, apiBaseUrl), **GitLab**, **Bitbucket**; comms — **Slack**; docs — **Confluence**; ai — **Azure AI Foundry** (projectEndpoint…), **Ollama**; cloud — **AWS**, **GCP**; platform — **Kubernetes**; collab — **Atlassian**, **SharePoint**; cms — **Contentful**; crm — **Salesforce**, **HubSpot**; data — **Snowflake**, **Databricks**, **Tableau**. Field types: `text` / `password` / `url` / `select`. Test-connection notes for several reads, e.g. *"Real test = backend OAuth/Basic auth against /api/now/table. Not done in the browser (no CORS)."*

---

## 4. Data Stores Reference

| Store | localStorage key | Holds |
|---|---|---|
| `resiliencyStore` | `sre.resiliency.audits.v1` | `ResiliencyAudit[]` |
| `resiliencyStore` | `sre.resiliency.tickets.v1` | `ResiliencyTicket[]` (RGAP/TUNE/VULN/INC/CHG) |
| `resolutionStore` | `sre.resolution.tasks.v1` | `ResolutionTask[]` |
| `resolutionStore` | `sre.resolution.prs.v1` | `PullRequest[]` |
| tuner store / `tunerTickets` | tuning runs & schedules | `TuningRun[]`, `TunerSchedule[]` |
| vuln scan store | vulnerability scans | `VulnScan[]` |
| `knowledgeStore` | `sre.knowledge.docs.v1` | `KnowledgeDoc[]` |
| `integrationsStore` | `sre.integrations.v1` | integration configs |
| `serviceIdentityStore` | `sre.service.identities.v1` | `ServiceIdentity[]` (shared with SRE side) |

### 4.1 Server endpoints (`vite.config.ts` → `server/*.mjs`)

`/api/github-fetch-bundle`, `/api/github-test`, `/api/github-resiliency-check` (GitHub); `/api/dynatrace-test`, `/api/dynatrace-metrics` (Dynatrace); `/api/test-aws`, `/api/aws-resiliency-check` (AWS). Secrets are read server-side from the stored integration config.

---

## 5. Key Types (abridged)

```ts
type ResiliencyCategory = 'retries-backoff'|'timeouts'|'circuit-breaker'|'bulkhead-isolation'|'rate-limiting'|'health-checks'|'graceful-degradation'|'idempotency'|'observability'|'dependency-failover'
type FindingSeverity = 'critical'|'high'|'medium'|'low'
type TicketState = 'open'|'in-progress'|'closed'
type VulnPriority = 'P0'|'P1'|'P2'|'P3'|'P4'
type VulnClass = 'security'|'malicious'|'resilience'|'secrets'|'dependency'|'infrastructure'

interface ResiliencyTicket { id; number; auditId; findingId; title; category; severity; body; repo; status; priority; impact; urgency; assignmentGroup; assignedTo?; caller; recommendation?; evidence?; createdAt; updatedAt; notes: TicketNote[] }
interface TuningRecommendation { id; category; parameter; currentValue; recommendedValue; flag: 'too-tight'|'too-loose'|'optimal'; rationale; expectedOutcome; confidence; priority; evidence; decision }
interface VulnFinding { id; vulnClass; category; severity; priority; title; description; file; line?; evidence; recommendation; cwe?; patch?; validated? }
interface PullRequest { id; number; ticketId; ticketNumber; repo; branch; title; description; fix; test?; status: 'open'|'approved'|'denied'|'merged'; iterations; createdAt; reviewedBy? }
```

---

## 6. Rebuild Checklist

1. Build the shared **`resiliencyStore`** (audits + tickets) and the **`ResiliencyTicket`** shape with `SEV_PRIORITY` / `CATEGORY_GROUP` first — it is the hub every workflow writes to.
2. Add the repo-access layer: File System Access API (`repoHandles`, read/write/`.bak`) and the GitHub bundle path (`fetchGithubBundle` → `/api/github-fetch-bundle`).
3. Implement the Ollama client + `call/specialist/extractJson` helper with deterministic fallbacks.
4. Build views in dependency order: Auditor → Audit History → Gap Tickets/TicketDetail → Resiliency Agent → Tuner → Vulnerability Detective → Vulnerability Fixer → Pull Requests → Resiliency Checks → KnowledgeHub → Configure Integrations.
5. Wire each workflow's `STEP_DEFS` + verbatim prompts (§3); reuse `resolutionWorkflow.applyFixToRepo` for write-back.
6. Wire KnowledgeHub auto-authoring as a fire-and-forget call at the end of each successful workflow.
7. Add `record-type chips` (`ticketKind`) on Gap Tickets so INC/CHG/VULN/TUNE/GAP are distinguishable.

> **Mock-vs-live seams to keep honest:** ServiceNow ticket *writes*, PR *merges*, and fix *file-writes beyond the local folder* are recorded locally — there is no live ServiceNow/Git push endpoint yet. Real audits/scans/tuning over local folders and remote GitHub, plus Dynatrace metric pulls and AWS checks, **are** live.
