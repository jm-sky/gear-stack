# UX: dopracowanie inline editing (LighterPack / Excel)

**Status:** `planned`  
**Created:** 2026-07-15  
**Updated:** 2026-07-15 — wnioski z dyskusji produktowej  
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

Fundament inline editing jest zaimplementowany (toggle, edytowalne komórki, dirty state, zapis blur/Enter). UX nadal odbiega od LighterPack i od oczekiwań „excelowych” — wymaga dopracowania, nie budowy od zera.

**Stan w kodzie (2026-07-15):**
- Toggle „Enable Inline Editing” w toolbarze kontenera
- Pola inline: nazwa, ilość, waga, priorytet, status, cena, kategoria, notatki
- W trybie edycji inputy zawsze widoczne; zapis per wiersz (✓) + blur/Enter
- Brak: debounced auto-save, quick add row, nawigacja Tab/Enter/Esc między komórkami

**Rozjazd dokumentacji:** ROADMAP_OFFLINE oznacza podstawowy inline editing jako ✅ Completed; FEATURE-007 nadal 🔄 Planned; osobne zadanie „dopracowanie UX” w LIGHTERPACK_IMPROVEMENTS_TASKS — **to issue dotyczy tego drugiego etapu**.

---

## Wnioski z dyskusji (2026-07-15)

| # | Temat | Decyzja | Uwagi |
|---|--------|---------|-------|
| 1 | Tryb edycji (toggle vs zawsze ON) | **TBD — trzeba zobaczyć** | Wymaga prototypu / side-by-side; decyzja po ocenie w UI |
| 2 | Strategia zapisu | **Prawdopodobnie D** | Auto-save (debounce) + stany wizualne: zapisuję / zapisano / błąd |
| 3 | Quick add row | **Prawdopodobnie tak** | Pusty wiersz na końcu tabeli; do potwierdzenia po prototypie |
| 4 | Klawiatura | **Tab, Enter, Esc** | Must-have; bez paste / strzałek na start |
| 5 | Problemy wizualne | **Prawdopodobnie wszystkie razem** | Hałas inputów, niespójne obramowania, wąskie kolumny, Save+Undo per wiersz, brak focus na komórce |
| 6 | Mobile | **Jak LighterPack** | Prosta siatka / scroll; bez osobnego widoku kart (na razie) |
| 7 | Zakres pól w siatce | **Jak LighterPack** | Rdzeń: nazwa, qty, waga, kategoria; reszta poza główną siatką lub w menu wiersza |

**Inspiracje:** LighterPack (prostota, auto-save, quick add) + Excel (Tab/Enter/Esc, siatka).

---

## Oczekiwane zachowanie (docelowe)

1. Edycja przedmiotów w tabeli jest **płynna i przewidywalna** — bez konieczności ręcznego „Save” per wiersz (przy strategii D).
2. **Tab** — następna edytowalna komórka; **Enter** — zatwierdzenie + ruch w dół (lub następna komórka — do ustalenia w planie); **Esc** — anulowanie bieżącej komórki.
3. **Quick add row** — dodanie przedmiotu bez formularza `/items/new` (jeśli potwierdzone po prototypie).
4. **Feedback zapisu** — widoczny stan wiersza/komórki (pending / saving / saved / error + retry).
5. **Wygląd** — spójna siatka komórek, czytelny focus, mniej wizualnego szumu niż obecny tryb edycji.
6. **Mobile** — używalna tabela z horizontal scroll (wzór LighterPack), spójna z #017.

---

## Otwarte pytania (blokery przed pełną implementacją)

- [ ] **Toggle vs always-on** — po prototypie A/B (lub demo w dev)
- [ ] **Quick add row** — ostateczne tak/nie po zobaczeniu flow
- [ ] **Enter** — zapis + w dół (Excel) vs zapis + blur (LighterPack)?
- [ ] Czy usunąć przycisk ✓ per wiersz po wdrożeniu auto-save?

---

## Zakres implementacji

- [ ] Plan: [2026-07-15-inline-editing-ux-plan.md](../plans/2026-07-15-inline-editing-ux-plan.md)
- [ ] Faza 0: prototyp / demo do decyzji (toggle, quick add, wizual)
- [ ] Faza 1: auto-save + stany zapisu (strategia D)
- [ ] Faza 2: nawigacja Tab / Enter / Esc
- [ ] Faza 3: quick add row (jeśli potwierdzone)
- [ ] Faza 4: polish wizualny siatki + mobile
- [ ] Aktualizacja FEATURE-007 i LIGHTERPACK_IMPROVEMENTS_TASKS po wdrożeniu

---

## Weryfikacja

1. Desktop — edycja 5+ pól w wielu wierszach bez klikania „Save”; Tab/Enter/Esc działają intuicyjnie.
2. Quick add (jeśli wdrożone) — nowy przedmiot z pustego wiersza bez nawigacji do formularza.
3. Stany zapisu — widać saving/saved/error; błąd sieci umożliwia retry.
4. Mobile 375px — tabela używalna (scroll); br regresji względem #017.
5. Porównanie z LighterPack — subiektywna ocena „nie gorzej niż LP” na core fields.
