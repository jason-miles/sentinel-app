# Sentinel — one codebase, three banks

A single source of truth for the Sentinel Fraud & AML app, rendered per bank from a
thin brand config. Replaces the three forked repos (`sentinel-app-capitec-bank`,
`sentinel-app-nedbank`, `sentinel-app-investec`) that had drifted and cost 3× to
maintain — every fix now happens once in `template/` and is regenerated.

## Why
The three apps were ~95% identical: byte-for-byte the same detection rules, SQL,
backend, and React — differing only in **brand tokens** (colours, logo, favicon,
bank name), **schema prefix**, **product/segment terms**, **landing figures**, and the
per-bank **Genie / dashboard / warehouse IDs**. All of that is now captured in a ~40-line
`banks/<bank>.brand.json`.

## Layout
```
template/            canonical app source (backend + React + SQL + pipeline + ML).
                     Baseline values are Capitec's; the generator substitutes them.
banks/
  capitec.brand.json   per-bank config (palette, logo, schema, products, IDs, stats)
  nedbank.brand.json
  investec.brand.json
generate.py          renders generated/<bank>/ from template/ + brand.json
generated/           (git-ignored) build output per bank — deploy from here
```

## Workflow
```bash
# make a change ONCE in template/ (e.g. a new detection rule, a UI fix)
python3 generate.py --all          # regenerate all three banks
# build + deploy a bank from generated/<bank>/ exactly as before:
cd generated/nedbank/app/backend/frontend && npm ci && npm run build && cp -r dist ../webroot
databricks sync generated/nedbank/app/backend /Workspace/.../nedbank-fraud-aml-src
databricks apps deploy nedbank-fraud-aml --source-code-path /Workspace/.../nedbank-fraud-aml-src
```

Adding a **fourth** bank = one new `banks/<bank>.brand.json` + `python3 generate.py <bank>`,
then the standard deploy (create schemas/seed/pipeline/Genie/dashboard/app — see
`template/DEPLOY.md`, which applies verbatim with the bank's schema prefix).

## What the generator substitutes (Capitec baseline → target)
- schema prefix (`capitec_fraud_aml` → `<bank>_fraud_aml`), bundle + app names
- legal name, goAML reporting entity, demo email domain
- palette hexes (light + dark), graph-node + chart colours
- product/segment terms + device-id prefix
- Genie space / dashboard / warehouse IDs, app URL
- brand display name / key (done last, broadest)

## Verified
The generator was validated by rendering Nedbank + Investec and confirming: correct
schema/brand/palette, **zero Capitec leakage**, clean `tsc` + `vite build`, and 34/34
backend tests passing on the generated output — i.e. it reproduces the hand-built,
deployed apps.

## Live apps (deployed from the pre-consolidation builds; identical feature set)
- Capitec:  https://capitec-fraud-aml-7474654808133980.aws.databricksapps.com
- Nedbank:  https://nedbank-fraud-aml-7474654808133980.aws.databricksapps.com
- Investec: https://investec-fraud-aml-7474654808133980.aws.databricksapps.com

All three carry: 10 detection families, the three WOW scenarios (mule network →
goAML STR → gaming-typology sweep), in-app auto-play **Story Mode**, the **Impossible
Travel world map**, the **⚡ live-transaction** beat, a real UC-registered MLflow model,
Unity Catalog governance + RLS, and per-bank branding.
