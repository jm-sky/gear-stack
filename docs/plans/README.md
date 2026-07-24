# Plans

Implementation plans for features and larger changes.

## Status values

`todo` · `planned` · `in progress` · `done` · `verification needed`

## Index

| File | Summary | Status |
|------|---------|--------|
| [2026-07-15-inline-editing-ux-plan.md](2026-07-15-inline-editing-ux-plan.md) | Inline editing UX — LighterPack + Excel (Tab/Enter/Esc, auto-save) | `done` |
| [AI_PLAN.md](AI_PLAN.md) | AI integration plan | `done` |
| [API_INTEGRATION_PLAN.md](API_INTEGRATION_PLAN.md) | API integration plan | `done` |
| [BACKEND_INTEGRATION.md](BACKEND_INTEGRATION.md) | Backend integration plan | `done` |
| [B2a-CRITICAL-FIXES-PLAN.md](B2a-CRITICAL-FIXES-PLAN.md) | Critical auth/WebAuthn security fixes (from refactor analysis) | `done` |
| [CLEAN_ITEM_UPDATE_DATA_IMLPEMENTATION_PLAN.md](CLEAN_ITEM_UPDATE_DATA_IMLPEMENTATION_PLAN.md) | Clean item update data implementation | `done` |
| [COMPONENT_REFACTORING_PLAN.md](COMPONENT_REFACTORING_PLAN.md) | Split large Vue components (>300 LOC) into smaller pieces | `in progress` |
| [CONTENT_REPORTING_IMPLEMENTATION_PLAN.md](CONTENT_REPORTING_IMPLEMENTATION_PLAN.md) | Content reporting implementation | `done` |
| [CONTAINER_RATING_IMPLEMENTATION_PLAN.md](CONTAINER_RATING_IMPLEMENTATION_PLAN.md) | Container rating feature | `planned` |
| [CONTAINER_VIEWS_STATS_PLAN.md](CONTAINER_VIEWS_STATS_PLAN.md) | Container views and stats | `planned` |
| [GLOBAL_CATALOGUE_IMPLEMENTATION_PLAN.md](GLOBAL_CATALOGUE_IMPLEMENTATION_PLAN.md) | Global catalogue implementation | `in progress` |
| [global-catalogue-items.md](global-catalogue-items.md) | Global catalogue items (v1 notes) | `done` |
| [global-catalogue-items-v2.md](global-catalogue-items-v2.md) | Catalogue content v2 — seed new items + example sets (not feature code) | `in progress` |
| [implementation-suggestions.md](implementation-suggestions.md) | General implementation suggestions | `done` |
| [MARKDOWN_LINK_SECURITY_PLAN.md](MARKDOWN_LINK_SECURITY_PLAN.md) | Markdown link security | `planned` |
| [PHASE-5-COMPLETION-SUMMARY.md](PHASE-5-COMPLETION-SUMMARY.md) | Stripe billing phase 5 completion summary | `done` |
| [PLAN_PAGE_TITLES.md](PLAN_PAGE_TITLES.md) | Page titles plan | `planned` |
| [REFACTOR_PROGRESS.md](REFACTOR_PROGRESS.md) | Progress tracker for REVIEW_AND_REFACTOR_PLAN | `in progress` |
| [REVIEW_AND_REFACTOR_PLAN.md](REVIEW_AND_REFACTOR_PLAN.md) | Code review and phased refactor plan (2026-07-03) | `in progress` |
| [SECURITY_IMPROVEMENT_PLAN.md](SECURITY_IMPROVEMENT_PLAN.md) | Production security audit — CSP, HSTS, WAF, cookies (moved from `docs/security/`) | `in progress` |
| [security-dependabot-remediation.md](security-dependabot-remediation.md) | GitHub Dependabot alerts remediation (pnpm overrides) | `done` |
| [stripe-pattern-verification.md](stripe-pattern-verification.md) | Stripe pattern verification | `done` |
| [stripe-subscription-implementation.md](stripe-subscription-implementation.md) | Stripe subscription implementation | `done` |
| [stripe-subscription-requirements.md](stripe-subscription-requirements.md) | Stripe subscription requirements | `done` |
| [stripe-webhook-signature-troubleshooting.md](stripe-webhook-signature-troubleshooting.md) | Stripe webhook signature troubleshooting | `done` |
| [UNIFIED_MODEL_IMPLEMENTATION_PLAN.md](UNIFIED_MODEL_IMPLEMENTATION_PLAN.md) | Unified model implementation | `in progress` |
| [UNIFIED_MODEL_V2_MISSING_FEATURES.md](UNIFIED_MODEL_V2_MISSING_FEATURES.md) | V2 missing features inventory | `in progress` |
| [2026-07-22-visualization-dnd-zones.md](2026-07-22-visualization-dnd-zones.md) | Container visualization — DnD placements + custom zones (DB) | `done` |
| [2026-07-23-gear-backend-v1-v2-unification.md](2026-07-23-gear-backend-v1-v2-unification.md) | Backend gear V1→V2 unification — drop legacy tables/models, repoint ratings/reports/promotions/stats/admin to `gear_items_v2` | `done` |

When adding a new plan: create `YYYY-MM-DD-slug.md` (legacy SCREAMING_SNAKE names are OK for older files — add a row here).

## Related

- [research/README.md](../research/README.md) — analyses and spikes before planning
- [reviews/README.md](../reviews/README.md) — review sessions that may spawn new plans
- [issues/README.md](../issues/README.md) — actionable follow-ups from plans and reviews
