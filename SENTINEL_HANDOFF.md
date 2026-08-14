# Sentinel Fraud & AML — Engineering Handoff

> **Purpose of this file.** A future engineer or AI agent should be able to read this
> and immediately understand what Sentinel is, how it's built, where everything lives,
> the conventions to follow, and how to extend it safely. Written 2026-08-14.
> Companion file: [SENTINEL_COMPLETED_WORK.md](SENTINEL_COMPLETED_WORK.md) (task-by-task log).

---

## 1. What this is

Sentinel is a **fraud & AML (anti-money-laundering) copilot** demo built on the
Databricks Lakehouse, shipped as **three fully-isolated, branded deployments** for
South African / SA-adjacent banks — **Capitec, Nedbank, Investec** — plus a
**single-codebase generator** that produces any bank from one template.

It demonstrates, end to end on one governed platform: real-time detection, an
AI-assisted analyst investigation workspace, a multi-agent SAR (Suspicious Activity
Report) drafting workflow with regulator-ready goAML XML, proactive typology sweeps,
graph-based entity resolution, impossible-travel geospatial detection, a served
MLflow risk model with governance/drift, and Genie natural-language Q&A.

**Domain framing (SA):** FIC / FICA, SARB Prudential Authority, STRs/CTRs filed to the
Financial Intelligence Centre via goAML, R25,000 cash-threshold structuring, POPIA for
data governance. Keep this framing when extending.

---

## 2. Live deployments

Workspace: `https://fevm-elexon-app-for-settlement-acc.cloud.databricks.com` (`o=7474654808133980`)
Catalog (shared): `elexon_app_for_settlement_acc_catalog`
Serving model (all): `databricks-claude-sonnet-4-5` (env `FRAUD_LLM_ENDPOINT`)

| Bank | Local dir | App URL | GitHub repo | Schemas | Warehouse | Genie space | Dashboard |
|------|-----------|---------|-------------|---------|-----------|-------------|-----------|
| Capitec | `capitec-sentinel-app/` | `https://capitec-fraud-aml-7474654808133980.aws.databricksapps.com` | `github.com/jason-miles/sentinel-app-capitec-bank` (remote name `public`) | `capitec_fraud_aml_{bronze,silver,gold}` | `10fbc0a24b3e418c` | `01f194ad316e127191fec45fdd5fb6bc` | `01f194ad41b618fa8342f8a851b45507` |
| Nedbank | `nedbank-sentinel-app-v2/` | `https://nedbank-fraud-aml-7474654808133980.aws.databricksapps.com` | `github.com/jason-miles/sentinel-app-nedbank` (`origin`) | `nedbank_fraud_aml_*` | `eeee8ab1661ce350` | `01f1962af9e61338a2c438fe01a7f352` | `01f1962b09fc173296fdc15c62aefb4e` |
| Investec | `investec-sentinel-app-v2/` | `https://investec-fraud-aml-7474654808133980.aws.databricksapps.com` | `github.com/jason-miles/sentinel-app-investec` (`origin`) | `investec_fraud_aml_*` | `e227fa247dd5bedd` | `01f1964fc35c10509e628e538ab4c3f8` | `01f1843c859f1acb97f76971d642826c` |
| **Unified template** | `sentinel-app/` | — (generator) | `github.com/jason-miles/sentinel-app` (`origin`) | — | — | — | — |

CLI profile: `fevm-elexon-app-for-settlement-acc` (OAuth). Deploy user workspace path:
`/Workspace/Users/jason.miles@databricks.com/<bank>-fraud-aml-src`.

