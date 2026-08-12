# Capitec Sentinel — Guided Demo Script (click-by-click)

A tight ~12-minute run that lands the three "wow" beats for a **Capitec compliance
audience** (MLRO / CCO / financial-crime analysts). Every value below is real, live
data — no slides needed; the app carries it.

- **Live app:** https://capitec-fraud-aml-7474654808133980.aws.databricksapps.com
- **Arc:** detect → document → anticipate (Scenario A → B → C)
- **All data is synthetic** ("DEMO DATA — 100% SYNTHETIC"); names/IDs are fabricated.
- Nedbank and Investec builds run the identical flow on their own isolated data —
  swap the URL and the branding; the case IDs and beats are the same.

> Pre-flight (2 min before): open the app once so the SQL warehouse is warm; confirm
> the landing page shows the Capitec hero. Set the "View As" persona to an AML
> Transaction Monitoring analyst (e.g. Thandeka Nkosi).

---

## 0 · Landing (30 sec) — set the frame
**Do:** open the app.
**Say:** "This is Sentinel — a fraud & AML copilot built entirely on Databricks on AWS,
the estate Capitec already runs. One governed Lakehouse: detection, investigation,
regulator-ready filing, and analytics."
**Point at the stat band:** R673m+ fraud prevented · 26M Global One clients · 15k card
payments/min · FIC · FICA · SARB PA · Unity Catalog · POPIA.

---

## 1 · Executive Overview (90 sec) — the CCO view
**Do:** click **Executive Dashboard**.
**Show, in order:**
- KPI tiles — **695 cases**, **false-positive rate 35.4%**, past-due alerts, **ZAR
  1,911m** transaction value monitored, avg 4.1 investigation hours.
- **Alerts by Scenario** bar + **New Alerts per Day** trend (141 days of history).
- **Case Resolution Flow** Sankey (scenario → team → status) and the **Team
  Performance** table (cases / closed / past-due / avg hours per team).
**Say:** "Every tile is live off the gold marts — the CCO sees the whole programme,
governed and lineage-tracked, without a data pull."

---

## 2 · WOW-A — the hidden mule network (4 min) — DETECT
The killer beat: a "boring" alert becomes a 7-account syndicate.

**Do:** go to **Alert Investigation** → open **CASE-90001** (Lerato Sithole, "Cash
Structuring Detection").
**Say:** "An analyst picks up what looks like a minor alert — a few cash deposits."
**Show on the case:**
- **Flagged transactions:** 3 sub-threshold cash deposits (~R20.5k–24.5k, each **just
  under the R25,000 CTR** limit) — textbook structuring.
- **Rules Score 88 vs AI Risk (✦) 85** — the model agrees this is high-risk.
- **Case notes** already show the analyst's trail; **Grounded Policy & Typology**
  cites the bank's own CTR/structuring policy + the FATF mule-network typology.

**Do:** click **Explore Network →** (Graph Explorer), search **Motaung**.
**Say:** "Entity resolution is the reveal. This one account shares a **device
fingerprint, IP, and residential address** with six others — all opened within a
3-week window. Each receives sub-threshold cash and forwards ~90% within 48h to a
single aggregator, **Kabelo Motaung (CASE-90002)**, which remits **R260k cross-border
SWIFT** to a Mauritius shell."
**The line that lands:** "Three of these sibling accounts were previously alerted and
**closed as false positives in isolation**. That's the exact failure mode of a
siloed rules engine — Sentinel sees the network."

**Fires:** structuring on 7 mules + rapid-movement on the aggregator + the graph.

---

## 3 · WOW-B — STR drafted in 90 seconds (3 min) — DOCUMENT
**Do:** on CASE-90001 (or CASE-90002), click **Proceed to SAR Filing**.
**Do:** click **Run multi-agent orchestration** (or it auto-runs).
**Show:**
- **Auto-gathered evidence pack** (transactions, counterparties, watchlist hits,
  pKYC band, adverse media, policy refs) — assembled with zero analyst effort.
- **Multi-agent trace:** transaction-analysis, adverse-media, and **policy** agents
  each return a finding; the **supervisor** synthesises a **FIC-format STR narrative**.
- **Grounded citations:** the narrative cites retrieved adverse-media articles **and**
  the bank AML policy / FATF typology guides (vector search over governed tables).
- Click **Download goAML XML** → point at **✓ goAML schema valid (12/12)** — "a real
  structured STR for the Financial Intelligence Centre, filed as **Capitec Bank
  Limited**, not just a PDF."
**The beat for compliance:** ask the app "why structuring, not a legitimate
cash-intensive business?" — the answer is evidence-cited, including the
**actual-vs-declared turnover** (the client's throughput runs many times the turnover
they declared at KYC).
**Say:** "SAR drafting is 2–6 hours of analyst time in real life. This is minutes, and
every claim traces to source in Unity Catalog — audit-defensible by construction."

---

## 4 · WOW-C — retrospective typology sweep (2.5 min) — ANTICIPATE
Flip from reactive to proactive.

**Do:** go to **Ask Sentinel** (Genie) and ask, or open the **Compliance → typology**
surface: *"A new FATF typology on third-party payment processors layering through
gaming merchants just dropped — do we have exposure?"*
**Show:** the sweep surfaces **2 accounts** — **Werner Pretorius** and **Fatima
Ismail** — each with ~60 gaming/TPP card debits matched by near-equal "winnings"
credits (net ≈ zero), and crucially **never_alerted = true**: they never tripped a
single monitoring rule.
**Say:** "This isn't a chatbot on a case tool. The analyst describes a brand-new
typology in plain English and Sentinel finds exposure that no existing rule would
catch — proactive risk discovery."

---

## 5 · Governance & AI trust (1 min) — the question compliance always asks
**Do:** Compliance → **Model Governance** tab.
**Show:** the registered **Unity Catalog model** `sar_propensity_gbt`, a real MLflow
GradientBoostedTrees model — **ROC-AUC 0.708**, and **~42% fewer false positives at an
equal alert budget** (26 vs 45 FPs) vs the rules-only baseline. Then the **drift
monitor**: features tracked, all stable — "ongoing model validation, the SARB
model-risk-management answer, built in."
**Say:** "Model, features, lineage, and every agent tool-call are governed by one Unity
Catalog plane — the substrate Capitec's responsible-AI framework needs."

---

## Director's cheat-sheet (planted IDs)
| Beat | Open | Subject | What to point at |
|------|------|---------|------------------|
| A entry | CASE-90001 | Lerato Sithole | 3 sub-threshold cash-ins; AI risk 85 vs rules 88 |
| A network | Graph "Motaung" / CASE-90002 | Kabelo Motaung | 7 mules, shared device/IP/addr, R260k SWIFT out |
| A killer line | (alert_feedback) | 3 sibling mules | previously closed as false positives |
| B | SAR Filing on A | — | multi-agent trace, cited STR, goAML 12/12 valid |
| C | Ask Sentinel / typology-sweep | Werner Pretorius, Fatima Ismail | ~60 gaming txns, net≈0, never_alerted |
| Governance | Compliance → Model | sar_propensity_gbt v-latest | AUC 0.708, ~42% fewer FPs, drift stable |

**If a warehouse is cold** the first click may take ~10s — open the app a couple of
minutes before you present so it's warm.
