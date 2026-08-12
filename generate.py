#!/usr/bin/env python3
"""Sentinel — single-codebase bank generator.

Renders a fully-branded, deployable app for one bank from:
  - template/         the canonical source (currently the Capitec baseline)
  - banks/<bank>.brand.json   the per-bank config

into generated/<bank>/. The template's Capitec baseline values are the substitution
SOURCE; the target brand.json supplies the substitution TARGET. Because the three
apps are ~95% identical (verified), the entire per-bank surface is: schema prefix,
brand words, palette hexes, product/segment terms, logo mark, landing stats, and the
Genie/dashboard/warehouse IDs — all captured in brand.json.

Usage:
  python3 generate.py capitec        # render one bank
  python3 generate.py --all          # render all banks in banks/

This replaces maintaining three forked repos: fix once in template/, regenerate.
"""
import json, os, re, shutil, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(ROOT, "template")
BANKS = os.path.join(ROOT, "banks")
OUT = os.path.join(ROOT, "generated")

# The template baseline is Capitec — its values are what we substitute FROM.
BASE = json.load(open(os.path.join(BANKS, "capitec.brand.json")))

SKIP_DIRS = {".git", ".venv", "node_modules", "dist", "webroot", "__pycache__",
             ".pytest_cache", ".databricks"}
TEXT_EXT = {".ts", ".tsx", ".css", ".html", ".py", ".sql", ".yml", ".yaml",
            ".json", ".md", ".svg", ".sh"}


def build_replacements(target: dict) -> list:
    """Ordered (from, to) string replacements: capitec-baseline -> target-bank.
    Order matters — do longer/more-specific strings first."""
    b, bp = BASE, BASE["palette"]
    t, tp = target, target["palette"]
    R = []
    # schema / infra identifiers
    R += [(b["schema_prefix"], t["schema_prefix"]),
          (b["bundle_name"], t["bundle_name"]),
          (b["app_name"], t["app_name"]),
          (b["legal_name"], t["legal_name"]),
          (b["goaml_entity_id"], t["goaml_entity_id"]),
          (b["email_domain"], t["email_domain"])]
    # IDs
    for k in ("warehouse_id", "genie_space", "dashboard_id", "app_url"):
        if b["ids"].get(k) and t["ids"].get(k):
            R.append((b["ids"][k], t["ids"][k]))
    # product/segment terms (longer first)
    for k in ("transact", "entry", "active", "plus", "app", "device_prefix"):
        if b["products"].get(k) and t["products"].get(k):
            R.append((b["products"][k], t["products"][k]))
    # palette hexes (case-insensitive handled by doing lower + upper)
    for k in bp:
        if bp.get(k) and tp.get(k) and bp[k] != tp[k]:
            R.append((bp[k], tp[k]))
            R.append((bp[k].upper(), tp[k].upper()))
    # brand display name LAST (broadest) — but only whole-word-ish to avoid overreach
    R.append(("Capitec", t["display_name"]))
    R.append(("capitec", t["bank_key"]))
    R.append(("CAPITEC", t["bank_key"].upper()))
    return R


def render(bank: str):
    target = json.load(open(os.path.join(BANKS, f"{bank}.brand.json")))
    reps = build_replacements(target)
    dst = os.path.join(OUT, bank)
    if os.path.exists(dst):
        shutil.rmtree(dst)
    for dirpath, dirnames, files in os.walk(TEMPLATE):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        rel = os.path.relpath(dirpath, TEMPLATE)
        os.makedirs(os.path.join(dst, rel), exist_ok=True)
        for f in files:
            if f == ".DS_Store":
                continue
            src_f = os.path.join(dirpath, f)
            out_f = os.path.join(dst, rel, f)
            ext = os.path.splitext(f)[1]
            if ext in TEXT_EXT:
                s = open(src_f, encoding="utf-8", errors="replace").read()
                for a, z in reps:
                    s = s.replace(a, z)
                open(out_f, "w", encoding="utf-8").write(s)
            else:
                shutil.copy2(src_f, out_f)
    # write the resolved brand.json into the generated app for reference
    json.dump(target, open(os.path.join(dst, "brand.resolved.json"), "w"), indent=2)
    print(f"✓ generated/{bank}  ({sum(len(files) for _,_,files in os.walk(dst))} files)")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(__doc__); sys.exit(1)
    banks = ([f[:-11] for f in os.listdir(BANKS) if f.endswith(".brand.json")]
             if args[0] == "--all" else args)
    for bank in banks:
        render(bank)
