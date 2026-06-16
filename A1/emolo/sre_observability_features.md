# SRE Observability — Feature Specification

> A rebuild-grade specification of the **SRE Observability** product: every sidebar page, its features and data flows, the agent fleet and the verbatim instruction prompts that drive the live investigation pipeline. Written so an engineer with no prior context can reconstruct the product.

---

## 1. Product Overview

SRE Observability is one of two products in a React 18 + Vite 5 + TypeScript (strict) single-page app. The sibling product is **Application Resiliency**; a header **⇄ product switch** toggles between them. The app is **localStorage-backed** (no server DB) with a **Vite dev-server middleware plugin** (`backendApi()` in `vite.config.ts`) exposing `/api/*` endpoints that run in Node context so secrets (Dynatrace OAuth, GitHub PAT) never touch the browser.

The product organizes around three SRE pillars (shown in the sidebar footer):

1. **① Reliability** — SLO & error-budget monitoring
2. **② Response** — AI triage / investigation
3. **③ Toil** — diagnose / remediate / improve

### 1.1 Live-vs-mock seams (`SourceBadge`)

Every data surface is labelled with a `SourceBadge` so mock and live data are always distinguishable:

| Badge | Meaning |
|---|---|
| `DT` | Dynatrace (mock/scenario fallback) |
| `DTLIVE` | Live Dynatrace (Grail/DQL pulled via OAuth) |
| `SN` | ServiceNow (recorded locally; no live write yet) |
| `GH` | GitHub (live repo content read) |
| `Foundry` | Azure AI Foundry agents (scenario demo, mock) |
| `FoundryLive` | Foundry-live (when the Foundry integration is enabled + has a project endpoint) |
| `Ollama` | Local Ollama LLM runtime |
| `SLK` / `PM` / `CNF` | Slack / Postmortem store / Confluence |

`agentRuntimeBadge()` (in `integrationsStore.ts`) returns `'FoundryLive'` if the Foundry integration is enabled and has a `projectEndpoint`, else `'Ollama'` — so the live investigation tab dynamically reflects the actual runtime.

### 1.2 Tech building blocks

- **Dynatrace platform (Grail/DQL):** OAuth2 client-credentials at `sso.dynatrace.com/sso/oauth2/token` → bearer → `POST /platform/storage/query/v1/query:execute` → poll `query:poll`. Tenant `bye75373.apps.dynatrace.com`. Server module: `server/dynatraceFetch.mjs`.
- **LLM reasoning:** local **Ollama** (`http://localhost:11434`) via `ollamaClient.ts`; default model `qwen3-coder:30b` (`DEFAULT_AGENT_MODEL_ID`). Deterministic fallbacks run when Ollama is offline.
- **GitHub content reads:** `server/githubFetch.mjs` + `githubBundle.ts`, using the stored GitHub PAT.
- **RBAC:** `can(resource, action, user)` gate shapes every create/edit/delete button.

---

## 2. Sidebar Navigation

Defined in `components/Sidebar.tsx`, type `View`. Order, icon, hint, and badge:

| # | View id | Label | Icon | Hint | Badge |
|---|---|---|---|---|---|
| 1 | `dashboard` | Dashboard | ◧ | SLOs, incidents, agents | — |
| 2 | `observability` | Observability | ◎ | Records, search & patterns | — |
| 3 | `investigation` | Investigation | 🔎 | Live incident investigation | — |
| 4 | `services` | Services | ▤ | Onboarded services | service count |
| 5 | `onboard` | Onboard service | ＋ | Enroll a new service | — |
| 6 | `configurator` | SLO Configurator | ◴ | Define SLO templates | template count |
| 7 | `agents` | Agents | ◈ | Foundry agent fleet | agent count |
| 8 | `guardrails` | Guardrails | 🛡 | Agent safety gates & policies | guardrail count |
| 9 | `permissions` | User Permissions | ◉ | RBAC & users | — |

**Footer:** the three pillars, a user chip (click → Permissions) showing the acting user + role, a `mode: mock` indicator, and a theme (dark/light) toggle. Root container: `SreConsole.tsx`, which holds `view` state, the RBAC `gate()`, and `investigatingService` (the service handed from Dashboard → Investigation).

---

## 3. Page Specifications

### 3.1 Dashboard (`DashboardView.tsx`)

Real-time SLO / golden-signal dashboard for onboarded services. Supports **custom dashboards** (service subsets) and **live Dynatrace pulls**.

**Layout (top→bottom):**

