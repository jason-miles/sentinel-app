# Sentinel — Full Project Journey (start → finish)

> The complete story of this project so any future engineer or AI can pick it up with
> full context. Chronological. For deep detail see the companion docs:
> - [SENTINEL_HANDOFF.md](SENTINEL_HANDOFF.md) — architecture, repo layout, code patterns
> - [SENTINEL_COMPLETED_WORK.md](SENTINEL_COMPLETED_WORK.md) — task-by-task log
> - [SENTINEL_DEMO_OPS.md](SENTINEL_DEMO_OPS.md) — warm-up jobs + demo runbook
>
> Last updated 2026-08-15.

---

## 0. TL;DR — where things stand now

**Four Databricks Apps, all live and healthy, on workspace**
`fevm-elexon-app-for-settlement-acc` (`o=7474654808133980`), catalog
`elexon_app_for_settlement_acc_catalog`:

| App | URL | Repo |
|-----|-----|------|
| Capitec Sentinel | capitec-fraud-aml-7474654808133980.aws.databricksapps.com | github.com/jason-miles/sentinel-app-capitec-bank |
| Nedbank Sentinel | nedbank-fraud-aml-7474654808133980.aws.databricksapps.com | github.com/jason-miles/sentinel-app-nedbank |
| Investec Sentinel | investec-fraud-aml-7474654808133980.aws.databricksapps.com | github.com/jason-miles/sentinel-app-investec |
| MCB Customer 360 | mcb-customer-360-7474654808133980.aws.databricksapps.com | github.com/jason-miles/mcb-customer360-app |
| (unified template) | — generator | github.com/jason-miles/sentinel-app |

All optimized, tested (38 backend tests), and kept warm by server-side jobs.
**`investec-fraud-aml` is HANDS-OFF** — no app deploy/edit/delete without re-authorization.

---

## 1. Origin — what was asked

Starting point: an existing Investec "Sentinel" fraud & AML app on Databricks. The ask
grew over time:
1. **Replicate it for Capitec Bank** (SA) — same architecture, Capitec branding, Capitec
   synthetic data, deploy scripts. Then **Nedbank**, then a fresh **Investec** rebuild.
2. Incorporate a Google-Doc account plan (all tabs) — full build of 7 domain items + 3
   "WOW" demo scenarios.
3. Push to GitHub, deploy to the workspace, create Genie spaces + dashboards.
4. Make synthetic data recognizably each bank's.
5. Real MLflow model (not a stub).
6. Unify into **one codebase + brand.json generator**.
7. Repeated rounds of **"review, optimise, make it WOW, make it fast."**

---

## 2. What Sentinel is (domain)

A fraud & AML copilot on the Databricks Lakehouse. SA regulatory framing throughout:
FIC/FICA, SARB Prudential Authority, STRs/CTRs to the Financial Intelligence Centre via
goAML, R25,000 cash-structuring threshold, POPIA. Surfaces: Executive Overview, Alert
Investigation queue + case detail, multi-agent SAR drafting (→ goAML XML), Compliance
(sanctions screening, perpetual-KYC, peer anomaly, impossible-travel map, model
governance/drift, typology sweep), Graph Explorer (entity resolution), Ask Sentinel
(Genie NL-to-SQL), plus an in-app guided "Story Mode".

**Three demo "wow" scenarios (keep coherent):** (1) DETECT — structuring → hidden Motaung
mule network via entity resolution → live streaming alert; (2) DOCUMENT — multi-agent SAR
with grounded citations + goAML XML; (3) ANTICIPATE — proactive FATF typology sweep that
finds exposure no rule caught.

---

## 3. Architecture (per bank, fully isolated)

```
Auto Loader landing volume → Lakeflow Declarative Pipeline (SQL, serverless)
   bronze → silver → gold (medallion)         MLflow GBT model (UC registry) scores →
                                              │
              Databricks App: FastAPI (single process)
              ├─ /api/*  → Statement Execution API → gold/silver
              ├─ ai_query / serving-endpoint SSE → Mosaic AI (Claude Sonnet 4.5)
              ├─ Genie Conversation API → NL-to-SQL
              └─ serves React SPA from webroot/
```
Isolation per bank: own schemas `<bank>_fraud_aml_{bronze,silver,gold}`, own SQL
warehouse, Genie space, dashboard, app, DAB bundle. Backend FastAPI (sync routes in the
anyio threadpool). Frontend React+TS+Vite (Cytoscape graph, Recharts), lazy-routed, built
to `webroot/`.

