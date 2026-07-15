# UX: logowanie — zduplikowany komunikat błędu pod oboma polami

**Status:** `todo`  
**Created:** 2026-07-15  
**Updated:** 2026-07-15  
**Type:** improvement  
**Severity:** low  
**Related:** [UX review 2026-07-15](../reviews/2026-07-06-ux.md)

**Strona:** `/auth/login`

## Problem

Po błędnym haśle ten sam tekst **„Invalid email or password”** pojawia się pod polem Email i pod polem Password. Redundantne dla użytkownika i głośne dla czytników ekranu.

## Oczekiwane zachowanie

Jeden komunikat na poziomie formularza (`role="alert"`) lub przy jednym polu — przy zachowaniu ogólnego komunikatu ze względów bezpieczeństwa.

## Zakres

- [ ] Login form error display (vee-validate / FormMessage).
- [ ] i18n PL/EN.

## Weryfikacja

1. Złe hasło — jeden komunikat (lub jeden alert + border na obu polach bez duplikacji tekstu).
2. Błąd walidacji formatu email — nadal przy właściwym polu.
