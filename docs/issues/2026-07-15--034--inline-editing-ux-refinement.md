# UX: dopracowanie inline editing (LighterPack / Excel)

**Status:** `verification needed`  
**Created:** 2026-07-15  
**Updated:** 2026-07-23 — auto-save, Tab/Enter/Esc, quick add, mobile polish (sticky name/actions, touch targets) shipped  
**Type:** improvement  
**Severity:** medium  
**Priority:** high  
**Related:**
- [Plan implementacji](../plans/2026-07-15-inline-editing-ux-plan.md)
- [FEATURE-007](../features/FEATURE-007-inline-editing.md)
- [LIGHTERPACK_IMPROVEMENTS_TASKS.md §5](../research/LIGHTERPACK_IMPROVEMENTS_TASKS.md)
- [ROADMAP_OFFLINE — Quick Add / Inline Editing](../ROADMAP_OFFLINE.md)
- [#017](2026-07-15--017--container-detail-mobile-layout.md), [#022](2026-07-15--022--container-detail-toolbar-clutter.md)

**Strona:** `/gear/:id` (Container detail — tabela przedmiotów)

---

## Kontekst

Fundament inline editing był zaimplementowany wcześniej; ten issue dotyczy dopracowania UX (LighterPack + Excel).

**Stan w kodzie (2026-07-23):**
- ✅ Toggle „Enable Inline Editing”
- ✅ Pola inline + debounced auto-save (`useInlineRowSave`) + wskaźnik pending/saving/saved/error
- ✅ Nawigacja Tab / Shift+Tab / Enter (w dół) / Esc
- ✅ Quick add row (`ItemsTableQuickAddRow`)
- ✅ Domyślne kolumny: name, category, qty, weight (+ actions); priority/status/price ukryte
- ✅ Mobile: kompaktowy toggle, ukryte chevrons reorder, touch targets `h-10`, sticky name + actions, horizontal scroll

---

## Wnioski z dyskusji (2026-07-15)

| # | Temat | Decyzja | Uwagi |
|---|--------|---------|-------|
| 1 | Tryb edycji (toggle vs zawsze ON) | **Na razie toggle** | Always-on odłożone (Faza 0 prototyp nieblokujący) |
| 2 | Strategia zapisu | **D** | Debounce ~450ms + stany wizualne |
| 3 | Quick add row | **Tak** | Wdrożone |
| 4 | Klawiatura | **Tab, Enter, Esc** | Enter = zapis + wiersz poniżej (Excel) |
| 5 | Problemy wizualne | **Razem** | Transparent inputs, focus-within, tint wiersza |
| 6 | Mobile | **Jak LighterPack** | Horizontal scroll + sticky kolumny |
| 7 | Zakres pól w siatce | **Jak LighterPack** | Rdzeń 4 kolumny |

---

## Zakres implementacji

- [x] Plan: [2026-07-15-inline-editing-ux-plan.md](../plans/2026-07-15-inline-editing-ux-plan.md)
- [ ] Faza 0: prototyp / demo do decyzji (toggle always-on) — opcjonalne, nieblokujące
- [x] Faza 1: auto-save + stany zapisu (strategia D)
- [x] Faza 2: nawigacja Tab / Enter / Esc
- [x] Faza 3: quick add row
- [x] Faza 4: polish wizualny siatki + mobile
- [x] Aktualizacja FEATURE-007 i LIGHTERPACK_IMPROVEMENTS_TASKS

---

## Weryfikacja

1. Desktop — edycja wielu pól bez „Save”; Tab/Enter/Esc działają.
2. Quick add — nowy przedmiot z pustego wiersza.
3. Stany zapisu — pending/saving/saved/error + retry.
4. Mobile 375px — full-width main; tabela scroll + sticky name/actions; brak pustego panelu (#017).
5. Porównanie z LighterPack — core fields używalne.
