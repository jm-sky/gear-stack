# Plan: Inline editing UX (LighterPack + Excel)

**Status:** `done`  
**Created:** 2026-07-15  
**Updated:** 2026-07-24 — marked done (Faza 0 always-on optional)  
**Issue:** [#034](../issues/2026-07-15--034--inline-editing-ux-refinement.md)  
**Related:**
- [FEATURE-007](../features/FEATURE-007-inline-editing.md)
- [LIGHTERPACK_IMPROVEMENTS_TASKS.md §5](../research/LIGHTERPACK_IMPROVEMENTS_TASKS.md)
- [ROADMAP_OFFLINE — Quick Add / Inline Editing](../ROADMAP_OFFLINE.md)

---

## Cel

Dopracować UX edycji inline w tabeli przedmiotów na stronie kontenera, tak aby zbliżyć się do **LighterPack** (prostota, auto-save, quick add) z elementami **Excel** (nawigacja Tab / Enter / Esc), bez budowania od zera — fundament już istnieje.

---

## Stan obecny (baseline)

| Element | Stan |
|---------|------|
| Toggle edit mode | ✅ `ItemsTableEditModeToggle` + localStorage |
| Edytowalne pola | ✅ nazwa, qty, waga, priorytet, status, cena, kategoria, notatki |
| UI w edit mode | Inputy zawsze widoczne (nie click-to-edit) |
| Zapis | Dirty map per wiersz + przycisk ✓; blur/Enter na polach |
| Debounced auto-save | ❌ (opisane w FEATURE-007, brak w kodzie) |
| Quick add row | ❌ |
| Tab / Enter / Esc między komórkami | ❌ |
| Wskaźnik saving/saved/error | ❌ (tylko `isSaving` na nazwie) |

**Pliki kluczowe:**
- `src/modules/gear/components/ItemsTable.vue`
- `src/modules/gear/components/items-table/ItemsTableEditable*.vue`
- `src/modules/gear/composables/useInlineItemEditingV2.ts`
- `src/modules/gear/composables/useItemsTableEditMode.ts`

---

## Decyzje produktowe (dyskusja 2026-07-15)

| Temat | Decyzja | Implikacja |
|-------|---------|------------|
| Toggle vs always-on | **TBD — prototyp** | Faza 0: dwa warianty do oceny w UI |
| Zapis | **Prawdopodobnie D** | Debounce 500ms + stany: pending → saving → saved / error |
| Quick add | **Prawdopodobnie tak** | Faza 3 po potwierdzeniu |
| Klawiatura | **Tab, Enter, Esc** | Faza 2 — must-have |
| Wygląd | **Wszystkie problemy naraz** | Faza 4 — spójna siatka, focus, mniej Save/Undo |
| Mobile | **Jak LighterPack** | Horizontal scroll; bez widoku kart na start |
| Pola w siatce | **Jak LighterPack** | Rdzeń: name, qty, weight, category; reszta poza główną siatką |

---

## Docelowe zachowanie

### Zapis (strategia D — do wdrożenia)

1. Zmiana w komórce → **debounce 500ms** → jeden request z zebranymi polami wiersza (jak w FEATURE-007).
2. **Enter** w komórce → natychmiastowy zapis (anuluje debounce).
3. **Esc** → anulowanie bieżącej komórki (przywrócenie wartości).
4. Stany per wiersz:
   - *pending* — żółta kropka / subtelne tło
   - *saving* — spinner / disabled
   - *saved* — krótki flash (1–2 s) lub checkmark
   - *error* — czerwony obrys + retry (klik lub Enter)

Usunąć lub ukryć przycisk ✓ per wiersz po stabilnym auto-save (decyzja w Fazie 1).

### Nawigacja klawiaturą

| Klawisz | Zachowanie (propozycja) |
|---------|-------------------------|
| **Tab** | Następna edytowalna komórka w wierszu; na końcu wiersza → pierwsza komórka następnego wiersza |
| **Shift+Tab** | Poprzednia komórka |
| **Enter** | Zapis bieżącej komórki + focus na **tej samej kolumnie, wiersz poniżej** (Excel) |
| **Esc** | Anuluj edycję bieżącej komórki |

*Do potwierdzenia:* Enter „w dół” vs „blur tylko” — domyślnie Excel (w dół).

Implementacja: composable `useItemsTableCellNavigation.ts` + `data-cell-id` / refs na edytowalnych komórkach.

### Quick add row (jeśli potwierdzone)

- Ostatni wiersz tabeli w edit mode = pusty szablon (`isDraft: true`).
- Wymagane minimum: **nazwa** (reszta domyślne z FEATURE-004).
- Po zapisie (blur z nazwą / Enter) → `createItem` → nowy pusty wiersz pod spodem.
- Esc na pustym wierszu → usuń draft jeśli pusty.

### Zakres kolumn (LighterPack)

**W głównej siatce (zawsze edytowalne w edit mode):**
- Name, Quantity, Weight (+ unit), Category

**Poza główną siatką** (menu wiersza, osobne kolumny opcjonalne, formularz):
- Priority, Status, Price, Notes, Wearable, Consumable, …

*Uwaga:* obecnie wszystkie 8 pól są inline — redukcja „hałasu” może wymagać zmiany domyślnej widoczności kolumn lub ukrycia zaawansowanych pól w trybie „simple” (powiązane z ROADMAP Simple Mode, ale nie blokuje tego planu).

### Wygląd siatki (Faza 4)

- Spójne obramowania komórek w edit mode (jeden token, np. `border-input/30`).
- Wyraźny **focus ring** na aktywnej komórce.
- Dirty row — subtelne tło wiersza zamiast Undo w każdej komórce (Undo opcjonalnie tylko na focus).
- Szerokości kolumn: qty min ~4rem; weight z unit inline; name flex.
- Mniej „form-like” padding — komórki jak siatka, nie jak osobne formularze.

### Mobile (LighterPack)

- Zachować tabelę + horizontal scroll (zgodnie z UX_REVIEW).
- Touch: tap = focus komórki; nie wymagać Tab.
- Powiązane z #017 — pełna szerokość main na mobile przed finalnym sign-off.

---

## Fazy implementacji

### Faza 0 — Prototyp do decyzji (TBD: toggle, quick add, look)

**Cel:** Umożliwić ocenę „muszę zobaczyć” przed pełnym rollout.

- [ ] Branch / flag `VITE_INLINE_EDIT_PROTOTYPE` lub lokalny demo
- [ ] Wariant A: toggle (obecny) vs Wariant B: always-on (edit mode domyślnie true, opcjonalnie w settings)
- [ ] Mock quick add row (bez backendu) — ocena flow
- [ ] Mock auto-save states — ocena feedbacku
- [ ] Screenshot / krótki film do decyzji produktowej

**Exit criteria:** Decyzja toggle vs always-on; tak/nie quick add; akceptacja kierunku wizualnego.

### Faza 1 — Auto-save + stany zapisu (strategia D)

- [x] Rozszerzyć `useInlineItemEditingV2` (lub nowy `useInlineRowSave`) o debounce 500ms, merge pól, `saveImmediately`
- [x] Stany per wiersz w `ItemsTable.vue`: pending / saving / saved / error
- [x] Usunąć lub ukryć ✓ per wiersz (po QA)
- [x] Error toast + retry inline

### Faza 2 — Nawigacja Tab / Enter / Esc

- [x] Composable nawigacji między komórkami
- [x] Spójna obsługa w `ItemsTableEditable*Cell`
- [x] Testy manualne: 3×3 wiersze, tylko klawiatura

### Faza 3 — Quick add row (warunkowo)

- [x] Draft row na końcu tabeli
- [x] Integracja z `useGearV2().createItem`
- [x] i18n: placeholder „Add item…”

### Faza 4 — Polish wizualny + mobile

- [x] Ujednolicenie stylów komórek
- [x] Focus / dirty row styling
- [x] Regresja mobile (#017) — full-width main, touch targets h-10, sticky name+actions, horizontal scroll
- [x] Ewentualnie: domyślna widoczność kolumn (core 4 — priority/status ukryte)

### Faza 5 — Dokumentacja

- [x] Zaktualizować FEATURE-007 (status, acceptance criteria)
- [x] Zaktualizować LIGHTERPACK_IMPROVEMENTS_TASKS §5
- [x] ROADMAP_OFFLINE — sekcja dopracowania → ✅ po weryfikacji
- [x] Issue #034 → `done`

---

## Poza zakresem (na teraz)

- Paste z Excela / bulk edit wielu komórek
- Strzałki między komórkami
- Osobny widok kart na mobile
- Simple Mode toggle (osobny roadmap item)
- Real-time waga w headerze (LIGHTERPACK task #8 — osobno)

---

## Ryzyka

| Ryzyko | Mitygacja |
|--------|-----------|
| Konflikt z paginacją (Enter w ostatnim wierszu strony) | Enter na ostatnim wierszu → nowa strona lub quick add |
| Select/combobox (category, status) łamią Tab flow | Tab skip lub rozwinięty select tylko na Enter/Space |
| V2 cache stale po szybkich zapisach | Invalidacja `gearQueryKeys` po save (istniejący pattern) |
| Toggle + always-on — dwa UX | Faza 0 przed kodem produkcyjnym |

---

## Metryki sukcesu

- Edycja 10 przedmiotów (name + qty + weight) bez użycia myszy poza focusem — **≤ 2 min**
- Brak konieczności klikania Save per wiersz
- Subiektywna ocena vs LighterPack: „co najmniej równie wygodne” na desktop
- Brak regresji a11y (aria-label na komórkach zachowane)

---

## Test plan

1. Desktop Chrome/Firefox — Tab przez wiersz i kolumny
2. Enter — zapis + ruch w dół
3. Esc — revert komórki
4. Szybkie edycje w 3 polach jednego wiersza → jeden debounced save
5. Offline / błąd API → error state + retry
6. Quick add — 3 nowe przedmioty z pustego wiersza
7. Mobile 375px — scroll, tap-to-edit
8. Public mode — brak edit UI (bez regresji)
