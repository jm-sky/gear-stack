# UI/UX browser audit — Gear Stack (2026-11-20)

**Status:** `in progress` (session 2 checkpoint — stop here; resume with prompt below / next chat)  
**Date:** 2026-11-20  
**Commit:** `12df1c7`  
**Plan:** [2026-11-20-ui-ux-browser-audit-cursor.md](../plans/2026-11-20-ui-ux-browser-audit-cursor.md)  
**Scenarios:** [2026-11-20-ui-ux-browser-audit-scenarios.md](2026-11-20-ui-ux-browser-audit-scenarios.md)  
**Assets:** [assets/2026-11-ui-ux/](assets/2026-11-ui-ux/) (16 PNGs; **no** 2FA secret screenshots)  
**Legend:** ✅ confirmed · 🟡 assumption · ❓ open  
**Issue proposals:** listed only — **user has not accepted** creating `docs/issues/*` yet.

---

## 1. Header / environment

| Item | Value |
|------|-------|
| Frontend | `http://localhost:5177` |
| Backend | Docker: `gear-stack-app` (host **8001**), db, redis |
| Browser | Cursor Browser MCP + CDP |
| Accounts | `ux-audit@` (regular, used); premium/admin prepared, admin UI not fully exercised |
| Dataset | Bug Out Bag (+ Fire Pouch) + Petzl + inline “Duct tape” (deleted); **Weekend hike** created; Realistic/Stress still thin |
| Viewports | 375, 768, ~1280 |
| Themes / locales | light+dark; en+pl |
| Sessions | 1 (~1.5–2 h) + 2 (~1 h) |

### Coverage

| Priority | Done / partial | Remaining |
|----------|----------------|-----------|
| P0 | S01–S03 partial, S05 partial, S06 ✅ (inline+Enter add), S08/S10/S11 partial/done, S12 partial (create @768), S15 ✅ (delete), S26 partial | S04 timed catalogue-add; S07 bulk (missing); S09 edge text; S13–S14 stress; deepen timings |
| P1 | S22 smoke, S25 empty, S26 tokens, S30 404, S42 2FA | S20–S21 import/export, S23–S24, S27–S29, S31–S32 |
| P2 | S40 AI history empty (regular), S41 admin blank as non-admin, S42 settings/2FA | billing, PWA, micro-polish depth |
| Cross | S50 largely done | S60 competitive pass to finish |

---

## 2. Executive summary (provisional after session 2)

**Top problems**