- **Header** — `{dashboard name} dashboard`, subtitle, and a **scenario bar** (`latency-breach`, `error-spike`, `saturation`, `healthy`) toggling mock scenario data. Source legend badges (DT/SN/Foundry/SLK/PM/CNF).
- **KPI row** — headline metrics from `data.kpis` (scenario-driven).
- **DashboardPicker** — tabs per dashboard (built-ins "All Services", "Payments", then user-created). `+ New` and `✎ Edit` open a **DashboardEditor** modal (name, description, service checkboxes with all/none helpers). Persists via `saveDashboard` / `deleteDashboard` (`dashboardStore`, key `sre.dashboards.v1`).
- **Left column:**
  - **ServicePanel — SLO cards** `DT`. Per service: name, team, overall status pill (`HEALTHY` / `WARN` / `BURNING` / `EXHAUSTED` / `NO_DATA`), expandable SLO rows (error-budget bar, % remaining, burn-rate ×). **🔎 Investigate** button on breaching services (WARN/BURNING/EXHAUSTED) → `onInvestigate(service)`. **⟳ Pull live signals from Dynatrace** button (disabled unless `dynatraceLiveConfigured()`) → `refreshDtSignals(names, windowMinutes)`; badge flips `DT`→`DTLIVE`. A no-telemetry note prompts the pull when SLOs are configured but unpopulated.
  - **GoldenSignals** — 4 mini line charts (p95 latency / error rate / traffic / CPU saturation) over a 30-point series from `primary.signals`.
  - **InvestigationPipelinePanel (scenario demo)** — the 3-agent pipeline visualization for the mock incident; **🔎 Open live investigation →** routes the first breaching service to the Investigation view. `Foundry`-mock (genuinely mock here).
  - **CommsLog** — A2A hand-off timeline (`buildCommsLog`).
- **Right column:**
  - **IncidentFeed** — scenario incidents; selecting one enables **⤓ Generate & store postmortem** (`draftPostmortem` → `savePostmortem`).
  - **AgentTimeline** — chronological agent events for the active incident.
  - **PostmortemArchive** `PM` — saved postmortems (`listPostmortems`), each with **Publish to Confluence** (`publishToConfluence`).

**Live pull path (Step 3.5):** `dtDashboardStore` caches signals by `service.name` (key `sre.dt.signals.v1`); `liveHealthFor(onboarding)` turns a cached signal into `ServiceHealth` with SLO status computed. Dashboard prefers live, falls back to scenario mock, then `NO_DATA`. `resolveDashboardServices()` maps a dashboard's onboarding IDs to `ServiceHealth`.

---

### 3.2 Observability (`ObservabilityView.tsx`)

Unified, searchable **90-day record stream** across incidents, agent activity, A2A comms, and postmortems, with pattern detection. Gated on `incidents: read`.

**Layout:**

- **Header** — badges `SN` `Foundry` `PM` (+ `DTLIVE` if configured). **⟳ Pull Dynatrace alerts** button (Step 4): `refreshDtAlerts()` converts breached/warning SLOs into incident records, caches (`dtAlertsStore`, key `sre.dt.alerts.v1`), and merges them to the top of the feed. Disabled unless `dynatraceLiveConfigured()`.
- **Search + time window** — full-text query across title/detail/service/refId/agent; window buttons 7d / 30d / 90d.
- **Facet chips** (each shows a live count, toggles a filter): **Source** (Incidents / Agent activity / A2A comms / Postmortems), **Service** (dynamic via `facetServices`), **Severity** (SEV1–3), **Signal** (latency/errors/saturation/traffic). A **clear** button resets.
- **Detected patterns** (`detectPatterns`) — cards for: recurring service+signal (≥5), frequent root-cause category (≥8), high escalation rate (≥35%), day-of-week clustering (≥1.8× avg). Severity: alert / watch / info.
- **Record volume over time** — Recharts stacked bar chart by source; period buttons Daily / Weekly / Monthly (`timeBuckets`).
- **Per-service breakdown** (`serviceStats`) — table: Service | Records | Incidents | Escalations (%) | Postmortems | Top signal | Top cause.
- **Unified record feed** — paginated rows (20/page, "Show more"), each a colored source badge + title + meta (relative time, service, severity, signal, category, escalation, refId).

**Store:** `observabilityStore.ts` — `listRecords(now)` synthesizes a reproducible (seeded-PRNG) 90-day history merged with persisted postmortems + live DT alert records. `applyFilter`, `facetServices`, `timeBuckets`, `serviceStats`, `detectPatterns` are pure helpers over that list.

