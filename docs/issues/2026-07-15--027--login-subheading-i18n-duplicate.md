# UX: logowanie — zduplikowany tekst w podtytule (i18n)

**Status:** `done`  
**Created:** 2026-07-15  
**Updated:** 2026-07-15 — zaakceptowane po review (`fix/ux-review-simple-medium`)
**Type:** improvement  
**Severity:** low  
**Related:** [UX review 2026-07-15](../reviews/2026-07-06-ux.md)

**Strona:** `/auth/login`

## Problem

Podtytuł czyta się jak **„Or create a new account Create new account”** — link i tekst zlepiły się bez separatora (EN; sprawdzić PL).

## Oczekiwane zachowanie

Naturalne zdanie, np. „Or [create a new account]” — jeden link, bez powtórzenia.

## Zakres

- [x] Klucze i18n w `auth` (en + pl).
- [x] Szablon login page — spacing / interpunkcja.

## Weryfikacja

1. EN i PL — brak podwójnego „Create new account” / „Utwórz nowe konto”.