---

## 4. Build history (phases)

- **Capitec** built first from the Investec original; branding, palette, SA data.
- **Deployment**: CLI OAuth, schemas + bronze DDL, synthetic seed, silver/gold/sherlock
  SQL, Lakeflow pipeline, Genie space + Lakeview dashboard, wired IDs, verified.
- **Nedbank** + **fresh isolated Investec** rebuilt to parity.
- **Real MLflow GBT** trained/registered to UC/scored on all three (serverless job).
- **Vector Search RAG** (adverse media, AML knowledge), LLM-as-judge evals, audit log,
  RLS row filter, drift monitor.
- **Unified generator** (`sentinel-app/`): `template/` (Capitec baseline) +
  `banks/<bank>.brand.json` + `generate.py` → `generated/<bank>/`. Reproduces the
  hand-built apps with zero cross-brand leaks.
- **Demo WOW**: graph deep-links, Story Mode that performs live actions, AI-vs-rules
  impact banner, impossible-travel world map, live streaming-alert beat.

### Notable bugs fixed along the way (so they aren't reintroduced)
- Word-splitting in bash schema-rename loops → `while IFS= read -r`.
- `pmod(id*5,5)≡0` → all cases 'new' → collapsed Sankey. Fixed to `*7`.
- Missing Auto Loader landing volume → pipeline schema-inference failed.
- Shared-warehouse ACL outage: `set-permissions` overwrote another app's SP → 500s.
  **Rule: use additive `update-permissions`; each app has a DEDICATED warehouse.**
- Cross-brand palette leaks from blanket `cp` of `AlertInvestigation.tsx` /
  `ExecutiveOverview.tsx` / `styles.css` → always preserve per-bank palettes on propagation.

---

## 5. Correctness review passes

Two deep backend reviews found + fixed real defects:
- **404 semantics**: single-record GETs returned HTTP 200 with `{"detail":"not found"}`;
  the React fetch wrapper (throws on `!res.ok`) never saw the error. Added
  `http.fetch_one_or_404()` → real 404s; de-duped the fetch-then-404 idiom.
- **db.py poll-timeout crash**: `resp.status` could be None on >120s statements. Added
  `_require_success()` + defensive manifest checks.
- **N+1** in impossible-travel → single windowed query.
- Sequential LLM judges → concurrent.
- Silent `except: pass` → logged warnings (audit + live-sim prune stay best-effort but visible).
- Added regression tests. **38 backend tests pass** on all 3 banks + template.

---

## 6. Performance work (the big theme — "make it fast, boss is watching")

