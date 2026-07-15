# A11y: pole hasła na logowaniu — accessible name z placeholdera

**Status:** `todo`  
**Created:** 2026-07-15  
**Updated:** 2026-07-15  
**Type:** bug (accessibility)  
**Severity:** medium  
**Related:** [UX review 2026-07-15](../reviews/2026-07-06-ux.md)

**Strona:** `/auth/login`

## Problem

Pole email ma poprawną nazwę **„Email *”**. Pole hasła w accessibility snapshot ma nazwę **„Enter your password”** (placeholder), podczas gdy widoczny label to **„Password *”**.

## Oczekiwane zachowanie

`aria-labelledby` / `<Label for="password">` powiązane z inputem; accessible name = „Password *” (lub tłumaczenie PL).

## Zakres

- [ ] Formularz logowania w module `auth` (komponent password + Label).
- [ ] Spójność z innymi formularzami auth (register, reset password).

## Weryfikacja

1. Accessibility snapshot / axe — password input name ≠ placeholder.
2. Klik label „Password” — focus na input.
