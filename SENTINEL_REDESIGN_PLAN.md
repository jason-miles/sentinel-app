# Sentinel — Bold Redesign: Design Direction (for approval)

> Planning only. Nothing here is built or deployed. Execute **after** this week's demos.
> Palettes stay brand-locked per bank (Capitec red/blue, Nedbank green, Investec
> slate/gold) — driven by `brand.json`, so the redesign propagates via the generator.
> Last updated 2026-08-17.

---

## 1. The brief, pinned

**Subject:** a fraud & AML *command center* for a bank. **Audience (demo):** the CCO and
bank executives judging whether this feels like production-grade financial-crime
intelligence. **The Executive Overview's single job:** convey *"we see the whole
picture, in real time, with AI you can defend to a regulator."*

**Why the current look leaves points on the table.** It's genuinely clean — Libre Caslon
headings, Inter body, per-bank palette, dark mode. But "serif headings on a tidy SaaS
dashboard, opening with a 6-tile KPI band" is now itself a default. It's *competent*; it
isn't yet *memorable*. The product's real drama — a hidden network lighting up, a signal
pulled from noise — never shows up in the visual language.

---

## 2. Design thesis — "Signal over noise"

Everything in fraud/AML is separating the one signal from millions of benign
transactions. Make that the whole design language:

- The interface is **quiet, precise, near-monochrome** — the bank's neutral navy/ink and
  a disciplined grey scale carry 95% of the surface.
- **Colour = meaning, never decoration.** The palette's `accent` is spent *only* on
  genuine signal: a critical alert, the AI-vs-rules delta, the mule-network reveal, a
  breached SLA. When something turns the brand colour, it *matters*.
- **Numbers are the hero material.** Risk scores, ZAR amounts, case IDs, timestamps,
  false-positive rates — these are the product. Typeset them as a precision instrument.

This is subject-true (it *is* what the analyst's job is) and it differentiates from all
three AI-default looks (cream-serif-terracotta, near-black-acid, broadsheet-hairline).

---

## 3. Tokens

### Colour (deploy the existing brand palette differently — do NOT change the hexes)
- Keep each bank's `navy` / `accent` / `accent-2` exactly.
- Add a **true neutral ramp** (ink-0…ink-4) so the UI reads as a disciplined greyscale,
  with `accent` reserved for signal. Today `accent` is used fairly freely (chips, tabs,
  bullets); the redesign *pulls it back* to signal-only — the single biggest perceived-
  quality lever, and it costs nothing in brand terms.
- One new semantic token: `--signal` (= `accent`) used exclusively for "this needs a
  human's attention" so its meaning is learned within seconds of the demo.

### Type (the real risk — a deliberate, non-default pairing)
| Role | Now | Proposed | Why |
|------|-----|----------|-----|
| Display | Libre Caslon Text | **Fraunces** (variable, optical) set tight + heavy | Editorial authority without the ubiquitous Caslon/Playfair "SaaS serif" read; optical axis lets headings feel precise, not decorative |
| Body / UI | Inter | **Inter** (keep) | Excellent for dense governed data; already loaded; boring in the right way |
| Numeric / data | — | **IBM Plex Mono** for scores, amounts, IDs, timestamps | Makes the numbers a *feature*; says "instrument, not spreadsheet." This is the signature type move |

Set a real scale (not ad-hoc px): 12 / 13 / 15 / 18 / 24 / 34 / 52, weights 400/500/700,
tabular lining figures everywhere (already added). Display tracking negative at ≥34px.

### Layout concept
Executive Overview stops opening with a 6-tile grid. Instead:

```
┌───────────────────────────────────────────────────────────────┐
│  EXECUTIVE OVERVIEW                              ● Live · 14:02  │
│                                                                 │
│  R673m            ▁▂▃▅▇▆▄▃▂  ← "watch pulse": a thin live        │
│  fraud prevented   (case-volume sparkline, animates in)         │
│  this year         one commanding number = the thesis, not 6    │
│                                                                 │
├───────────────────────────────────────────────────────────────┤
│  case volume 698   FP rate 35%   past-due 12   ZAR 1.9bn  ...   │  ← KPIs demoted to a
│  (precise mono band, quiet — secondary, scannable)              │    single quiet band
├───────────────────────────────────────────────────────────────┤
│  [ Daily new alerts area ]        [ Alerts by scenario ]        │  ← charts unchanged in
│                                                                 │    structure; restyled
└───────────────────────────────────────────────────────────────┘
```

Open with the **most characteristic true thing** — one commanding metric + a live pulse —
then the precise KPI band, then the existing charts. Same data, same routes; a re-ranked
hierarchy. The other pages get the same treatment: quiet neutrals, mono numerics, accent
reserved for signal.

### Signature element — "the watch pulse"
A single thin line beneath the hero number that renders live case-volume as a sparkline
and animates in on load (respecting `prefers-reduced-motion`). It's the Sentinel's
heartbeat — literally the product watching. Appears once, on the hero, nowhere else
(spend boldness in one place). On the Alert Investigation page the same motif becomes the
"a new alert just arrived" pulse — tying the live-detection wow-moment to the identity.

---

## 4. Self-critique (did I just reach for a default?)

- **Near-black + bright accent?** No — base is the bank's own neutral navy/ink, and accent
  is *restricted*, not sprinkled. The discipline is the point.
- **Cream + serif + terracotta?** No — no cream; the serif is Fraunces used tightly, and
  colour is brand-locked.
- **Broadsheet hairlines?** Tempting (financial instrument) but that's default #3 — so I
  am **not** going hairline-dense-columns. Structure stays card-based; the "instrument"
  feeling comes from the *mono numerics*, not from rules.
- **Numbered 01/02/03 markers?** Only where content is a true sequence (Story Mode beats
  already are). Not as decoration.
- **The one risk I'm taking:** the mono-numeric type system + the accent-as-signal-only
  discipline. Justified because numbers and signal *are* this product.

---

## 5. Rollout (safe, generator-first)
1. Add fonts (Fraunces, IBM Plex Mono) to `index.html`; add neutral ramp + `--signal` to
   `template` `:root` (+ dark). Palette hexes untouched.
2. Build the hero + pulse on **Capitec first**, on a branch; screenshot; you review live.
3. Iterate to sign-off, then propagate to Nedbank + Investec, regenerate, verify per-bank
   palettes + zero cross-brand leaks (the usual guardrail).
4. Full browser QA across pages + mobile/projector breakpoints (the step there wasn't time
   for pre-demo). Deploy all 3 (Investec with your per-change authorization).

## 6. Effort & risk
- ~1 focused build session for the Capitec hero + type system; ~½ session to propagate +
  QA. Reversible (CSS + one hero component; layouts otherwise intact).
- **Do it after the Thu 20 demo**, in a clear window — never on a demo morning.

---

### Decision needed from you (post-demos)
- Green-light the **"Signal over noise"** thesis + the **Fraunces / Inter / IBM Plex Mono**
  type system? (Or steer: e.g. keep Libre Caslon, or go bolder/quieter.)
- Comfortable with **accent-as-signal-only** (pulling brand colour out of chrome)? This is
  the highest-impact change and the one most worth a conscious yes.
