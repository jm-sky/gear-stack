# Research: Item form layout (`/gear/:id/items/new`)

**Status:** `done`  
**Date:** 2026-07-23  
**Related:** [issue #041](../issues/2026-07-23--041--add-item-page-layout-and-form-design.md)

## Current state (code baseline)

- [`ItemFormPage.vue`](../../src/modules/gear/pages/ItemFormPage.vue) wraps content in `max-w-2xl mx-auto` (~672px) inside [`AuthenticatedLayout`](../../src/layouts/AuthenticatedLayout.vue) (`max-w-7xl` + card padding).
- Effect: a narrow centered column with large empty side margins on desktop.
- [`ItemFormFields.vue`](../../src/modules/gear/components/ItemFormFields.vue) is mostly single-column; quantity/weight, priority/status, expiration already use `sm:grid-cols-2`. Extended fields sit under one heading; primary identity fields (name, category) are full-width stacked.
- Submit CTA is at the bottom of a long form (not sticky). Same page serves create + edit.

## Patterns (LighterPack / inventory forms)

From existing [`LIGHTERPACK_COMPARISON.md`](LIGHTERPACK_COMPARISON.md) and common gear/inventory UIs:

- Prefer clear **field groups** (identity → metrics → status → optional) over one flat list.
- Use available desktop width with **2 columns for related pairs**; keep mobile single-column.
- Avoid collapsing required create fields behind progressive disclosure — slows first-time entry.
- Sticky/footer actions help on long forms but must not obscure content on small screens.

## Recommendation (implemented)

1. Widen page wrapper to `max-w-4xl` (still inside layout `max-w-7xl`).
2. Add explicit section headings: identity, quantity/weight, status, expiration, notes, extended.
3. Put name + category in `md:grid-cols-2` when name is visible.
4. Keep CTA at bottom with `md:sticky md:bottom-0` bar (background so it stays readable); no collapsible groups in v1.
5. Do not change data model or validation.

## Out of scope

- Unifying nest-container into this page (#006 / issue #040 option A).
- Changing ContainerFormPage / CatalogueItemFormPage (same `max-w-2xl` pattern; can follow later).
