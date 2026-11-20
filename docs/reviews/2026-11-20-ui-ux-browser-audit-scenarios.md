# UI/UX browser audit — scenario list (2026-11-20)

**Status:** `accepted` — session 3 checkpoint (S20/S21/S27 done; see report); resume S23–S24, P2, S60 next session  
**Plan:** [2026-11-20-ui-ux-browser-audit-cursor.md](../plans/2026-11-20-ui-ux-browser-audit-cursor.md)  
**Commit at prep:** `12df1c7` · Frontend `http://localhost:5177` · API proxy `http://localhost:8001`  
**Accounts:** `ux-audit@` (regular), `ux-audit-premium@` (premium), `ux-audit-admin@` (admin) — passwords out of repo  
**Datasets (to build during / before P0):** empty (fresh register or cleared gear), Small (~12 items), Realistic (6–10 containers, nesting 3 levels, 60–150 items), Stress (300+ items / 40+ containers via import + UI)

Legend for matrix cells: **R** = required · **S** = smoke · **—** = skip (timebox)

---

## Coverage matrix

### Priorities × directions (plan §5)

| Direction (plan §5) | Scenarios | Priority |
|---------------------|-----------|----------|
| P0.1 First run / onboarding | S01, S02 | P0 |
| P0.2 Add item speed | S03, S04, S05 | P0 |
| P0.3 Edit existing fast | S06, S07 | P0 |
| P0.4 Container detail readability | S08, S09 | P0 |
| P0.5 Weight / readiness comprehension | S10 | P0 |
| P0.6 Mobile layout 375/768 | S08, S11, S12 (+ re-verify #017) | P0 |
| P0.7 Navigation / wayfinding | S13, S14 (+ #025, #018 spot) | P0 |
| P0.8 Data-safety feel | S15, S16 | P0 |
| P1.1 Import / export | S20, S21 | P1 |
| P1.2 Catalogue | S22 (+ #006, #040) | P1 |
| P1.3 Search / filter / sort | S23 | P1 |
| P1.4 Charts / stats / viz / shopping | S24, S25 | P1 |
| P1.5 Sharing & public | S26, S27 (+ #039, #044 UI) | P1 |
| P1.6 Dark / light theme | woven into P0 + S28 | P1 |
| P1.7 i18n en/pl | woven into P0 + S29 | P1 |
| P1.8 Empty / loading / error / offline | S30, S31 | P1 |
| P1.9 Forms / validation | S32 | P1 |
| P2.1 AI chat | S40 | P2 |
| P2.2 Admin | S41 | P2 |
| P2.3 Settings / profile / 2FA | S42 (+ #016) | P2 |
| P2.4 Billing / premium | S43 | P2 |
| P2.5 PWA | S44 | P2 |
| P2.6 Micro-polish | S45 | P2 |
| Re-verify open UX issues | S50 | cross |
| Competitive parity pass | S60 | cross |

### Viewport × theme × locale (minimum)

| Scenario set | 375 | 768 | 1280+ | light | dark | pl | en |
|--------------|-----|-----|-------|-------|------|----|----|
| P0 (S01–S16) | R | R | R | R | R | R | R (main flows) |
| P1 (S20–S32) | R | S | R | R | S | S | R |
| P2 (S40–S45) | S | — | R | S | S | — | R |
| Competitive (S60) | S public share | — | R | R | — | — | R |

**Deliberately deferred / constrained:** real OAuth login, real Stripe payment, SMTP email delivery (mark `not testable` if blocked); ultrawide 2560 and landscape phone = spot only if time; concurrent two-tab edit = one scenario only (S31).

---

## Personas (task framing)

| ID | Persona | Goal |
|----|---------|------|
| P-A | New backpacker | First account → first list → understand weight |
| P-B | Phone packer | Log a bought headlamp in ≤30 s on phone |
| P-C | Trip planner | Base weight under 6 kg for weekend hike; know what to buy |
| P-D | Sharer | Send a friend a read-only list link without forcing signup |
| P-E | Migrator | Move list from Markdown / LighterPack-style CSV |
| P-F | Prepper | See which first-aid items expire soon |
| P-G | Admin | Moderate catalogue / users without breaking user tables |

---

## Scenarios

Status: `todo` until execution starts.

### P0 — core

| ID | Title | Persona | Start | Observe / measure | VP / theme / locale | Status |
|----|-------|---------|-------|-------------------|---------------------|--------|
| S01 | Guest landing → register → empty dashboard | P-A | `/` | CTA clarity; clicks to empty `/dashboard` or `/gear`; empty-state next step; starter template / import / catalogue hints | 375+1280, light+dark, pl+en | partial (login path + empty CTAs; register not timed) |
| S02 | First container + first item (cold start) | P-A | `/gear` empty | Clicks/seconds to saved item; required fields; defaults (unit/category); mobile keyboard/`inputmode`/zoom | 375+1280, light, pl | partial (sample set + 1 item; timings incomplete) |
| S03 | Add 10 items in a row from container detail | P-C | `/gear/:id` | Friction; save-and-add-next; Tab/Enter; form length (#041); timing vs LighterPack expectation | 1280, light, en | partial (1 item + form review; not 10×) |
| S04 | Add item from catalogue (≤2 clicks after search) | P-B | `/gear/:id/items/new` | Tabs (#006); global vs mine clarity; images | 375+1280, dark, en | todo |
| S05 | Phone quick-add one item ≤30 s | P-B | `/gear/:id` @375 | Thumb-zone primary action; field count; soft keyboard overlap | 375, light, pl | todo |
| S06 | Inline edit: toggle, Tab/Enter/Esc, auto-save, feedback | P-C | `/gear/:id` | Save status visible; undo; errors; #034 regression spot | 1280+375, light+dark, en | todo |
| S07 | Bulk actions presence (multi-select move/delete/status) | P-C | `/gear/:id`, `/gear/items` | Present or missing (finding if missing) | 1280, light, en | todo |
| S08 | Container detail with Realistic dataset (60+ items) | P-C | `/gear/:id` | Density, columns, category group, totals, nesting, truncation, images (#008), sticky header | 375+768+1280, light+dark, pl | partial (small BOB set; need Realistic) |
| S09 | Long names / emoji / diacritics / no-weight rows | P-C | `/gear/:id` | Truncation+tooltip; wrapping; missing weight ≠ `0` | 1280, light, pl | todo |
| S10 | Weight & readiness at a glance | P-C | `/gear/:id` + dashboard | Base/worn/consumable clarity; units/separators; readiness definition; tooltips | 1280+375, light+dark, en+pl | todo |
| S11 | Mobile chrome: sidebar off-canvas, no page H-scroll | P-B | authenticated pages | #017 re-verify; touch targets ≥24px; sticky actions | 375+390, light+dark, pl | done (#017 fixed; touch sizes spot) |
| S12 | Tablet 768 container detail + forms | P-C | `/gear/:id`, add item | Layout between phone/desktop; table vs cards | 768, light, en | todo |
| S13 | Wayfinding: breadcrumbs, highlight, Back after dialog/filter | P-A | deep `/gear/:id/items/:itemId` | Nested path; reload deep link; Back behaviour | 1280+375, light, en | todo |
| S14 | Sidebar with many containers + search (#025) | P-C | Stress / Realistic | Search works; duplicate names (#018 done spot-check) | 1280, dark, pl | todo |
| S15 | Destructive: delete item / nested container confirm copy | P-C | `/gear/:id` | What is deleted; undo/toast; no one-click loss | 1280+375, light, en | todo |
| S16 | Save feedback everywhere (create/edit/settings) | P-A | forms | User always knows saved vs dirty | 1280, dark, en | todo |

### P1 — important

| ID | Title | Persona | Start | Observe | VP / theme / locale | Status |
|----|-------|---------|-------|---------|---------------------|--------|
| S20 | Import Markdown (`example-gear.md`) + malformed file | P-E | `/gear?import=true` | Discoverability; preview; errors; summary; #004 spot | 1280+375, light, en | done (F019 name `**`; paste-only) |
| S21 | Export JSON/MD/CSV naming & units | P-E | `/gear` More actions | Content correctness; feedback; #002/#003 spot | 1280, light, en | done (F021 weak copy toast) |
| S22 | Catalogue browse/search/add + admin manage smoke | P-A/G | `/gear/catalogue` | Relevance; empty search; #009 images if present; #040 dialog | 1280+375, light, en | todo |
| S23 | Search/filter/sort on `/gear`, `/gear/items`, shopping | P-C | those routes | Placeholder; clear; URL persistence; empty results; `/` shortcut? | 1280+375, light, pl | todo |
| S24 | Visualization DnD + gear settings zones (#042) | P-C | `/gear/visualization`, `/gear/settings` | Touch alternative; empty; dark contrast | 1280+375, dark, en | todo |
| S25 | Shopping planning totals by priority/currency | P-C | `/gear/shopping` | Legibility; empty; mobile | 1280+375, light, pl | todo |
| S26 | Share tokens UI + anonymous `/shared/container/:token` | P-D | share page + guest | ≤2 clicks to link; phone public view; #044 UI | 375+1280, light, en | partial (token OK; shared list broken F001; guest/incognito TBD) |
| S27 | Public containers browse/rate/report + badge unpublish (#039) | P-D | `/gear/public` | Guest vs auth; unpublish speed | 1280+375, light, en | done (#039 fixed; F020 public items empty) |
| S28 | Theme islands: dialogs, toasts, dropdowns, charts | — | core pages | Un-themed islands; #033 palette spot | 1280, toggle live | todo |
| S29 | PL overflow stress (buttons, tabs, headers, badges) | — | main nav + forms | Truncation; mixed lang; pluralisation; formats | 375+1280, light, pl | todo |
| S30 | Empty / 404 / 403 / expired token / offline message | — | bad IDs, DevTools offline | Retry; CLS; copy quality | 1280+375, light, en | todo |
| S31 | Session expiry mid-edit + two-tab concurrent edit | — | item edit | Redirect/message; conflict behaviour | 1280, light, en | todo |
| S32 | Validation: decimals pl comma, required, unsaved navigate | — | item form | Inline errors; focus; warning | 1280+375, light, pl | todo |

### P2 — smoke

| ID | Title | Observe | Status |
|----|-------|---------|--------|
| S40 | AI chat premium gate + history (`ux-audit-premium`) | Gate for regular; streaming/error if available | todo |
| S41 | Admin dashboard tables consistency | Users/containers/items/limits/reports/subscriptions | todo |
| S42 | Settings: theme, locale, passkeys empty, 2FA setup (#016), delete account wording | End-to-end 2FA if API works; else not testable | todo |
| S43 | Billing pages + upsell dismiss persistence | No real payment; success/cancel routes | todo |
| S44 | PWA: manifest, installability, offline SW message | Smoke only | todo |
| S45 | Micro-polish: titles, focus rings, toast position mobile, action icon consistency | Spot across P0 routes | todo |

### Cross-cutting

| ID | Title | Notes | Status |
|----|-------|-------|--------|
| S50 | Re-verify issues table (plan §2) | 005, 006, 008, 016, 017, 024, 025, 039–042; spot-check done 015, 018–023, 026–031, 033–034 | todo |
| S60 | Competitive directions (plan §9) | LighterPack speed/share/totals; PackWizard packing mode; library vs list; print/PDF; differentiators discoverability | todo |

### Timed tasks (for competitive section)

| Task | Target hypothesis (🟡) | Scenario |
|------|------------------------|----------|
| First usable list with 10 named+weighted items | LighterPack ~2–3 min keyboard | S03 |
| Phone log one purchased item | ≤30 s | S05 |
| Share read-only link | ≤2 clicks after open container | S26 |
| Import example Markdown to visible containers | ≤1 min including file pick | S20 |

---

## Execution order

1. Accept this list (user).  
2. Build Small + Realistic datasets on `ux-audit@` (import + UI); leave `ux-audit-premium@` relatively clean for AI; use admin only for S41/S22 manage.  
3. Run S01→S16 (P0), updating status and capturing screenshots under `docs/reviews/assets/2026-11-ui-ux/`.  
4. S20→S32 (P1), then S40→S45 (P2 smoke).  
5. S50 re-verification + S60 competitive.  
6. Write `docs/reviews/2026-11-20-ui-ux-browser-audit.md` + issue proposals from **045**.

---

## Open prep notes

- ✅ Backend containers Up; catalogue seeded (71 items updated).  
- ✅ Audit users exist, email verified, login API OK.  
- 🟡 Demo data not yet created (will build after acceptance, as part of S01–S03 / import S20).  
- ❓ SMTP / OAuth / Stripe local config — treat as not testable when blocked.
)
