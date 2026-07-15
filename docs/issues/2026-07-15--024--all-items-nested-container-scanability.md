# UX: All Items — słaba czytelność zagnieżdżonych kontenerów

**Status:** `todo`  
**Created:** 2026-07-15  
**Updated:** 2026-07-15  
**Type:** improvement  
**Severity:** medium  
**Related:** [UX review 2026-07-15](../reviews/2026-07-06-ux.md)

**Strona:** `/gear/items`

## Problem

Tabela miesza przedmioty i zagnieżdżone kontenery (badge **„Container”**). Te same nazwy powtarzają się w kolumnach Name i Container (np. wiele „Apteczka Blackhawk”, „Do zakupu”) — trudno szybko ustalić kontekst / parent.

## Oczekiwane zachowanie

Użytkownik od razu widzi pełną ścieżkę lub parent kontenera dla każdego wiersza.

## Propozycje

- Kolumna Container domyślnie włączona z pełną ścieżką (breadcrumb).
- Tooltip na nazwie z hierarchią.
- Wizualne wcięcie / indent dla poziomów zagnieżdżenia.

## Zakres

- [ ] `AllItemsPage` + kolumny tabeli.
- [ ] Uzgodnić z issue #018 (nazwy w sidebarze).

## Weryfikacja

1. Konto z zagnieżdżonymi kontenerami — każdy wiersz jednoznaczny bez klikania.
2. Filtr + sort nadal działają.