> **Warehouse isolation matters.** Each bank has a **dedicated** SQL warehouse. Do NOT
> run `databricks warehouses set-permissions` (it overwrites the ACL and evicts another
> app's service principal → 500s). Use `update-permissions` (additive) only.

> Old/stale dirs `investec-sentinel-app/` and `nedbank-sentinel-app/` (no `-v2`) are
> superseded — the `-v2` dirs are the live ones. Ignore the non-v2 ones.

---

## 3. Architecture

Per bank, fully isolated (own schemas, warehouse, Genie, dashboard, app, bundle):

```
Auto Loader landing volume  ──▶  Lakeflow Declarative Pipeline (SQL, serverless)
                                   bronze ──▶ silver ──▶ gold  (medallion)
                                                          │
   MLflow GBT model (Unity Catalog registry) ── scores ──┤
                                                          ▼
                          Databricks App: FastAPI (single process)
                          ├─ /api/*  → Statement Execution API → gold/silver tables
                          ├─ ai_query / serving-endpoint SSE  → Mosaic AI (Claude)
                          ├─ Genie Conversation API           → NL-to-SQL
                          └─ serves React SPA from webroot/
```

- **Backend:** FastAPI, single process (Databricks Apps bind one port; single-process
  avoids CORS). All SQL goes through the Statement Execution API (`server/db.py`).
- **Frontend:** React + TypeScript + Vite, Cytoscape (graph), Recharts (charts).
  Lazy-routed; built to `frontend/dist` then copied to `webroot/` (the name
  `databricks sync` won't special-case) and served by FastAPI.
- **Governance:** Unity Catalog, RLS row filter, LLM-as-judge evals, audit log, drift
  monitor, model registry.

---

## 4. Repo layout (per bank, and template)

```
app/backend/
  app.py                  # FastAPI entry: middleware, routers, warehouse warm-up,
                          #   gzip, immutable static cache, SPA serving
  requirements.txt        # fastapi, uvicorn, pydantic, databricks-sdk, httpx
  app.yaml                # Databricks Apps config: env vars (schemas, warehouse,
                          #   Genie/dashboard IDs, FRAUD_LLM_ENDPOINT, host)
  server/
    config.py             # CATALOG / GOLD_SCHEMA / SILVER_SCHEMA, get_workspace_client()
    db.py                 # ★ SQL client + all perf/LLM helpers (see §6)
    http.py               # fetch_one_or_404(), text_stream()  (HTTP helpers)
    scoring.py, sla.py, casestate.py   # pure domain logic (unit-tested)
    routes/
      alerts.py           # alert queue + detail + feedback
      sherlock.py         # ★ biggest: personas, exec dashboard, queue, case detail,
                          #   case actions/transition/reassign, agent chat, SAR gen, graph
      genai.py            # Genie ask, exec briefing, triage (+ /triage/stream), prioritize
      sar_agents.py       # multi-agent SAR orchestration + goAML XML builder
      sar_eval.py         # LLM-as-judge groundedness/completeness + guardrail
      advanced_aml.py     # screening, pKYC, peer anomaly, model governance, drift, audit, typology sweep
      customers.py, network.py, travel.py, sim.py
    tests/test_routes.py  # 38 tests, mocked DB layer (no warehouse needed)
  frontend/src/
    api.ts                # apiGet/apiPost/apiPostStream + typed endpoint callers
    App.tsx               # lazy routes + Suspense (SkelPage fallback)
    components/ui.tsx      # Skel*/persona context/Sev/money/etc. shared UI
    components/StoryMode.tsx  # in-app guided "Play Demo" walkthrough
    pages/*.tsx           # ExecutiveOverview, AlertInvestigation, Investigation,
                          #   SarFiling, GraphExplorer, Compliance, Reports, AskSentinel, Architecture, Landing
    styles.css            # per-bank :root palette + shared components/skeletons/caret
sql/                      # 00_foundation → 06_sherlock/06_governance DDL + seed
fraud_aml_pipeline/       # Lakeflow declarative pipeline project
ml/retrain_driver.py      # serverless notebook: train GBT, register to UC, score, metrics
dashboards/ genie/ data/ docs/ databricks.yml   # DAB bundle + assets
```

**The unified generator** (`sentinel-app/`):
```
template/          # canonical source == Capitec baseline
banks/<bank>.brand.json   # per-bank: schema prefix, brand words, palette hexes,
                          #   product/segment terms, logo, landing stats, Genie/dash/warehouse IDs
generate.py        # substitutes baseline→target into generated/<bank>/
generated/         # .gitignored output
```
`python3 generate.py --all` regenerates all three; validated to reproduce the
hand-built apps with **zero cross-brand leaks**.

---

## 5. Build / test / deploy (the loop used throughout)

```bash
# Backend tests (from app/backend, needs .venv or python3):
.venv/bin/python -m pytest        # expect 38 passed

# Frontend build (from app/backend/frontend, needs node_modules):
./node_modules/.bin/tsc -b && npm run build
rsync -a --delete dist/ ../webroot/     # ship built UI into webroot

# Deploy one bank (profile = fevm-elexon-app-for-settlement-acc):
DEST=/Workspace/Users/jason.miles@databricks.com/<bank>-fraud-aml-src
databricks sync app/backend "$DEST" --profile fevm-elexon-app-for-settlement-acc
databricks apps deploy <bank>-fraud-aml --source-code-path "$DEST" \
  --profile fevm-elexon-app-for-settlement-acc -o json | grep state   # expect SUCCEEDED
```
> `databricks apps deploy` can take >2 min; if a shell call times out, re-run the
> deploy alone — it's idempotent — and check `databricks apps get <app>` for
> `active_deployment.status.state == SUCCEEDED`.

**Golden rule for changes:** edit the **template first**, verify, then **propagate**
to the three banks. Files that are byte-identical across banks are straight copies;
files with brand tokens (palette hexes in `AlertInvestigation.tsx`/`ExecutiveOverview.tsx`/
`styles.css`, brand words in `genai.py` prompts, `app.py` title/slug) need surgical
edits that preserve each bank's brand. Then regenerate the template's `generated/` to
confirm the generator still reproduces everything. Commit + push all four repos
(Capitec pushes to remote `public`, others to `origin`).

> **Never overwrite the per-bank scenario palette** (`SCEN_COLORS` in
> AlertInvestigation, `KIND_COLOR` in GraphExplorer, `:root` in styles.css). A blanket
> `cp` of these files across banks was a real bug — always verify palettes stay
> Capitec-blue / Nedbank-green / Investec-slate after propagation.

---

## 6. Key patterns & performance conventions (READ BEFORE OPTIMIZING)

Every Statement Execution API call carries **~1.5s fixed round-trip overhead**, and
`ai_query` LLM calls take several seconds. The app is already heavily optimized around
this. Shared helpers live in **`server/db.py`** — use them, don't re-invent:

- **`fetch_all` / `fetch_one` / `execute`** — SQL. Prompts/values are **always bound
  params** (`:name`), never string-interpolated (Spark treats `\` as escape → injection
  risk). Schema/catalog names come from config and are safe to f-string.
- **`_require_success()`** — poll-timeout-safe result checking (handles `resp.status`
  being None on >120s statements).
- **`parallel(*tasks)`** — run independent warehouse reads concurrently. Used in the
  queue, case detail, customer detail, exec-briefing, exec/summary, gather_evidence,
  and the multi-agent orchestrator. **If an endpoint fires N independent SELECTs, wrap
  them in `parallel()`.**
- **`cached_fetch_all(key, sql, ttl=)`** — tiny in-process TTL cache (default 15s, env
  `FRAUD_CACHE_TTL`) for near-static MV reads (exec tiles, personas, model governance,
  screening). Keep TTL short so live-sim/new cases still appear during a demo.
- **`fire_and_forget(fn)`** — background daemon pool for best-effort writes. `audit()`
  uses it so the ~1.5s INSERT never sits on a GET's critical path.
- **`ai_query(prompt)`** — single non-streaming LLM call (`ai_query()` SQL function).
- **`ai_stream(prompt, system, max_tokens)`** — SSE generator over the serving
  endpoint's chat completions (via `httpx`), yields text tokens; **falls back to
  `ai_query` on error**. Paired with **`http.text_stream()`** (FastAPI StreamingResponse,
  buffering disabled) for endpoints like `/api/genai/triage/stream` and
  `/api/sherlock/agent/chat/stream`. Frontend consumes via `api.ts apiPostStream()`.
- **`http.fetch_one_or_404()`** — single-record GETs return real HTTP 404 (not 200 with
  a `{"detail":"not found"}` body), so the client's fetch wrapper routes misses to its
  error state.

**Frontend perceived-perf conventions:**
- Routes are **lazy-loaded**; landing is eager (instant first paint).
- Loading states use **skeletons** (`Skel/SkelKpis/SkelTable/SkelChart/SkelPage` in
  `ui.tsx`), never blank "Loading…" text. Streaming AI panels show a `.stream-caret`.
- Data pages fetch in parallel (`Promise.all` or a combined endpoint like
  `/exec/summary` which returns all dashboard tiles in one call).
- `app.py` warms the warehouse on startup + `/api/health?warm=true`; gzips responses
  >1KB (bundle ships ~67% smaller); serves content-hashed `/assets/*` with a 1-year
  immutable cache.

**FastAPI concurrency note:** routes are sync `def` and run in the anyio threadpool, so
blocking warehouse/LLM I/O and `ThreadPoolExecutor` fan-out are safe. A full async
rewrite was deliberately **rejected** as high-risk churn for no real gain — don't do it.

---

## 7. The three demo "wow" scenarios (keep coherent when editing)

1. **DETECT** — `CASE-90001` (Lerato Sithole): 3 sub-R25k cash deposits = structuring;
   entity resolution reveals the **Motaung mule network** (7 accounts, shared
   device/IP/address, ~90% forwarded in 48h, cross-border cash-out; siblings previously
   closed as false positives). Deep-link: `/graph?q=Motaung%20mule%20network`.
   Live-sim beat: `POST /api/sim/live-alert` inserts a rotating critical `CASE-LIVE-*`
   (auto-pruned to newest 2 so the queue never inflates).
2. **DOCUMENT** — multi-agent SAR (`/sar/CASE-90001`): 3 specialist agents run
   concurrently → supervisor synthesises a regulator-ready STR grounded in retrieved
   adverse media + AML policy + FATF typologies, with schema-valid goAML XML.
3. **ANTICIPATE** — proactive typology sweep (Compliance): a plain-English FATF typology
   (third-party processors layering through gaming merchants) surfaces exposure that
   never tripped a rule. Plus impossible-travel world map + model governance.

**In-app Story Mode** (`components/StoryMode.tsx`) auto-plays these beats (the "▶ Play
Demo" button); the SAR step has a longer `dwell` so the multi-agent narrative renders.

---

## 8. History of what's been done (high level)

- Replicated the original Investec Sentinel to **Capitec**, then **Nedbank** and a fresh
  **Investec** rebuild — all isolated. Personalized synthetic data per bank.
- Real **MLflow GBT** model trained/registered/scored on all three (serverless job).
- Genie spaces + Lakeview dashboards + vector-search RAG (adverse media, AML knowledge).
- **Unified single-codebase generator** (template + brand.json).
- Demo features: graph deep-links, Story Mode that performs live actions, AI-vs-rules
  impact banner, impossible-travel map, live streaming-alert beat.
- Two **critical-review passes** (correctness): 404-vs-200 semantics, poll-timeout
  crash safety, N+1 elimination, parallel LLM judges, logged (not swallowed) errors.
- Upgraded serving model to **Claude Sonnet 4.5** (env-swappable, zero code change).
- **Performance pass** (all measured live): queue 3.5s→2.0s, case 6.5s→2.8s, exec tiles
  cached ~0.8s, combined `/exec/summary` (1 call not 5), warehouse keep-warm,
  poll backoff, `alerts/summary` two-queries→one ROLLUP.
- **Perceived perf:** skeleton loaders everywhere; **live LLM token streaming** for the
  AI Triage + Multi-Agent panels (first token ~3s vs ~7-10s full).
- **Polish:** gzip (bundle -67%), immutable asset caching, dead-code removal.

Test suite: **38 passing** (template + all 3 banks). Full task log in
[SENTINEL_COMPLETED_WORK.md](SENTINEL_COMPLETED_WORK.md).

---

## 9. Good next enhancements (not yet done — genuinely worth doing)

Small/safe:
- SSE streaming for the **SAR narrative** and **exec briefing** panels (same pattern as
  triage/agent chat — `ai_stream` + `text_stream` + `apiPostStream` already exist).
- **Genie streaming** in Ask Sentinel (currently blocks on `create_message_and_wait`).

Larger/product:
- Real **Auto Loader → pipeline** hot path for the live-sim beat (currently a direct
  gold insert to avoid extra SP privilege + pipeline round-trip).
- **Alerting/notifications** (e.g. Slack/email on new critical case) — hooks into `sim`.
- **Feedback-loop retraining trigger** wired to the drift monitor verdict.
- Per-analyst **saved views / filters** persisted to a gold table.
- More FATF **typologies** in the proactive sweep (data + `advanced_aml.typology_sweep`).

Before any perf work: **measure live first** (curl `-w "%{time_total}"` against the app
URL with a bearer token from `databricks auth token`). The obvious backend wins are
already taken; new lag is most likely warehouse cold-start (warm it) or a newly-added
serial query (wrap in `parallel()`).

---

## 10. Conventions checklist for any change

- [ ] Edit **template** first; propagate to 3 banks; regenerate `generated/` to validate.
- [ ] Preserve per-bank **palettes** and **brand words**; scan for cross-brand leaks.
- [ ] Bind all user/DB values as SQL params; never f-string them in.
- [ ] Independent warehouse reads → `parallel()`; near-static reads → `cached_fetch_all`;
      best-effort writes → `fire_and_forget`.
- [ ] Loading UI → skeletons; new AI panels → consider `ai_stream`/`text_stream`.
- [ ] `pytest` (38) green; `tsc -b && npm run build` clean; `rsync dist → webroot`.
- [ ] Deploy all 3 apps; verify live (health + a real endpoint); confirm SUCCEEDED.
- [ ] Commit + push all 4 repos (Capitec → `public`, others → `origin`, template → `origin`).
