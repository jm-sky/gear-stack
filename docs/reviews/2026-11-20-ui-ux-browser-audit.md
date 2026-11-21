# UI/UX browser audit — Gear Stack (2026-11-20)

**Status:** `in progress` (functional fixes F001/F020/F013/F019 applied 2026-11-21 — see "Fix status"; session 3 checkpoint — S20/S21/S27 done; resume remaining P1/P2 below)  
**Date:** 2026-11-20  
**Commit:** `4fb8847` (session 3)  
**Plan:** [2026-11-20-ui-ux-browser-audit-cursor.md](../plans/2026-11-20-ui-ux-browser-audit-cursor.md)  
**Scenarios:** [2026-11-20-ui-ux-browser-audit-scenarios.md](2026-11-20-ui-ux-browser-audit-scenarios.md)  
**Assets:** [assets/2026-11-ui-ux/](assets/2026-11-ui-ux/) (25+ PNGs; **no** 2FA secret screenshots)  
**Legend:** ✅ confirmed · 🟡 assumption · ❓ open  
**Fix status:** see [§ Fix status (2026-11-21)](#fix-status-2026-11-21) below.  
**Issue proposals:** listed only — **user has not accepted** creating `docs/issues/*` yet.

---

## 1. Header / environment

| Item | Value |
|------|-------|
| Frontend | `http://localhost:5177` (restarted mid-session 3) |
| Backend | Docker: `gear-stack-app` (host **8001**), db, redis |
| Browser | Cursor Browser MCP + CDP |
| Accounts | `ux-audit@` (regular, used); premium/admin prepared, admin UI not fully exercised |
| Dataset | After MD import: **14 containers / 55 items** (BOB + Weekend hike + Samochód/Plecak/… from `example-gear.md`); Realistic denser; Stress/40+ sidebar still thin |
| Viewports | 375, 768, ~1280 |
| Themes / locales | light+dark; en+pl |
| Sessions | 1 (~1.5–2 h) + 2 (~1 h) + 3 (~1.5 h) |

### Coverage

| Priority | Done / partial | Remaining |
|----------|----------------|-----------|
| P0 | S01–S03 partial, S05 partial, S06 ✅, S08/S10/S11 partial/done, S12 partial, S15 ✅, S26 partial | S04 timed catalogue-add; S07 bulk; S09 edge text; S13–S14 stress 40+; deepen timings |
| P1 | S20 ✅, S21 ✅, S22 smoke, S25 empty, S26 tokens, S27 ✅ (#039 fixed), S30 404, S42 2FA | S23–S24, S28–S29, S31–S32 |
| P2 | S40 AI history empty (regular), S41 admin blank as non-admin, S42 settings/2FA | admin as `ux-audit-admin@`; premium AI gate; billing; PWA; micro-polish |
| Cross | S50 largely done (#039 now fixed) | S60 competitive pass to finish |

---

## 2. Executive summary (provisional after session 3)

**Top problems**

1. **F001 + F019 Shared/public item lists broken** — Items 0 + wrong “Add your first item” CTA on token share **and** `/gear/public/:id` (charts/weight still show).  
2. **F012 Delete item without confirm** — row More → Delete removes immediately (**S1** data-safety).  
3. **Add-item full form still slow** (#041/#006) — mitigated by inline + Enter when enabled.  
4. **Base/worn/consumable not in header** (F003); chart vs header totals diverge (F007; also on public detail 955 g vs chart 885 g).  
5. **Unit mismatch** — settings **g** vs new-item default **kg** (F013).

**Top strengths**

1. Markdown import (paste → preview → progress) + export MD/CSV/JSON are solid migrator paths (S20/S21).  
2. Inline edit + Enter-to-add; #017/#024/#025; #039 unpublish via Public badge (1–2 clicks).  
3. #016 2FA setup; #042 viz zones; CSV export options (BOM, columns, nested).  
4. Sample sets + catalogue; Wearable/Consumable copy.  
5. Public list browse works once published.

**Competitor readiness (🟡):** Import/export and inline edit help vs LighterPack migrators; **public/shared list views still unusable for items** — blocks share persona. Finish S23–S24, P2 smoke, S60 next.

---

## 3. Findings table

| ID | Area / route | Sev | Impact | Effort | Recommendation | Screenshot | Related | Cert |
|----|--------------|-----|--------|--------|----------------|------------|---------|------|
| F001 ✅ **fixed** | `/shared/container/:token` | **S1** | Shared packing list unusable | M | Fix item load; read-only empty copy; guest layout without owner chrome | [F001-…](assets/2026-11-ui-ux/F001-shared-empty-1280-dark-en.png), [guest](assets/2026-11-ui-ux/F001-shared-guest-1280-light-en.png) | #044 | ✅ |
| F012 ⚪ **not reproducible in code** | Item delete (row menu) | **S1** | Accidental data loss | S | Confirm dialog with item name; undo toast | — (repro: More → Delete) | S15 | ✅ |
| F002 | `/items/new` form | **S2** | Slow adds if not using inline | M | Respect settings unit; collapse advanced; save-and-add-next | [S03](assets/2026-11-ui-ux/S03-add-item-375-dark-en.png) | #041 #006 | ✅ |
| F003 | Container header stats | **S2** | Weight comprehension | M | Show base/worn/consumable + Readiness tooltip | [S08](assets/2026-11-ui-ux/S08-container-detail-1280-light-en.png) | calc V2 | ✅ |
| F005 | Share discoverability | **S2** | Sharing persona | S | One-click copy share link | [S26](assets/2026-11-ui-ux/S26-share-tokens-1280-dark-en.png) | — | ✅ |
| F013 ✅ **fixed** | Unit default vs settings | **S2** | Wrong weights | S | New item unit = preferredWeightUnit from gear settings | S03 vs `/gear/settings` | — | ✅ |
| F014 | PL star rating copy | **S3** | i18n polish | S | Fix pluralisation (`Oceń 1 gwiazdką` / `2 gwiazdki` / `5 gwiazdek`) | PL container | S29 | ✅ |
| F015 | Catalogue card images | **S3** | Trust/polish | M | Broken/missing catalogue images | [S22](assets/2026-11-ui-ux/S22-catalogue-1280-light-en.png) | #009 | ✅ |
| F016 | `/admin` as non-admin | **S3** | Confusing blank | S | Redirect or 403 page, not empty document | — | S41 | 🟡 |
| F004 | List thumbnails | **S3** | Visual scan | M | Default-on or discoverable “Show Item Images” (exists on create) | S08 | #008 | ✅ |
| F006 | Relative share URL | **S3** | Copy UX | S | Absolute URL in UI | S26 | — | ✅ |
| F007 🟠 **partly fixed** (public/shared) | Weight total mismatch | **S3** | Trust | M | Align header vs chart | F001/S08 | — | ✅ |
| F008 | Sample sets discoverability | **S3** | Mid-journey | S | Expose beyond empty dashboard | — | — | ✅ |
| F009 | Brand/Color a11y names | **S3** | SR | S | Labels on comboboxes | S03 | #021 | 🟡 |
| F010 | Dual sidebar toggle | **S4** | Clutter | S | One control | S11 | — | ✅ |
| F011 | Dashboard vs `/gear` empty | **S4** | Wayfinding | S | Clarify | S01 | — | 🟡 |
| F017 | Missing weight shown as `0` | **S3** | Clarity | S | Show “—” / empty, not 0 g | inline Duct tape | — | ✅ |
| F018 | Guest shared layout | **S2** | Share UX | M | Public/guest layout for token links | F001 guest | F001 | ✅ |
| F019 ✅ **fixed** | Import container name keeps `**md**` | **S3** | Polish / trust | S | Strip bold markers from heading names on import | [S20-result](assets/2026-11-ui-ux/S20-import-result-1280-light-en.png) | S20 | ✅ |
| F020 ✅ **fixed** | `/gear/public/:id` items empty | **S1** | Public list unusable | M | Same fix class as F001; read-only empty copy (no “Add first item”) | [S27-detail](assets/2026-11-ui-ux/S27-public-detail-1280-light-en.png) | F001 #039 | ✅ |
| F021 | Export/copy no success toast | **S4** | Feedback | S | Toast or button “Copied” after MD Copy / file export | S21 | — | 🟡 |

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
| 039 public unpublish | **fixed** — Public badge → Unpublish / Copy public link (1–2 clicks) | [S27-badge](assets/2026-11-ui-ux/S27-published-badge-1280-light-en.png); unpublish removes badge |
| 040 add-container dialog | **still present** (no create-new in dialog) | S50-005 |
| 041 add-item layout | **still present** (full form); mitigated by inline | S03, S06 |
| 042 viz zones settings | **fixed** — Custom Visualization Zones + Add Zone | `/gear/settings` |
| done a11y UX spots | hold (#019 #020 #022 #023 #029 #027) | session 1 |

---

## 5. Quick wins (provisional)

1. Confirm dialog on item delete (F012).  
2. Fix shared **and** public item lists + guest layout (F001/F018/F020) — one root cause likely.  
3. Wire new-item unit to gear settings (F013).  
4. One-click copy absolute share link (F005/F006).  
5. Header base/worn/consumable chips (F003).  
6. PL pluralisation for stars (F014).  
7. Empty nest dialog → “Create nested container” (#040).  
8. Missing weight as “—” not 0 (F017).  
9. Strip `**` from imported container names (F019).  
10. Toast / “Copied” after MD Copy and file exports (F021).

---

## 6. Competitive gap list (provisional)

| Direction | Verdict | Notes |
|-----------|---------|-------|
| LighterPack fast entry | **parity when inline ON** / behind if form-only | S06 Enter-to-add; discoverability of toggle |
| Share ≤2 clicks + public list | **behind** | Publish/unpublish OK (#039); **item table empty** F001/F020; F005/F018 |
| Import / export | **parity / ahead** | S20 paste+preview; S21 MD/CSV/JSON (CSV options strong) |
| Base/worn/consumable totals | **behind** | F003 |
| Nested containers | **ahead** | Fire Pouch |
| Catalogue | **ahead** capability / polish gaps | S22, F015 |
| Packing mode | **behind / n/a** | not seen |
| Images in lists | **behind** default | #008 / F004 |

---

## 7. Positive / keep

- Inline editing + “Add item…” row (Enter creates item).  
- Markdown import preview + progress; export MD (AI options) / CSV (columns, BOM) / JSON.  
- Public badge → Copy link / Unpublish (#039).  
- Sample sets; sidebar search; All Items `›` path.  
- 2FA setup flow; viz zones in gear settings.  
- Mobile container layout; Wearable/Consumable help text.

---

## 8. Cross-cutting themes

1. Share/public trust — empty item tables on token + public routes (F001/F018/F020).  
2. Destructive safety (F012).  
3. Weight truthfulness (F003/F007/F013/F017).  
4. Dual add paths (inline vs long form) — teach or default to inline.  
5. Import polish (raw markdown in names F019; paste-only vs file pick).

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
| **051** | Public container detail items empty + wrong CTA | bug | S1 | F020 (group with 045 if same root) |
| **052** | Strip markdown markers from import names | bug | S3 | F019 |
| — | #006 #008 #040 | existing | — | do not duplicate; #039/#042/#016 can close after formal QA |

---

## 10. Open questions

1. Root cause of F001/F020 (API payload vs client filter vs store)? Same bug for shared + public?  
2. Accept proposals 045–052?  
3. Should inline editing default **on** for new users?  
4. Close #016, #039, and #042 after this audit?

---

## Session 3 notes (S20 / S21 / S27)

| ID | Result | Evidence |
|----|--------|----------|
| S20 | ✅ Paste import from `example-gear.md` → preview → import (~11 containers); More actions discoverable; malformed keeps Import disabled | [dialog](assets/2026-11-ui-ux/S20-import-dialog-1280-light-en.png), [preview](assets/2026-11-ui-ux/S20-import-preview-1280-light-en.png), [result](assets/2026-11-ui-ux/S20-import-result-1280-light-en.png), [malformed](assets/2026-11-ui-ux/S20-import-malformed-1280-light-en.png) |
| S21 | ✅ MD export dialog + Copy; JSON `gear-export-all-YYYY-MM-DD.json`; CSV config “Will export 55 items” + BOM | [MD](assets/2026-11-ui-ux/S21-export-markdown-1280-light-en.png), [CSV](assets/2026-11-ui-ux/S21-export-csv-1280-light-en.png) |
| S27 | ✅ Publish → public list → public detail (items empty F020); #039 Unpublish works | [badge](assets/2026-11-ui-ux/S27-published-badge-1280-light-en.png), [list](assets/2026-11-ui-ux/S27-public-list-1280-light-en.png), [detail](assets/2026-11-ui-ux/S27-public-detail-1280-light-en.png) |

---

## Checkpoint — next session

1. S23–S24 search/filter + visualization; S28–S29 theme/PL; S31–S32 forms/session.  
2. Stress: S14 sidebar 40+ (import more / clone); deepen S08 on Realistic.  
3. P2: admin as `ux-audit-admin@`; premium AI chat gate; billing/PWA smoke.  
4. Finish S50 + S60; mark report `done`; propose close #032 / #039.  
5. **No issue files / no commit** until user accepts 045–052.

**Env reminder:** `pnpm dev` :5177; `docker compose` from repo root (no `_` prefix); password in `/tmp/gear-stack-ux-audit/pass.txt` (not in repo).


---

## Fix status (2026-11-21)

Root causes verified in code (not taken from the audit at face value). Branch `claude/gear-stack-audit-fixes-70xa40`. Verified by unit tests + `pnpm type-check` + full `pnpm test:run` (386 passed); **not** re-verified in a browser.

| ID | Verdict | Root cause (verified) | Fix | Regression test |
|----|---------|-----------------------|-----|-----------------|
| F001 / F020 | ✅ fixed (one root cause) | API (`/gear/shared/containers/:token`, `/gear/public/containers/:id`) returns `items` correctly. `convertV1ContainerToV2` dropped `items`, but both pages read `container.children` → always 0 items, plus the "Add your first item" CTA from `ItemsTable`'s empty slot. | New `utils/containerTree.ts` (`buildContainerTreeFromApi`) turns API `items` into `children`; both pages use it. Empty table in `publicMode` shows read-only copy (`gear.item.emptyReadOnly*`, en+pl). | `utils/containerTree.spec.ts` |
| F007 (public/shared) | 🟠 partly fixed | Header weight/readiness and `CategoryPieChart` read the **viewer's own gear store** (which doesn't hold someone else's container), so totals were wrong/inconsistent. | Pages compute weight/readiness from the fetched tree; `CategoryPieChart` got optional `items` prop and uses local accessors. | `containerTree.spec.ts` (weight 2500 g, readiness 50 %) |
| F007 (own container header vs chart) | ❓ not investigated | Not reproduced/analysed in this pass. | — | — |
| F013 | ✅ fixed | `DEFAULT_ITEM_VALUES` hard-coded `0.1 kg`; form ignored `preferredWeightUnit`. | `getDefaultItemValues(preferredUnit?)` (auto-* → base unit, default ≈100 g in that unit); used in `ItemFormPage` (new item + tab reset) and `ShoppingPlanningPage` add-item dialog. | `utils/defaultValues.spec.ts` |
| F019 | ✅ fixed | Container name regex took the whole heading incl. `**MFH**`, in both sync and async parser. | `stripInlineMarkdown()` applied to container names. | `markdownImportService.spec.ts` ("F019 regression") |
| F012 | ⚪ not a code bug | Row More → Delete → `ContainerDetailPage.handleDeleteItem` already calls `confirm(t('gear.item.deleteConfirm'))` (present since 2026-07-08; same on `ItemDetailPage`). The audit's CDP browser most likely auto-accepted the **native** dialog. | None. Remaining UX gap (native `confirm` doesn't name the item; no undo toast) stays in the UX backlog (proposal 049, downgraded S1 → S3). | — (native `confirm`; no cheap unit seam) |

**Still open / left for later (UX, per scope):** F002, F003, F005, F006, F008–F011, F014–F018 (F018 guest layout), F021, #006/#008/#040/#041. Note: public/shared items still lose `primaryImageUrl` in the V1→V2 conversion (not part of this fix).