---

### 3.3 Investigation (`InvestigationView.tsx`)

The **live SRE incident-investigation pipeline**, opened by clicking 🔎 Investigate on a breaching Dashboard service. Reasoning is real Ollama LLM output over **live Dynatrace signals + live GitHub code**. See §4.2 for the full agent pipeline and prompts.

**Layout:**

- **Header** — `Investigation · {service}`, badges `DTLIVE` `GH` `{runtime}` (runtime = Ollama|FoundryLive). Empty state prompts the user to pick a breaching service on the Dashboard.
- **Incident header card** — overall status pill, team · assignment group, breached-SLO chips (`name: sli% / target% (status)`, SEV-colored).
- **Live golden signals** `DTLIVE` — p95 latency / error rate / traffic / CPU saturation (warn thresholds 500 ms / 1% / — / 75%).
- **Investigation engine card** — Ollama health (`checking…` / `● connected` / `● not reachable`), **model picker** (Ollama models ordered by `PREFERRED_MODELS`, ★ preferred), pipeline description, and **▶ Run investigation** / **↻ Re-investigate** (disabled unless Ollama OK). Live `progress` text per stage.
- **Live step timeline** — `StepRow` per stage with an agent-colored dot (✓ done / ⟳ running / ↻ retry / • queued), agent name, label, detail, status.
- **Code cause card** `GH` — when `run.codeCause` exists: 📄 file:line, finding, offending-line `<pre>`, **Fix:** recommendation (green border if found; muted if not).
- **Result card** `SN` — `InvestigationPipelinePanel` rendering Triage → Evidence (per specialist) → Synthesis (root cause, confidence bar with 0.75 gate, AUTO-REMEDIATE vs HUMAN ESCALATION).
- **ServiceNow remediation** — "Raise ServiceNow tickets from this root cause": **＋ Create ServiceNow incident** (INC) and **＋ Create change request** (CHG). Each is **independent** — clicking one turns *only that button* into a done pill (`INC…`/`CHG…` · "raised · in Gap Tickets"); the other stays enabled. Each kind files **at most once**. Both tickets land in **Application Resiliency → Gap Tickets** (see §3.10).
- **Past investigations** — clickable history rows (incident #, severity, truncated root cause, timestamp).

**Stores/helpers:** `investigationStore.ts` (`sre.investigations.v1`; `nextInvestigationId` `INV-…`, `nextIncidentNumber` `INC8…`, `getLatestInvestigationFor`); `investigationTickets.ts` (`createServiceNowTicket`); `serviceIdentityStore` (service→repo); `githubBundle` (code); `dynatraceFetch.mjs` (`dynatraceProbe`).

---

### 3.4 Services / Onboarded services (`OnboardedServices.tsx`)

Cards for every service enrolled in SLO monitoring (`listOnboardings()`, store key `sre.onboarding.v1`, 12 seeded + user).

**Per card:** name · team; status badge (`draft`/`validated`/`live`); entity selector + `dtEntityId`; **repo row** (`repo:` link or "not mapped", `GH` badge — resolved via `resolveByServiceName(name)?.repoUrl`); enabled SLO chips (name + target%); meta (assignment group, window `Nd`, sweep `Ns`, freeze-on-exhaustion); badges DT/SN/SLK.

**Actions (RBAC-gated):**
- **✎ edit repo** (`services: edit`) — toggles an inline **RepoEditor**: GitHub repository URL + Branch (placeholder `https://github.com/xebitstudios/opentelemetry-demo`). **Save repository** writes to the service's **ServiceIdentity** (`saveIdentity`, creating one if absent), so the **Code Cause Analyst** can fetch + scan the source. Note: "Used by the Code Cause Analyst…".
- **remove** (`services: delete`) — hidden for seeded `ONB-CHECKOUT`/`ONB-CATALOG`/`ONB-IDENTITY`.
- **＋ Onboard service** (`services: create`) → Onboard page.

---

### 3.5 Onboard service (`OnboardService.tsx`)

Full enrollment form. Gated on `services: create` (a banner explains read-only otherwise). Form seeded from `blankOnboarding(nowIso, seq)` (id `ONB-YYYYMMDD-###`).

**Section 1 — Identity & routing:** service name, owning team, ServiceNow assignment group `SN`, Slack escalation channel `SLK`.

**Section 2 — Dynatrace entity & service identity:** entity selector (`type("SERVICE"),tag("app:…")`), optional entity ID (typing it re-derives every SLO's SLI DQL via `applyEntityId`); **Service Identity** sub-block to link source repo + ServiceNow CI (DT ↔ CMDB ↔ repo); SLO window (days, default 28), eval interval (sec, default 60), min valid events (NO_DATA floor, default 100), freeze-deploys-on-exhaustion checkbox.

**Section 3 — Select SLOs:** one card per template in `sliCatalog(entityId)`. Each: enable checkbox + signal color dot; if not advisory → target% + objective(ms) + budget-fraction display; **Act on breach** toggles (Page on-call / Open incident / Auto-remediate / Advisory only); collapsible SLI DQL (`dqlSurface` + rendered DQL).

**Validation — `validateOnboarding` (L1–L4 gate):** name, team, assignment group required; entity selector must contain `tag(` or `entityName(`; ≥1 SLO enabled; each enabled non-advisory SLO needs `0 < target < 100` and ≥1 action; paging SLOs require an assignment group.

**Submit:** **Save draft** (`status: 'draft'`, no validation) or **✓ Validate & go live** (runs L1–L4; on pass, persists a ServiceIdentity if repo/CI/entity supplied, then `onSubmit` with `status: 'live'`).

---

### 3.6 SLO Configurator (`SloConfigurator.tsx`)

Authoring surface for reusable **SLO templates** (`sloTemplateStore.ts`, key `sre.slo.templates.v1`). Each template becomes selectable when onboarding.

**Template card:** signal dot + name; built-in/custom badge; advisory badge; target%, thresholdMs (latency), DQL surface, SLI ref; default actions; collapsible SLI DQL (with `{entity}` placeholder); **remove** (custom only, `slo-templates: delete`).

**Form:** name (kebab-case, unique), golden signal (latency/errors/traffic/saturation), description, SLI query ref, DQL surface (`fetch spans` / `timeseries` / `fetch logs`), advisory-gauge checkbox, default target% (non-advisory), objective ms (latency), **SLI DQL** textarea (must contain `{entity}`), default actions (≥1). `validateTemplate` enforces kebab-case + uniqueness, `0<target<100`, `{entity}` presence, and surface rules (e.g. `timeseries` can't use `countIf`).

**Built-in templates:** `availability` (errors, 99.9%), `latency-p95` (latency, 99.5%, 500 ms), `traffic-context` (traffic, advisory, timeseries), `saturation-cpu` (saturation, advisory, timeseries). `renderDql(t, entityId)` substitutes `{entity}`.

**Signal palette:** latency `#4f8cff`, errors `#e74c3c`, traffic `#2ecc71`, saturation `#e67e22`.

---

### 3.7 Agents (`AgentsView.tsx`)

The **Foundry agent fleet** — see §4.1 for the full roster and verbatim instructions. UI per agent: name, role, pillar, status, the attached guardrails, and an **effective model** display.

**Model picker (`ModelField`):** selecting one of the two Foundry **class deployments** (`fast` → `gpt-5.1-mini`, `reasoning` → `gpt-5.1`) clears any pin; selecting an **approved concrete model** (grouped by provider — OpenAI / Anthropic / Ollama, `PROVIDER_ORDER`) pins it via `approvedModelId`. `agentModelDisplay` shows the pinned model (label + `provider · id`) or the class deployment (`{class} class`). A general/default selector lets all agents default to a chosen approved model (default `qwen3-coder:30b`). Approved models are managed in `AgentModelsModal` (`agentModelsStore.ts`, `MODEL_CATALOG`).

---

### 3.8 Guardrails (`GuardrailsView.tsx`)

Configurable **safety gates & policies** for agents (`guardrailStore.ts`, key `sre.guardrails.v1`). Enabled per agent on the Agents page; sensible defaults auto-selected by role (`defaultGuardrailNames(role)`).

**Card:** category dot + name; built-in/custom; default badge; description; category pill; severity (`advisory`/`standard`/`strict`); applies-to roles (or "all roles"). **✎ Edit** / **remove** (RBAC-gated).

**Form:** name (the contract string agents reference), description, category (`safety`/`data`/`cost`/`security`/`reliability`/`compliance`/`quality`), severity, "recommend on by default", applies-to roles (checkbox grid over the 9 agent roles; none = all).

**Seeded guardrails (16):** Universal — PII redaction, Prompt-injection (XPIA) filter, Audit & provenance logging, Schema-validate every envelope, Token/spend ceiling, Tool-call rate limit. Safety/change — Human-in-the-loop approval, Blast-radius limit, Rollback/dry-run, Circuit breaker. Authority — Read-only (no remediation), Confidence gate (0.75). Orchestration — Single writer of state, Connected-agents depth cap (2). Routing/data — Enum-constrained routing, NO_DATA suppression. Lookups: `getGuardrailByName` (fuzzy), `guardrailsForRole`, `appliesToRole`.

**Category colors:** safety `#e74c3c`, data `#9b59b6`, cost `#f1c40f`, security `#e67e22`, reliability `#2ecc71`, compliance `#4f8cff`, quality `#1abc9c`.

---

### 3.9 User Permissions / RBAC (`PermissionsView.tsx`)

Client-side RBAC policy layer (`rbacStore.ts`) that shapes the UI and blocks actions; a real impl enforces the same matrix server-side (Entra ID groups).

- **Acting as** — role switcher (`setCurrentUserId`) over active users, with role pill + description.
- **Your effective permissions** — per-resource C/R/E/D badges for the current user.
- **Permission matrix** — Resource × Role table; **Admin** can toggle cells (`toggleMatrix`) and **Reset to defaults** (`resetMatrix`), otherwise read-only.
- **User directory** + **User editor modal** — name, email (regex `/.+@.+\..+/`), role, active; create/edit/delete gated on `users: …`.

**Model:** `ROLES` = admin / editor / operator / viewer; `RESOURCES` = services, slo-templates, dashboards, agents, guardrails, postmortems, incidents, users; `ACTIONS` = create / read / edit / delete. Core gate: `can(resource, action, user)` (false if user inactive). Matrix persisted at `sre.rbac.matrix.v1`; users at `sre.rbac.users.v1`; session at `sre.rbac.session.v1`. Seeded users: Ada Admin, Eli Editor, Omar Operator, Vera Viewer. Default matrix: admin = all; editor = CRE on operational resources + dashboards CRUD + incidents R/E + users R; operator = read + dashboards CRE + incidents R/E; viewer = read-only (nothing on users).

---

### 3.10 Cross-product output — Gap Tickets

Investigation tickets (and Tuner/Vuln/Audit tickets) are `ResiliencyTicket`s persisted via `saveTicket` (`resiliencyStore.ts`) and shown in **Application Resiliency → Gap Tickets** (`ResiliencyConsole.tsx`). Each row carries a **record-type chip** derived from the number prefix: **INC** (investigation incident, orange), **CHG** (investigation change, blue), **VULN** (red), **TUNE** (yellow), **GAP** (RGAP, muted). Numbers: `nextInvestigationTicketNumber('incident'|'change')` → `INC…`/`CHG…`. Routing resolves the service's CMDB assignment group from its ServiceIdentity. The ServiceNow *write* is recorded locally (status + work note); there is no live `/api/now/table` endpoint yet.

---

## 4. Agents & Instruction Prompts

Two agent surfaces exist: the **catalog fleet** (Agents page, `agentStore.ts` — the Azure-AI-Foundry-style spec used for display/governance) and the **executable investigation pipeline** (`investigationWorkflow.ts` — the prompts actually sent to Ollama at runtime). Model classes: `reasoning` → `gpt-5.1`, `fast` → `gpt-5.1-mini`.

### 4.1 Catalog fleet (Agents page)

| Agent | id / name | Role · Pillar | Class | Instruction (verbatim) |
|---|---|---|---|---|
| **Orchestrator** | `AG-ORCHESTRATOR` · reliability-supervisor | orchestrator · All | reasoning | *Drive the incident state machine. Delegate in natural language to connected sub-agents; validate each returned envelope against its schema; call transition_state; dispatch the next agent. Never perform domain work yourself. Log every hand-off as an AgentInteraction.* |
| **SLO & Error-Budget Monitor** | `AG-MONITOR` · slo-monitor | monitor · ① Reliability | fast | *For each ServiceSLO, pull good/valid per alert window, compute SLI + per-SLO burn rate, suppress on NO_DATA, emit budget-status every cycle and an alert when both long+short windows exceed the per-SLO threshold.* |
| **Triage & Router** | `AG-TRIAGE` · triage | triage · ② Response | fast | *Classify symptom (latency/errors/saturation/traffic/db). Derive impact×urgency (never set priority directly). Dedup by correlation_id. Pick the investigation_path. Constrain routing/severity fields to enum/CMDB lookups.* |
| **Investigator (coordinator)** | `AG-INVESTIGATOR` · investigator | investigator · ② Response | reasoning | *Pass 1: from the triage symptom+scope, choose the investigation_path. Pass 2: weigh specialist Evidence (supports vs ruled-out), produce hypotheses, score confidence, decide auto-remediate vs human-escalation against the gate.* |
| **Change & Communications** | `AG-COMMS` · change-comms | comms · ③ Toil | fast | *Create/update the incident record idempotently. Add work notes mirroring agent decisions. On human-escalation, post ranked hypotheses + evidence to the Slack channel with the incident link.* |
| **Latency Specialist** | `AG-SPEC-LATENCY` · spec-latency | specialist · ② Investigation Layer | fast | *Run the scoped fetch spans probe for latency (p95 traces). Interpret the result for this signal only. Emit an Evidence verdict; if nothing found, return ruled-out with low strength (never silence).* |
| **Error Specialist** | `AG-SPEC-ERROR` · spec-error | specialist · ② Investigation Layer | fast | *Run the scoped fetch spans / fetch logs probe for error rate (exceptions & spans). Interpret the result for this signal only. Emit an Evidence verdict; if nothing found, return ruled-out with low strength (never silence).* |
| **Saturation Specialist** | `AG-SPEC-SATURATION` · spec-saturation | specialist · ② Investigation Layer | fast | *Run the scoped timeseries probe for CPU / memory / queue saturation. Interpret the result for this signal only. Emit an Evidence verdict; if nothing found, return ruled-out with low strength (never silence).* |
| **Traffic Specialist** | `AG-SPEC-TRAFFIC` · spec-traffic | specialist · ② Investigation Layer | fast | *Run the scoped timeseries probe for request volume. Interpret the result for this signal only. Emit an Evidence verdict; if nothing found, return ruled-out with low strength (never silence).* |
| **DB/Storage Specialist** | `AG-SPEC-DBSTORAGE` · spec-dbstorage | specialist · ② Investigation Layer | fast | *Run the scoped fetch spans (client) probe for query performance / IO. Interpret the result for this signal only. Emit an Evidence verdict; if nothing found, return ruled-out with low strength (never silence).* |

Each spec also records its tools (e.g. signal-scoped `DynatraceTool`), inputs/outputs (e.g. `Evidence{specialist, finding, signal_strength, supporting}`), and default guardrails (read-only, XPIA filter, explicit ruled-out, etc.). The Orchestrator's guardrails include *single writer of state* and *depth-2 connected-agents cap*; the Investigator's include the *confidence gate (0.75)*.

### 4.2 Executable investigation pipeline (`investigationWorkflow.ts`)

`runInvestigation(svc, model, nowIso, callbacks)` runs 6 steps and emits live `InvestigationStep`s. **Persona prepended to every LLM call:**

> *You are an SRE incident-investigation agent. You reason ONLY from the provided live Dynatrace signals — never invent metrics you cannot see. Be precise, terse, and decisive.*

Call timeout 120 s; confidence gate 0.75. `metricLines(m)` renders:
```
p95 latency: {latencyP95Ms} ms (p99 ~{latencyP99Ms} ms)
error rate: {errorRatePct}%
traffic: {trafficRps} rps
CPU saturation: {saturationCpuPct}%
```

**STEP_DEFS:** SLO Monitor (detect) → Triage & Router (triage) → specialist fan-out (investigate) → Code Cause Analyst (code) → Investigator coordinator (synthesize) → Change & Communications (communicate).

**Step 0 — SLO Monitor** (deterministic): confirms breached SLOs, opens the incident number, sets severity from overall health.

**Step 1 — Triage & Router** (LLM). Verbatim prompt:
```
Classify this SRE incident from the LIVE signals and decide which specialists to dispatch.
SERVICE: {svc.name} (team {svc.team}, overall {svc.overall})
BREACHED SLOs: {name (signal, sli X% vs target Y%, status); …  | 'none'}
LIVE SIGNALS:
{metricLines(metrics)}

Return STRICT JSON: { "symptom": "Latency|Error Rate|Saturation|Traffic|DB/Storage", "scope": "single-service|dependency-chain|infrastructure|regional", "blastRadius": "<short>", "investigationPath": ["Latency Specialist", ...up to 3 most relevant], "rationale": "<1 sentence>" }
```
Fallback: `defaultPath(metrics)` selects specialists by signal thresholds.

**Step 2 — Specialist fan-out** (LLM per specialist, parallel). Each specialist first pulls its own live probe: `pullDynatraceProbe(PROBE_SIGNAL[name], svc.name, 60)`.

`PROBE_SIGNAL`: Latency→`latency`, Error→`errors`, Saturation→`saturation`, Traffic→`traffic`, DB/Storage→`db`. Sample probes per specialist (`SPECIALISTS[].probe`): `fetch spans | summarize p99=percentile(duration,99)`; `fetch spans | filter request.is_failed==true | summarize count()`; `timeseries cpu=avg(dt.host.cpu.usage)`; `timeseries rps=rate(dt.service.request.count)`; `fetch spans | filter span.kind=="client"`.

Verbatim prompt (per specialist):
```
You are the {name}. Focus ONLY on {spec.focus}. You ran this Dynatrace probe and got these rows — interpret them.
SERVICE: {svc.name}
PROBE: {probe.query ?? spec.probe}
PROBE RESULTS:
{probeText}
SUMMARY SIGNALS:
{metricLines(metrics)}

Return STRICT JSON: { "finding": "<one precise sentence citing a SPECIFIC value/endpoint from the probe rows>", "signalStrength": <0..1>, "supporting": <true if this evidence supports a root cause, false if ruled out> }
```
Fallback: `heuristicFinding` / `heuristicStrength`.

**Step 3 — Code Cause Analyst** (LLM). Resolves `resolveByServiceName(svc.name)` → repo, fetches `fetchGithubBundle(repo, branch, svc.name)`. The bundle ranks **feature-flag/fault-injection configs** (flagd, `demo.flagd.json`, LaunchDarkly, Unleash) and the **failing service's own subtree** first, and demotes build-only noise (`tsconfig.json`, lockfiles) — see `server/githubFetch.mjs` `pathRelevance`. Verbatim prompt:
```
You are the CODE CAUSE ANALYST investigating a LIVE production incident on service "{svc.name}" (primary symptom: {signal}). Runtime evidence from the specialists:
{topEvidence}

Find the code/config that CAUSES this runtime symptom. Strong candidates, in order:
1. FEATURE-FLAG / FAULT-INJECTION config (e.g. flagd, demo.flagd.json, LaunchDarkly, Unleash). An ENABLED fault flag (a non-default variant such as a forced failure, an injected delay like "10sec", or a failure rate) that targets "{svc.name}" or its request path is the MOST LIKELY cause in this environment — call it out explicitly with the flag name and its active value.
2. A dependency/downstream call on the failing path of "{svc.name}" with no retry / timeout / circuit-breaker / error-handling, or a bug in that service's own handler code.

Reason ONLY about things that affect RUNTIME behavior. Do NOT cite build-time or compiler config (e.g. tsconfig.json "strict", linter settings, lockfiles) — those do not cause latency, errors, or saturation. If nothing in the source plausibly explains the symptom, say so honestly (an injected fault flag or external dependency may live outside this bundle).

Cite the exact file and line.
SOURCE (repo {repo}, the failing service's files and flag configs ranked first):
{source}

Return STRICT JSON: { "file": "<path:line>", "finding": "<what in the code/config explains the incident>", "evidence": "<the offending line>", "recommendation": "<the fix>" }
```
If unmapped/unreadable, returns `CodeCauseFinding{ ok:false, finding:"No repository mapped to {svc} — add a Source repository…" }`.

**Step 4 — Investigator (coordinator)** (LLM). Verbatim prompt:
```
Synthesize the root cause from the runtime evidence AND the code analysis, then decide.
SERVICE: {svc.name} · severity {severity}
LIVE SIGNALS:
{metricLines(metrics)}
RUNTIME EVIDENCE (each specialist's own probe):
{- specialist (supports|ruled-out, strength X): finding …}
CODE ANALYSIS: {codeCause.file: finding [evidence]  | codeCause.finding}

Return STRICT JSON: { "rootCause": "<ranked root cause fusing runtime + code>", "confidence": <0..1>, "proposedAction": "<remediation action OR escalation summary; cite the code fix if known>", "changeType": "standard|normal|emergency" }
```
Decision: `confidence ≥ 0.75` → `auto-remediate`, else `human-escalation`. Fallback: `heuristicConfidence` / `heuristicRootCause`.

**Step 5 — Change & Communications** (deterministic): records the decision; on escalation sets the Slack channel (e.g. `#sre-incident`). The UI then offers the **Create ServiceNow incident / change** buttons (§3.3, §3.10).

### 4.3 Related workflow (remediation)

`resolutionWorkflow.ts` is the Application-Resiliency remediation loop that fixes the Gap Tickets the investigation files: Resiliency Coder ↔ Validator (≤3 iters) → Unit Test Validator (≤3) → Guardrail Validator → PR Agent. Persona: *You are a software reliability engineer fixing resiliency gaps in source code. Produce minimal, correct, idiomatic changes. Reason only from the given context.* (Full prompts live in that file; it is the downstream consumer of this product's output.)

---

## 5. Data Stores Reference

| Store | localStorage key | Holds |
|---|---|---|
| `onboardingStore` | `sre.onboarding.v1` | `ServiceOnboarding[]` (12 seeded + user) |
| `serviceIdentityStore` | `sre.service.identities.v1` | `ServiceIdentity[]` (DT entity ↔ CMDB CI ↔ repo) |
| `sloTemplateStore` | `sre.slo.templates.v1` | `SloTemplate[]` (4 built-in + custom) |
| `dashboardStore` | `sre.dashboards.v1` | custom dashboards |
| `dtDashboardStore` | `sre.dt.signals.v1` | cached live golden signals by service name |
| `dtAlertsStore` | `sre.dt.alerts.v1` | cached live SLO-alert incident records |
| `observabilityStore` | (in-memory, seeded PRNG) | 90-day `ObsRecord[]` history |
| `postmortemStore` | `sre.postmortems.v1` | `Postmortem[]` |
| `investigationStore` | `sre.investigations.v1` | `InvestigationRun[]` |
| `resiliencyStore` | `sre.resiliency.tickets.v1` | `ResiliencyTicket[]` (INC/CHG/VULN/TUNE/GAP) |
| `agentStore` / `agentModelsStore` | agent specs / approved models | fleet + model catalog |
| `guardrailStore` | `sre.guardrails.v1` | `Guardrail[]` (16 seeded + custom) |
| `rbacStore` | `sre.rbac.matrix.v1` / `.users.v1` / `.session.v1` | matrix / users / session |

### 5.1 Server endpoints (`vite.config.ts` → `server/*.mjs`)

`/api/dynatrace-test`, `/api/dynatrace-metrics`, `/api/dynatrace-slos`, `/api/dynatrace-service-signals`, `/api/dynatrace-probe` (→ `dynatraceFetch.mjs`); `/api/github-fetch-bundle`, `/api/github-check` (→ `githubFetch.mjs` / `githubCheck.mjs`). Secrets are read server-side from the stored integration config; the browser never holds them.

---

## 6. Key Types (abridged)

```ts
type SloStatus = 'HEALTHY' | 'WARN' | 'BURNING' | 'EXHAUSTED' | 'NO_DATA' | 'ADVISORY'
type GoldenSignal = 'latency' | 'errors' | 'saturation' | 'traffic'
type Severity = 'SEV1' | 'SEV2' | 'SEV3'

interface InvestigationRun {
  id; service; incidentNumber; severity; signal; model?; status
  steps: InvestigationStep[]; metrics?: ServiceMetricsSnapshot
  breachedSlos: { name; signal; target; sli; status }[]
  pipeline?: InvestigationPipeline; codeCause?: CodeCauseFinding
  snTickets?: { id; number; kind: 'incident' | 'change' }[]
  startedAt; completedAt?
}
interface SynthesisResult { rootCause; confidence; confidenceThreshold; decision; proposedAction; changeType?; escalateTo?; slackChannel? }
interface CodeCauseFinding { repo; ok; file?; finding; evidence?; recommendation? }
interface ServiceIdentity { id; dtEntityId; serviceNowCi; repoUrl; repoBranch; displayName; team; assignmentGroup; environment?; tier?; source; createdAt }
```

---

## 7. Rebuild Checklist

1. Scaffold Vite + React + TS; add the `backendApi()` middleware plugin and the `server/*.mjs` modules for Dynatrace + GitHub.
2. Implement the localStorage stores (§5) with their seeds.
3. Build the **ServiceIdentity** layer and resolvers first — it is the correlation key the Dashboard, Investigation, and Gap Tickets all depend on.
4. Build the sidebar + `SreConsole` shell with the RBAC `can()` gate.
5. Implement pages in dependency order: SLO Configurator → Onboard → Services → Dashboard → Observability → Investigation; then Agents / Guardrails / Permissions.
6. Wire the live pulls (Dynatrace signals/alerts/probes, GitHub bundle) behind the `SourceBadge` seams.
7. Implement the investigation pipeline (§4.2) against Ollama with the verbatim prompts and deterministic fallbacks.
8. Wire the **Create ServiceNow incident/change** buttons → `createServiceNowTicket` → Gap Tickets, with INC/CHG record-type chips.
```