Root fact: each Statement Execution API call ≈ 1.5s fixed overhead; `ai_query` LLM calls
several seconds. Shared helpers in **`server/db.py`** (use these, don't reinvent):
- `parallel(*tasks)` — run independent warehouse reads concurrently.
- `cached_fetch_all(key, sql, ttl=)` — in-process TTL cache (env `FRAUD_CACHE_TTL`, 15s
  default) for near-static MV reads.
- `fire_and_forget(fn)` — background daemon pool (audit writes off the critical path).
- `ai_query(prompt)` / `ai_stream(prompt,...)` — non-streaming / SSE token streaming.
- `http.fetch_one_or_404`, `http.text_stream`.

Applied: queue 3 serial→parallel (3.5s→2.0s); case detail 4 reads→parallel + async audit
(6.5s→2.8s); exec dashboard 6 tiles→TTL-cached; **combined `/exec/summary`** (1 call vs 5);
`alerts/summary` two queries→one `GROUP BY ROLLUP`; exec-briefing + customer detail
parallelized; poll backoff; **in-app warehouse keep-warm loop + startup prime**;
model-governance/screening cached.

**Model upgrade**: `FRAUD_LLM_ENDPOINT` centralized in db.py → swapped to
**databricks-claude-sonnet-4-5** with zero code change (env var).

**Perceived latency**: lazy routes; **skeleton loaders** everywhere (no blank "Loading…");
**live LLM token streaming** for AI Triage + Multi-Agent panels (first token ~3s vs ~7-10s
full) with a blinking caret; `apiGet` auto-retry on transient/5xx (cold-start self-heal);
**gzip** (bundle −67%) + **immutable asset caching**.

Measured warm latency after all this: ~0.8–2.7s across endpoints on all three.

---

## 7. The two-app Investec incident (important context)

There were briefly **two** Investec apps: the healthy `investec-fraud-aml` (all fixes) and
a stale orphaned `investec-sentinel` (old source, 500-ing). The user was looking at the
broken one while fixes landed on the good one — hence "still broken." Resolution:
**deleted `investec-sentinel`** (app + its `investec-sentinel-src` workspace folder);
**kept `investec-fraud-aml`** and marked it **hands-off** (persistent memory
`do-not-touch-investec-fraud-aml`). Only one Investec app exists now.

---

## 8. Demo warm-up system (final state — no laptop dependency)

Serverless warehouses cold-start ~15-30s; a cold first click in front of the boss reads as
slow. Two layers:

**Layer 1 — server-side Databricks Jobs (primary).** One per app, schedule
`0 0 9,11,13 ? * MON-FRI` (Africa/Johannesburg) → **09:00 / 11:00 / 13:00 SAST weekdays**,
UNPAUSED. Fire regardless of any laptop.
- Capitec 904514902417610 · Nedbank 940799723574121 · Investec 222788104794952 · MCB 657733045157540
- Sentinel warm SQL: `/Workspace/Users/jason.miles@databricks.com/sentinel-warm/<bank>_warm.sql`
  (read-only reads of `<bank>_fraud_aml_gold`; API-managed, NOT bundle-managed — app untouched).
- MCB warm SQL: `src/ops/warm.sql` in the mcb repo (bundle-managed).
- Reschedule (API jobs): `databricks jobs update --json '{"job_id":<ID>,"new_settings":{"schedule":{...}}}'`
  — **job_id goes INSIDE the JSON**; `--json` forbids a positional id (this bit us once).
- Warehouse auto-stop: Sentinel 60min, MCB 240min.

**Layer 2 — laptop crontab + `prime_apps.sh`** (`/Users/jason.miles/vibe-coding-repos/__PRIME-DEMOS/`).
Hits all 4 apps' HTTP endpoints — warms warehouse **and** fills the app's in-process TTL
cache (jobs only warm the warehouse), and runs MCB's role/Genie/avatar preflight. macOS
cron only fires if the Mac is awake; the manual run is the guaranteed fallback:
`bash /Users/jason.miles/vibe-coding-repos/__PRIME-DEMOS/prime_apps.sh`

**Before any high-stakes demo:** jobs keep warehouses hot automatically; still run
`prime_apps.sh` ~1-2 min prior to also fill app caches + preflight MCB.

---

## 9. Golden rules for future changes

- **Never touch the `investec-fraud-aml` app** (deploy/edit/delete) without explicit
  re-authorization. Warming its warehouse via its job is fine.
- **Edit the `template/` first**, verify, then propagate to the 3 banks; regenerate
  `generated/` to confirm the generator still reproduces everything.
- **Preserve per-bank palettes/brand words** on propagation; scan for cross-brand leaks.
- Bind all user/DB values as SQL params; f-string only trusted config (schema/catalog).
- Independent reads → `parallel()`; near-static → `cached_fetch_all`; best-effort writes →
  `fire_and_forget`. New AI panels → consider `ai_stream`/`text_stream`.
- Loading UI → skeletons. Each app has a DEDICATED warehouse — use additive
  `update-permissions`, never `set-permissions`.
- Loop: `pytest` (38 green) → `tsc -b && npm run build` → `rsync dist → webroot` → deploy
  all 3 → verify live → commit + push all repos (Capitec → remote `public`, others → `origin`).

---

## 10. Repos & push targets
- capitec-sentinel-app → sentinel-app-capitec-bank (remote **public**)
- nedbank-sentinel-app-v2 → sentinel-app-nedbank (origin)
- investec-sentinel-app-v2 → sentinel-app-investec (origin)
- sentinel-app (unified template) → sentinel-app (origin)
- mcb-customer-360 → mcb-customer360-app (origin, branch **master**; bundle-managed)

Local dirs of note: `capitec-sentinel-app/`, `nedbank-sentinel-app-v2/`,
`investec-sentinel-app-v2/`, `sentinel-app/`, `__PRIME-DEMOS/`. The non-`-v2` Nedbank/
Investec dirs are stale — ignore them.
