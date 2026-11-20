# Plan: hands-on UI/UX browser audit (for Cursor)

**Status:** `planned`
**Created:** 2026-11-20
**Executor:** Cursor (AI agent with a browser tool; Cursor Browser MCP primary, Playwright as fallback)
**Output:** [docs/reviews/2026-11-XX-ui-ux-browser-audit.md](../reviews/README.md) (replace `XX` with the run day) + screenshots + proposed issues
**Legend:** ✅ confirmed (read in repo) · 🟡 assumption (not verified) · ❓ open

---

## 1. Goal and success criteria

**Goal.** Find what makes Gear Stack uncomfortable, hard to read or unpolished in real use, and judge whether it can be an attractive replacement for competing gear/packing apps (see section 9). This is an **audit, not an implementation**: the result is evidence-backed findings and recommendations.

**This plan sets** directions, priorities, constraints and output format. **Cursor designs** the concrete test scenarios (section 8).

**Success criteria**

1. All P0 areas covered with at least 2 viewports (375 and 1280+) and both themes; P1 covered at least at desktop + mobile; P2 at least a smoke pass.
2. Each finding is reproducible from its description (steps, viewport, theme, locale, route) and has a screenshot.
3. Previous findings (section 2) are explicitly re-verified: fixed / still present / regressed.
4. A prioritised list of quick wins and a competitive gap list exist.
5. Actionable findings are proposed as issues in the `docs/issues` format (not created without approval, see section 12).

## 2. Context: what is already known (verify, do not re-report blindly)

Prior inputs (read them first):

- [reviews/2026-07-06-ux.md](../reviews/2026-07-06-ux.md) — UX session 1 (2026-07-15, desktop 1920x1080 + mobile 375x667). Produced issues #017-#031, #033.
- [reviews/UX_REVIEW.md](../reviews/UX_REVIEW.md) — partial review from 2025-01-20 (old; several items already fixed: search placeholder, colour picker wrap).
- [issues/2026-07-15--032--ux-review-phase-2.md](../issues/2026-07-15--032--ux-review-phase-2.md) — **phase 2 checklist of areas not covered** (import/export, destructive dialogs, extended auth, admin, AI, stats, billing, shopping list, public containers, profile, 404, PWA/offline, keyboard-only, focus traps, tablet 768). This audit **absorbs and completes phase 2**; when done, issue #032 can be closed.
- [features/FEATURE-022-accessibility.md](../features/FEATURE-022-accessibility.md) — a11y work in progress; only manual tests remain (tooltips, aria-label, semantics done).
- [research/LIGHTERPACK_COMPARISON.md](../research/LIGHTERPACK_COMPARISON.md), [research/LIGHTERPACK_IMPROVEMENTS_TASKS.md](../research/LIGHTERPACK_IMPROVEMENTS_TASKS.md), [research/features-comparison-and-plans.md](../research/features-comparison-and-plans.md) — existing competitive thinking (only LighterPack is covered in depth).
- [research/2026-07-23-item-form-layout.md](../research/2026-07-23-item-form-layout.md), [plans/2026-07-15-inline-editing-ux-plan.md](2026-07-15-inline-editing-ux-plan.md) — item form layout research and inline-editing plan (done).
- [ROADMAP.md](../ROADMAP.md), [FEATURES.md](../../FEATURES.md) — what exists / is planned.

**Status of open UX issues to re-verify** (statuses from [issues/README.md](../issues/README.md) at plan time):

| Issue | Topic | Status at plan time | What to verify |
|-------|-------|--------------------|----------------|
| 005 | nested container dialog empty | `todo` | still reproducible? |
| 006 | add-existing-item tab | `todo` | still 2 tabs only? |
| 008 | item images missing on list | `todo` | thumbnails in table/cards |
| 016 | 2FA setup API 404 | `verification needed` | setup flow works end to end |
| 017 | container detail mobile layout (was HIGH) | `verification needed` | 375 and 768 px, sidebar off-canvas |
| 024 | All items nested scanability | `verification needed` | parent context readable |
| 025 | sidebar container search | `verification needed` | search works with 30+ containers |
| 039-042 | public badge unpublish, add-container dialog, add-item layout, visualization zones in settings | `todo` | confirm gaps, assess severity |
| 015, 018-023, 026-031, 033-034 | fixed UX/a11y items | `done` | spot-check for regressions only |