1. **F001 Shared list broken** (owner + guest) — Items 0 / empty table + wrong “Add your first item” CTA; guest also sees authenticated chrome / stale sidebar.  
2. **F012 Delete item without confirm** — row More → Delete removes immediately (**S1** data-safety).  
3. **Add-item full form still slow** (#041/#006) — though **inline editing + “Add item…” + Enter** is strong LighterPack-like path when enabled.  
4. **Base/worn/consumable not in header** (F003); chart vs header totals diverge (F007).  
5. **Unit mismatch** — Gear Settings preferred unit **g**, new-item form defaults to **kg** (F013).

**Top strengths**

1. #017 mobile fixed; #024 nested path; #025 sidebar search.  
2. Inline edit mode with bottom quick-add row.  
3. #016 2FA setup API/QR works (verified; screenshot with secret **not** kept).  
4. #042 visualization zones UI present in `/gear/settings`.  
5. Sample sets + catalogue browse; Wearable/Consumable copy; 404 PL.

**Competitor readiness (🟡):** Inline edit narrows the LighterPack gap for power users who find the toggle; share/public view and one-click share still block replacement. Finish S60 next session.

---

## 3. Findings table

| ID | Area / route | Sev | Impact | Effort | Recommendation | Screenshot | Related | Cert |
|----|--------------|-----|--------|--------|----------------|------------|---------|------|
| F001 | `/shared/container/:token` | **S1** | Shared packing list unusable | M | Fix item load; read-only empty copy; guest layout without owner chrome | [F001-…](assets/2026-11-ui-ux/F001-shared-empty-1280-dark-en.png), [guest](assets/2026-11-ui-ux/F001-shared-guest-1280-light-en.png) | #044 | ✅ |
| F012 | Item delete (row menu) | **S1** | Accidental data loss | S | Confirm dialog with item name; undo toast | — (repro: More → Delete) | S15 | ✅ |
| F002 | `/items/new` form | **S2** | Slow adds if not using inline | M | Respect settings unit; collapse advanced; save-and-add-next | [S03](assets/2026-11-ui-ux/S03-add-item-375-dark-en.png) | #041 #006 | ✅ |
| F003 | Container header stats | **S2** | Weight comprehension | M | Show base/worn/consumable + Readiness tooltip | [S08](assets/2026-11-ui-ux/S08-container-detail-1280-light-en.png) | calc V2 | ✅ |
| F005 | Share discoverability | **S2** | Sharing persona | S | One-click copy share link | [S26](assets/2026-11-ui-ux/S26-share-tokens-1280-dark-en.png) | — | ✅ |
| F013 | Unit default vs settings | **S2** | Wrong weights | S | New item unit = preferredWeightUnit from gear settings | S03 vs `/gear/settings` | — | ✅ |
| F014 | PL star rating copy | **S3** | i18n polish | S | Fix pluralisation (`Oceń 1 gwiazdką` / `2 gwiazdki` / `5 gwiazdek`) | PL container | S29 | ✅ |
| F015 | Catalogue card images | **S3** | Trust/polish | M | Broken/missing catalogue images | [S22](assets/2026-11-ui-ux/S22-catalogue-1280-light-en.png) | #009 | ✅ |
| F016 | `/admin` as non-admin | **S3** | Confusing blank | S | Redirect or 403 page, not empty document | — | S41 | 🟡 |
| F004 | List thumbnails | **S3** | Visual scan | M | Default-on or discoverable “Show Item Images” (exists on create) | S08 | #008 | ✅ |
| F006 | Relative share URL | **S3** | Copy UX | S | Absolute URL in UI | S26 | — | ✅ |
| F007 | Weight total mismatch | **S3** | Trust | M | Align header vs chart | F001/S08 | — | ✅ |
| F008 | Sample sets discoverability | **S3** | Mid-journey | S | Expose beyond empty dashboard | — | — | ✅ |
| F009 | Brand/Color a11y names | **S3** | SR | S | Labels on comboboxes | S03 | #021 | 🟡 |
| F010 | Dual sidebar toggle | **S4** | Clutter | S | One control | S11 | — | ✅ |
| F011 | Dashboard vs `/gear` empty | **S4** | Wayfinding | S | Clarify | S01 | — | 🟡 |
| F017 | Missing weight shown as `0` | **S3** | Clarity | S | Show “—” / empty, not 0 g | inline Duct tape | — | ✅ |
| F018 | Guest shared layout | **S2** | Share UX | M | Public/guest layout for token links | F001 guest | F001 | ✅ |

---

## 4. Previous findings re-verification

| Issue | Result | Evidence |
|-------|--------|----------|
| 005 nested dialog empty | **partially explained** — empty when no other nestable containers; with **Weekend hike** list shows option. Still poor empty CTA (#040). | [S50-005](assets/2026-11-ui-ux/S50-005-add-container-dialog-1280-light-en.png) |
| 006 add-existing tab | **still present** | S03 |
| 008 images on list | **still present** (default off; setting on create exists) | S08; create form checkbox |
| 016 2FA API 404 | **fixed** — QR + manual secret load | `/auth/2fa/setup` (no secret asset kept) |
| 017 mobile layout | **fixed** | S11 |
| 024 nested scanability | **fixed** | S50-all-items |
| 025 sidebar search | **fixed** | sidebar searchbox |
| 039 public unpublish | ❓ not tested | — |
| 040 add-container dialog | **still present** (no create-new in dialog) | S50-005 |
| 041 add-item layout | **still present** (full form); mitigated by inline | S03, S06 |
| 042 viz zones settings | **fixed** — Custom Visualization Zones + Add Zone | `/gear/settings` |
| done a11y UX spots | hold (#019 #020 #022 #023 #029 #027) | session 1 |

---

## 5. Quick wins (provisional)

1. Confirm dialog on item delete (F012).  
2. Fix shared view item list + guest layout (F001/F018).  
3. Wire new-item unit to gear settings (F013).  
4. One-click copy absolute share link (F005/F006).  
5. Header base/worn/consumable chips (F003).  
6. PL pluralisation for stars (F014).  
7. Empty nest dialog → “Create nested container” (#040).  
8. Missing weight as “—” not 0 (F017).

---

## 6. Competitive gap list (provisional)

| Direction | Verdict | Notes |
|-----------|---------|-------|
| LighterPack fast entry | **parity when inline ON** / behind if form-only | S06 Enter-to-add; discoverability of toggle |
| Share ≤2 clicks + public list | **behind** | F001, F005, F018 |
| Base/worn/consumable totals | **behind** | F003 |
| Nested containers | **ahead** | Fire Pouch |
| Catalogue | **ahead** capability / polish gaps | S22, F015 |
| Packing mode | **behind / n/a** | not seen |
| Images in lists | **behind** default | #008 / F004 |

---

## 7. Positive / keep

- Inline editing + “Add item…” row (Enter creates item).  
- Sample sets; sidebar search; All Items `›` path.  
- 2FA setup flow; viz zones in gear settings.  
- Mobile container layout; 16px inputs; Wearable/Consumable help text.  
- Preferred weight unit control in gear settings (once honored by forms).

---

## 8. Cross-cutting themes

1. Share/public trust (F001/F018).  
2. Destructive safety (F012).  
3. Weight truthfulness (F003/F007/F013/F017).  
4. Dual add paths (inline vs long form) — teach or default to inline.

---

## 9. Proposed issues (**not created** — awaiting user acceptance)

| Prop | Title | Type | Sev | Notes |
|------|-------|------|-----|-------|
| **045** | Shared container empty / wrong CTA | bug | S1 | F001 |
| **046** | Header base/worn/consumable | UX | S2 | F003 |
| **047** | Add-item form speed + unit from settings | UX | S2 | F002 F013 / #041 |
| **048** | One-click absolute share link | UX | S2 | F005 F006 |
| **049** | Confirm before item delete | bug/UX | S1 | F012 |
| **050** | Guest layout for share tokens | UX | S2 | F018 |
| — | #006 #008 #039 #040 | existing | — | do not duplicate; #042/#016 can close after formal QA |

---

## 10. Open questions

1. Root cause of F001 (API payload vs client filter vs store)?  
2. Accept proposals 045–050?  
3. Should inline editing default **on** for new users?  
4. Close #016 and #042 after this audit?

---

## Checkpoint — next session

1. Markdown import S20 + export S21; publish/public S27/#039.  
2. Realistic/stress data; S14 sidebar 40+.  
3. Admin as `ux-audit-admin@`; premium AI chat gate.  
4. Finish S60 competitive; mark report `done`; propose close #032.  
5. **No issue files / no commit** until user accepts.

**Env reminder:** `pnpm dev` :5177; `docker compose` from repo root (no `_` prefix); password in `/tmp/gear-stack-ux-audit/pass.txt` (not in repo).