Report each as **fixed / still present / regressed / not testable**. Do not log "done" issues as new findings unless regressed.

## 3. Environment setup (local only)

Facts (✅ from [CLAUDE.md](../../CLAUDE.md), [docs/deployment/local-development.md](../deployment/local-development.md), `.env`):

- Frontend: `pnpm dev` from the repo root. Port from `VITE_PORT` (`.env` currently `5176`; the 2026-07-15 session saw `5177`, so check the Vite output).
- Backend: `docker compose up -d` from the **repo root** (Compose V2, not `docker-compose`). API at `http://localhost:8000`, Vite proxies `/api`. Auto-reload for Python; restart only on `.env`/dependency changes.
- **Docker underscore rule:** if the project directory name starts with `_`, do **not** run any `docker`/`docker compose` command (production server dev dir). Check `pwd` first. In that case stop and ask the user for a running backend.
- Never test against production URLs or production data.

Test accounts (create via CLI, container `gear-stack-app`):

```bash
# regular user (use --no-input; password min requirements: use a strong one)
docker exec gear-stack-app python -m cli users create --no-input \
  --email ux-audit@example.com --name "UX Audit" --password "<strong-pass>" --role user
# premium user (AI chat, billing gates, premium limits)
docker exec gear-stack-app python -m cli users create --no-input \
  --email ux-audit-premium@example.com --name "UX Audit Premium" --password "<strong-pass>" --premium
# admin (admin panel, catalogue management)
docker exec gear-stack-app python -m cli users create --no-input \
  --email ux-audit-admin@example.com --name "UX Audit Admin" --password "<strong-pass>" --role admin
```

- ✅ `users create` supports `--email --name --password --role --admin --owner --premium --no-input`. The exact valid `--role` values and password policy: run `docker exec gear-stack-app python -m cli users create --help` first.
- ✅ Existing E2E user from tests: `e2e-test@example.com` (password from `E2E_TEST_USER_PASSWORD` env / `tests/e2e/fixtures/auth.ts`) — can be reused if present.
- Do not put passwords in the report or commit them.
- Global catalogue: ✅ `docker exec gear-stack-app python -m cli db seed catalogue` (seeds `backend/app/seeders/catalogue_items.json`; needs an owner/admin user to exist first). Undo: `db seed-remove catalogue`.
- Email flows (verify email, forgot password): 🟡 may depend on SMTP config; `python -m cli test email` exists. If emails cannot be delivered, mark flows as "not testable" rather than guessing.
- OAuth providers / reCAPTCHA / Stripe: 🟡 likely not configured locally; verify button visibility logic only (#013, #014), do not attempt real provider logins.

### 3.1 Demo data (❓ no ready-made demo seed for user gear)

✅ Only the global catalogue seeder exists; there is **no seed for user containers/items**. ❓ Whether a demo mode exists is not confirmed. Cursor must therefore **prepare its own realistic dataset** via the UI and/or the import feature (also a UX test of import):

- Sample files: `docs/examples/example-gear.md`, `docs/examples/example-gear-formatted.md` (Markdown import).
- Build these datasets (suggested; adapt freely):
  - **Empty account** (first-run experience, zero state everywhere).
  - **Small**: 1 container (e.g. "Weekend hike"), ~12 items across 4 categories.
  - **Realistic**: 6-10 containers, nesting 3 levels deep (e.g. Bug-out bag > Medical kit > Pouch), 60-150 items, mixed statuses (owned/missing/toBuy), priorities, weights from 2 g to 12 kg (g/kg/oz/lb), expiration dates (past / soon / far), prices in several currencies, some items with images, long names (60+ chars), long Polish names, emoji/diacritics, duplicate container names, items with no weight.
  - **Stress**: 300+ items in one container (scroll, table performance, pagination), 40+ containers (sidebar).
- Keep audit data under a clearly named test account; do not touch other users' data.

## 4. Page map (✅ from `src/router` and module `routes.ts`)

Layouts: `authenticated` (sidebar + top bar), `public`, guest (auth pages: no explicit `layout` meta in `auth/config/routes.ts`, 🟡 resolved as guest layout by the layout resolver). Note: about/cookies/privacy/terms/contact are declared with `layout: 'authenticated'` (🟡 check how they look for logged-out visitors). Landing `/` has no layout meta (own page).

| Area | Route | Layout / guard | Notes |
|------|-------|----------------|-------|
| Landing | `/` | none (own) | guest vs logged-in CTA |
| Static | `/about`, `/cookies`, `/privacy`, `/terms`, `/contact` | authenticated layout meta | long text readability |
| 404 | any unknown path | public | |
| Auth | `/auth/login`, `/auth/register`, `/auth/forgot-password`, `/auth/reset-password`, `/auth/change-password`, `/auth/2fa/setup` (auth), `/auth/2fa/verify`, `/auth/verify-email`, `/auth/callback/:provider` | guest | passkeys/OAuth buttons |
| Dashboard | `/dashboard` | authenticated | stats, premium upsell |
| Gear list | `/gear` (`?import=true` opens import) | authenticated | search, pagination, favourites, More actions (import/export) |
| Create container | `/gear/new` | authenticated | colour picker, images |
| Container detail | `/gear/:id` | authenticated | table, stats, inline editing, nesting |
| Edit container | `/gear/:id/edit` | authenticated | |
| Share tokens | `/gear/:id/share-tokens` | authenticated | (#044 backend fixed; check UI) |
| Item new/detail/edit | `/gear/:containerId/items/new`, `/gear/:containerId/items/:itemId`, `.../edit` | authenticated | add item tabs: New / From catalogue |
| All items | `/gear/items` | authenticated | cross-container table, filters |
| Shopping planning | `/gear/shopping` | authenticated | toBuy list, prices, totals |
| Visualization | `/gear/visualization` | authenticated | DnD zones / placements |
| Gear settings | `/gear/settings` | authenticated | units, defaults, visualization |
| Public containers | `/gear/public`, `/gear/public/:id`, `/gear/public/:containerId/items/:itemId` | authenticated layout | browse, rating, reporting |
| Shared via token | `/shared/container/:token` | authenticated layout meta | 🟡 test logged out too |
| Catalogue | `/gear/catalogue`, `/gear/catalogue/:id` | authenticated | browse/search/add to container |
| Catalogue admin | `/gear/catalogue/manage`, `/gear/catalogue/new`, `/gear/catalogue/:id/edit` | admin | |
| AI | `/ai/history` (+ chat UI/panel, 🟡 locate in app) | authenticated, premium-gated 🟡 | |
| Billing | `/billing`, `/billing/success`, `/billing/cancel` | authenticated | no real payments |
| Profile | `/profile`, `/profile/edit`, `/users/:userId/public` | authenticated | |
| Settings | `/settings` | authenticated (no layout meta, 🟡 check) | theme, locale, security, passkeys, 2FA, delete account |
| Admin | `/admin`, `/admin/users`, `/admin/containers`, `/admin/items`, `/admin/limits`, `/admin/reports`, `/admin/subscriptions` | admin | |

Cursor: confirm the page map against the live nav (sidebar + top bar) and note any page reachable by URL but not by navigation (orphans) or the reverse.

## 5. Priorities

Time shown in section 13. Order of execution: P0, then P1, then P2.

### P0 — core flows and comprehension (most value, do first)

The question for each: *can a new, impatient, mobile user get this done fast and understand the screen without help?*

1. **First run / onboarding**: landing -> register -> empty dashboard -> first container -> first item. Count clicks and decisions. Is the next step always obvious? Is there a starter template / example import / catalogue suggestion in empty states?
2. **Add item speed**: both from container detail and from `/gear/new` item form. Minimum fields to save? Keyboard flow (Tab/Enter, Enter-to-save, "save and add next")? Defaults for unit/category/currency? Form length and grouping (see #041 and the item-form research). Add 10 items in a row and measure friction. Mobile: keyboard type for numeric fields (🟡 `inputmode`), no zoom-on-focus (inputs >= 16 px).
3. **Edit existing items fast**: inline editing (toggle, Tab/Enter/Esc, auto-save, error and saving feedback, undo) vs full edit page. Bulk actions (multi-select, move, delete, status change) — present or missing?
4. **Container detail readability**: table density, which columns visible by default, scanability of 60+ items, grouping by category, totals row, weight-by-category summary, nested container presentation, long names truncation + tooltip, images in rows (#008), sticky header/summary, sort/filter discoverability.
5. **Weight and readiness comprehension**: can a user tell at a glance total / base / worn / consumable weight, what "readiness" means, what counts into which number? Are units and thousands separators consistent between table, cards, charts, export? Are definitions explained (tooltips/help)?
6. **Mobile layout (375 / 390 / 414 and 768)**: sidebar off-canvas behaviour (#017), table behaviour (horizontal scroll vs cards), sticky actions, header action overflow, bottom-reachable primary actions (thumb zone), touch targets >= 24x24 CSS px (WCAG 2.2 AA 2.5.8) and ideally 44 px, no horizontal page scroll, safe-area/keyboard overlap on forms.
7. **Navigation and wayfinding**: sidebar vs top bar, breadcrumbs/back button, current location highlight, nested container paths, 30+ containers (#025), duplicate names (#018), deep links and reload on each page, browser Back behaviour after dialogs/filters.
8. **Data-safety feel**: destructive actions (delete container/item/all/account) — confirmation copy, what exactly will be deleted (nested?), undo/toast, no accidental one-click loss. Save feedback everywhere (user must always know whether it saved).

### P1 — important features and system-wide quality

1. **Import / export** (JSON, Markdown, CSV; `/gear?import=true`): discoverability, preview before import, error messages for malformed files, duplicates handling, progress, result summary; export naming and content (weights/prices/units). Cross-check #002-#004.
2. **Catalogue** (browse, search, filters, add to container, images #009): result relevance, empty search, loading, adding in <= 2 clicks, clarity of "global catalogue" vs "my items" (#006, #040).
3. **Search, filter, sort** everywhere (`/gear`, `/gear/items`, sidebar, catalogue, shopping): placeholder text, clear button, persistence in URL (query params), result count, empty result state, keyboard shortcut (🟡 e.g. `/`).
4. **Charts / stats / visualization / shopping planning**: legibility, colour-blind safety, labels not colour-only, tooltips on touch, empty/low-data behaviour, units, long category names, dark mode contrast, performance with large data; shopping total by priority/currency.
5. **Sharing & public**: share tokens UI, public badge and quick unpublish (#039), public container page as seen by an anonymous visitor (this is the "shareable list link" use-case — see section 9), rating/reporting UX, public profile.
6. **Dark / light theme**: contrast of text, borders, muted text, charts, badges (status/priority colours), focus rings; no un-themed islands (dialogs, toasts, dropdowns, tooltips, image placeholders); #033 palette consistency.
7. **i18n en/pl**: text overflow and truncation in buttons, tabs, table headers, badges, sidebar; untranslated strings / mixed languages; pluralisation (1/2/5 items in Polish), date/number/currency formats per locale, locale switch persistence and no layout jump.
8. **Empty / loading / error / offline states** on every list and detail page: skeletons vs spinners, layout shift (CLS), error retry, 404 for missing container/item IDs, 403 for another user's container, expired share token, session expiry mid-edit, 5xx / rate limit messages.
9. **Forms and validation generally**: inline errors, required markers, error summary focus, number inputs (comma vs dot decimals in pl), paste behaviour, max lengths, unsaved-changes warning on navigation.

### P2 — everything else (smoke pass, deeper only if time remains)

1. **AI chat** (premium gate, loading/streaming states, error states, context controls, history page, copy/export prompt features).
2. **Admin** (dashboard, users, containers, items, limits, reports, subscriptions, catalogue manage): table patterns consistent with user-facing tables, destructive guards.
3. **Settings / profile / account**: theme, locale, units, 2FA setup (#016), passkeys empty state, change password, delete account flow wording.
4. **Billing / premium upsell**: banner frequency and dismiss persistence, plan comparison clarity, success/cancel pages (no real payment).
5. **PWA**: install prompt, manifest/icons, offline behaviour (what works? what message?), update prompt after new version, service worker caching stale UI.
6. **Micro-polish**: favicon/page titles per route, hover/focus/active states, transitions, toasts (duration, stacking, position on mobile), icon consistency (action icons are centralised in `actionIcons.ts`, check for deviations), tooltip behaviour on touch, scrollbars, text selection, cursor styles, image loading/placeholder/broken image, long-word wrapping, print stylesheet (🟡 packing list printing).

## 6. Viewports, themes, locales

| Dimension | Values |
|-----------|--------|
| Phone | 375x667 (min), 390x844, 414x896; landscape 667x375 spot-check |
| Tablet | 768x1024 (and 1024x768) |
| Desktop | 1280x800, 1440x900, 1920x1080; one ultrawide 2560 spot-check for max-width/line length |
| Theme | light, dark, and "system" follow (switch live without reload) |
| Locale | en, pl (long Polish strings are the overflow stress test) |
| Other | browser zoom 200% (WCAG reflow 320 CSS px), text-size increase, `prefers-reduced-motion` (🟡), slow network throttle (Fast 3G), keyboard-only |

Not every cell of the matrix is required: P0 = {375, 768, 1280+} x {light, dark} x {en, pl at least on the main flows}. Record the combination in every finding.

## 7. Heuristics and checklist to apply

- **Nielsen's 10**: visibility of status, match with real world (gear vocabulary: base weight, worn, consumable), user control/undo, consistency, error prevention, recognition over recall, flexibility/shortcuts, minimalist design, error recovery, help/docs.
- **WCAG 2.2 AA basics**: contrast 4.5:1 text / 3:1 UI and large text; focus visible and not obscured by sticky bars (2.4.11); target size min 24 px (2.5.8); text resize/reflow; labels and accessible names (placeholder is not a label); no colour-only meaning (status, priority, charts); keyboard operability and no traps; dialog focus trap and return focus; heading hierarchy and landmarks; `lang` attribute follows locale; drag-and-drop has a non-drag alternative (2.5.7); consistent help/redundant entry (3.2.6/3.3.7).
- **Consistency with shadcn-vue/Tailwind**: spacing scale, button variants/sizes, radius, one pattern per concern (dialogs vs sheets vs pages; toasts; tables; badges), no custom one-off styles. Icons from the central map.
- **Touch**: size, spacing between adjacent targets, hover-only affordances (tooltips as sole info), swipe/long-press alternatives, no accidental taps near destructive actions.
- **Typography and density**: base font size >= 14-16 px on mobile, line length 45-80 characters on text pages, hierarchy (title/section/meta), tabular numerals for weights/prices (🟡 `tabular-nums`), muted text contrast, row height and density options.
- **Numbers**: weight formatting (g vs kg thresholds, oz/lb, thousands separator, decimals), alignment (right-aligned numeric columns), price + currency symbol/position per locale, rounding consistency between table totals and charts and exports, zero/missing weight shown clearly (not as 0).
- **Perceived performance**: first paint, skeletons, layout shift, long lists (virtualisation or pagination), image lazy-loading, input lag on 300+ items (note numbers, no deep profiling — that belongs to the performance reviews).
- **Copy**: clarity, tone consistency, no dev notes in production UI, consistent terminology ("container" vs "list/bag/kit", "catalogue" vs "catalog", "item" vs "gear").

## 8. Execution method (mandatory order)

1. **Read** section 2 documents (time-box: 20 min). Do not start clicking before this.
2. **Set up** environment and data (section 3). Record versions/ports/commit (`git rev-parse --short HEAD`) at the top of the report.
3. **Write the scenario list first.** Create `docs/reviews/2026-11-XX-ui-ux-browser-audit-scenarios.md` (or a "Scenarios" section at the top of the report) **before executing**. Each scenario: ID, priority (P0/P1/P2), persona/goal, start route, steps (high level), what to observe, viewports/themes/locales, status (`todo/done/blocked`). Requirements for the list:
   - Covers every P0 and P1 direction in section 5 (map scenario IDs to directions; show a coverage matrix; flag any direction deliberately skipped and why).
   - Includes **task-based scenarios with a persona**, e.g. "I am packing for a 3-day hike tomorrow evening and want my base weight under 6 kg", "I just bought a headlamp and want to log it in 30 seconds on my phone", "I want to share my list with a friend", "I want to know what to buy before the trip", "I want to know which first-aid items expire soon", "I want to move my EDC list from a spreadsheet/LighterPack".
   - Includes negative/edge scenarios (empty, very long text, 300 items, invalid import, slow network, session expiry, other user's resource, concurrent edit in two tabs).
   - Includes at least a few time-boxed task timings (clicks, seconds) to compare against competitor expectations (section 9).
   - Shows the scenario list to the user for a quick sanity check only if the user asked for it; otherwise proceed.
4. **Execute** scenarios in priority order, updating status. For each issue found, immediately capture a screenshot and the repro steps.
5. **Verify previous findings** (section 2 table).
6. **Competitive pass** (section 9): evaluate the listed directions against the app and write the gap list.
7. **Write the report** (section 11), propose issues (section 12), and update indexes (section 14).

Tools tips: use accessibility snapshots plus screenshots; use device emulation and CDP for viewport; use the keyboard (Tab order) rather than clicks for the a11y pass; check the console for errors/warnings during every scenario (log notable ones as findings, tag `console`); check the network tab for failed requests (4xx/5xx) on the happy path.

## 9. Competitive parity and differentiators

Goal: judge if Gear Stack could replace other apps. All competitor facts below are 🟡 **assumptions from general knowledge (not verified for this plan)**; Cursor may verify them lightly by opening the public sites/screenshots if a browser is available, but must not create accounts with real personal data or scrape heavily. Treat this section as a hypothesis list to **evaluate Gear Stack against (not to implement)**.

| App | What users value (🟡) | Direction for Gear Stack to evaluate |
|-----|----------------------|--------------------------------------|
| **LighterPack** | Extremely fast spreadsheet-like list editing: add row, type name/weight/qty inline, Enter to next; drag-and-drop reorder across categories; live base/worn/consumable totals; category pie chart and legend; one-click **public share link**; CSV import/export; per-item worn/consumable toggles; unit switch (g/oz/lb/kg); very light, no clutter. | Time to first list with 10 items; keyboard-only row entry; reorder between categories; sharing link in <= 2 clicks; totals visible without scrolling; clarity of base/worn/consumable. Existing comparison: [LIGHTERPACK_COMPARISON.md](../research/LIGHTERPACK_COMPARISON.md). |
| **PackWizard** | Trip-oriented packing: templates per trip type/duration, weather/activity suggestions, checklists and "packed" state, collaboration/sharing, mobile apps. | Is there a "packed/checked" state per item and a packing-mode view? Templates (starter lists, clone container) discoverability? Trip concept missing? |
| **Hikerbase / Packstack** | Social/community: public gear lists, gear databases with weights, comparison with other users, gear "closet" separate from per-trip lists, profile pages. | Separation of inventory ("what I own") from trip lists (items linked across containers — Gear Stack has linking, ✅ per comparison doc); public profile/list browsing quality; catalogue as a weight database. |
| **GearGrams** | Weight-focused spreadsheets, gear library reused across lists, total weight and category breakdown, simple sharing. | Reuse of an item across several lists with consistent weight; library vs list distinction; speed of adding from library. |
| **Trailpacker** | Visual pack/gear lists with images, weight breakdown, sharing, community lists. | Item images in lists (#008), visual cards vs table toggle, shareable visual summary. |
| **PackLight** | Mobile-first quick lists, weight tracking per trip, simple UI. | Mobile quick-add (<= 30 s per item), thumb-zone actions, offline use. |
| **Hikt** (🟡 mostly trip planning/tracking) | Trip planning with packing list tie-in, apps for mobile. | Whether a gear list can be tied to a trip/date; reminders before trip (expiry, missing items). |
| **Generic inventory (e.g. Sortly)** | Photo-first items, QR/barcode labels and scan, quantities with low-stock alerts, folders/nesting, custom fields, bulk edit, search that is instant, activity log, mobile scanning. | Photo-first quick-add from phone camera; barcode/QR (🟡 not in scope today); quantity thresholds; bulk edit; instant global search; nested containers (✅ strength). |
| **Prepper / bug-out / emergency-supply apps** (🟡 various) | Expiry tracking with notifications, rotation (FIFO), per-person/per-days supply calculators (water, food, calories), checklists by scenario, offline-first, print/PDF checklists. | Expiration visibility (colour + sorting + reminders), readiness score explanation, shopping/to-buy list, offline, printable checklist/PDF export, "days of supply" calculators (idea only). |

### Cross-cutting patterns to evaluate (🟡 what winning apps tend to share)

1. **Speed of data entry** — spreadsheet-like inline entry, Enter to add next row, sensible defaults, paste-from-spreadsheet. Measure Gear Stack.
2. **Shareable read-only link** with a clean public view that works well on phones and requires no login. Evaluate the public/shared pages as an anonymous user and the sharing UX (tokens, publish toggle).
3. **Weight analytics** — base / worn / consumable split, by-category charts, big total number, goal/target weight (🟡 missing?), comparison between lists.
4. **Packing mode** — checkboxes "packed", progress bar, hide non-essential columns, large touch targets, works offline.
5. **Templates and starting points** — example lists, "clone", import from other apps (LighterPack CSV is a common ask), catalogue as source of weights.
6. **Mobile quick-add and offline** — PWA behaviour in the field.
7. **Item library vs list** — own inventory reused across lists.
8. **Print/PDF/export** — printable packing list; export of weights table.
9. **Trust/polish** — speed, no data loss, clear save status, account export/delete, privacy of public lists.

### Differentiators to confirm and present well (✅ per existing docs; check they are *discoverable and understandable* in the UI)

Nested containers, item linking across containers, global catalogue, statuses (owned/missing/toBuy) and priorities, expiry/shelf life, prices/currencies, shopping planning, AI assistant, ratings and public containers, DnD visualization, i18n pl/en, passkeys/2FA. For each: is the value visible within the first session, or hidden behind jargon/menus?

For each competitive direction, produce a verdict in the report: **parity / behind / ahead / n/a**, with evidence (screenshot or timing) and an effort guess. Do not propose features without tying them to a user task and a UX finding.

## 10. Evidence rules

- Screenshots: `docs/reviews/assets/2026-11-ui-ux/` (create it). Name: `<FindingID>-<route-slug>-<viewport>-<theme>-<locale>.png` (e.g. `F012-gear-id-375-dark-pl.png`). Crop or annotate when the issue is small; keep file size reasonable (PNG/WebP, < 500 kB each where possible). No real personal data in screenshots (use test accounts).
- Each finding: exact route (incl. params), viewport, theme, locale, account type (regular/premium/admin), data state (empty/small/large), numbered repro steps, expected vs actual, console/network errors if any, and the previous issue ID if related.
- Measurements over adjectives: px sizes, contrast ratio (tool-measured), click counts, seconds, number of items.
- Mark certainty: ✅ reproduced (2x) · 🟡 observed once / assumption · ❓ could not determine. Separate **bugs** from **design opinions**; label opinions as such.
- Positive findings count too: record what is already good (feeds "keep" list).
- If a flow is blocked (no SMTP, no OAuth, no premium, no backend), mark `not testable` with the reason; do not guess.

## 11. Output: findings report

File: `docs/reviews/2026-11-XX-ui-ux-browser-audit.md`. Sections:

1. **Header**: date, commit, environment (ports, browser tool), accounts/datasets used, viewports covered, time spent, coverage matrix (scenario IDs x priorities), what was not covered and why.
2. **Executive summary**: 5-10 lines, top 5 problems, top 5 strengths, verdict on "ready to replace competitors?" (🟡 opinion with reasons).
3. **Findings table**:

| ID | Area / route | Severity | Impact (who/how often) | Effort | Recommendation | Screenshot | Related issue | Certainty |
|----|--------------|----------|------------------------|--------|----------------|------------|---------------|-----------|
| F001 | ... | S1-S4 | ... | S/M/L | ... | link | #NNN | ✅/🟡/❓ |

   Severity scale: **S1** blocks a core task or loses/corrupts data or is inaccessible (fix now); **S2** major friction or confusion on a P0/P1 flow, or a clear WCAG AA failure; **S3** minor friction/readability/polish; **S4** nit/idea. Effort: **S** < 0.5 day, **M** 0.5-2 days, **L** > 2 days (frontend estimate).
4. **Previous findings re-verification** table (section 2): issue ID -> fixed / still present / regressed / not testable + evidence.
5. **Quick wins** (S/M effort and S2-S3 severity, max ~15), ordered by value/effort, each with a one-line change description.
6. **Competitive gap list** (section 9): direction -> verdict (parity/behind/ahead/n/a) -> evidence -> suggested follow-up (idea, not commitment) -> effort guess.
7. **Positive findings / keep list**.
8. **Cross-cutting themes** (e.g. "weights are not explained", "save status is unclear") — group related findings so they can be fixed as one change.
9. **Proposed issues** (section 12).
10. **Open questions** for the product owner (❓).

Keep the report factual and terse; use tables over prose. Write in English (or Polish if the user prefers; issue files in this repo are written mostly in Polish with English technical terms — either is accepted, stay consistent within the report).

## 12. Proposed issues

- Do **not** create issue files unless the user approves; first list proposals in the report (section 11.9).
- Naming (✅ [issues/README.md](../issues/README.md)): `YYYY-MM-DD--NNN--short-slug.md`, with a row in the README table. **Last used number at plan time: 044** (`2026-07-23--044--container-share-tokens-table-missing-prod.md`), so the next is **045**. Re-check the README immediately before creating files (other agents may have added issues).
- Group related findings into one issue (e.g. one for "weights explanation", one for "mobile table"); aim at issues an engineer can finish in 1-3 days. Each proposal: title, type (UX/A11y/bug/feature idea), severity, effort, repro/evidence link, acceptance criteria (testable), related issues.
- Use statuses from the README (`todo` by default). Mark competitive ideas as `todo` with type "idea" and low priority unless tied to an S1/S2 finding.
- Do not duplicate: if a finding matches an open issue, comment on that issue's ID in the report instead of proposing a new one.

## 13. Timeboxes (suggested; total about 8-10 h of agent work)

| Block | Time |
|-------|------|
| Read inputs (section 2) | 0.5 h |
| Environment + datasets | 0.5-1 h |
| Scenario list (section 8.3) | 0.5-1 h |
| P0 execution | 3 h |
| P1 execution | 2 h |
| P2 smoke | 1 h |
| Re-verification of old issues | 0.5 h (can overlap with P0) |
| Competitive pass | 0.5-1 h |
| Report + issue proposals | 1 h |

If time runs short: finish P0 completely (both mobile and desktop) before touching P1; shrink P2 to a smoke pass; always leave the last hour for the report. Stop and report early if a blocker prevents the app from running (do not "fix the app" to continue).

## 14. Constraints and rules

- **Do not modify application code, package files or `CLAUDE.md`** during the audit unless the user explicitly asks. Output files are limited to `docs/reviews/*` (report, scenarios, assets) and, after approval, `docs/issues/*`.
- **No production**: only local dev (`localhost`). Never log into or send traffic to the production site.
- **Docker underscore rule** ([CLAUDE.md](../../CLAUDE.md)): if the working directory name starts with `_`, run no `docker`/`docker compose` commands at all.
- **Do not delete or alter real data**: use dedicated `ux-audit*` accounts; destructive flows (delete all, delete account, admin deletes) only on those accounts and datasets. Do not run `db seed-remove`, DB resets or `init-test --force` unless the user agrees.
- No real payments (Stripe) and no real provider OAuth logins; no mass requests or scraping of competitor sites.
- Do not commit; do not push. Report and issue proposals are left for the user to review (project rule: no substantive content committed without user acceptance).
- Truth discipline: mark ✅/🟡/❓ explicitly; no invented facts about competitors or the codebase; "not testable" is a valid result.
- Keep secrets (passwords, tokens) out of reports and screenshots.

## 15. Definition of done

- [ ] Scenario list written before execution, with coverage matrix for P0/P1.
- [ ] P0 fully executed on phone (375), tablet (768), desktop (1280+), light and dark, en and pl (main flows).
- [ ] P1 executed at least on desktop + phone; P2 smoke pass done.
- [ ] Old findings re-verified (section 2 table).
- [ ] Report `docs/reviews/2026-11-XX-ui-ux-browser-audit.md` complete with findings table, quick wins, competitive gap list, proposed issues, open questions.
- [ ] Screenshots under `docs/reviews/assets/2026-11-ui-ux/` and linked.
- [ ] [reviews/README.md](../reviews/README.md) row updated (`planned` -> `done`) and [issues/README.md](../issues/README.md) updated only for approved issues; issue #032 closure proposed.

## Related

- [plans/README.md](README.md) · [reviews/README.md](../reviews/README.md) · [issues/README.md](../issues/README.md) · [research/README.md](../research/README.md)
