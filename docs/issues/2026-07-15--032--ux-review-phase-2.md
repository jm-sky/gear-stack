# UX review — faza 2 (obszary nieobjęte sesją 2026-07-15)

**Status:** `planned`  
**Created:** 2026-07-15  
**Updated:** 2026-07-15  
**Type:** review / QA  
**Related:** [UX review 2026-07-06](../reviews/2026-07-06-ux.md) (sesja 1 — `done`)

## Cel

Uzupełnić przegląd UX o obszary **nie sprawdzone** w pierwszej sesji (browser review), żeby review był pełny — nie tylko gear list/detail/forms.

## Środowisko

Jak sesja 1: Docker backend, `pnpm dev`, użytkownik `e2e-test@example.com` + ewentualnie konto **admin** do panelu admin.

**Narzędzie:** Cursor Browser lub Playwright; viewport desktop + mobile.

## Checklist fazy 2

### Import / export
- [ ] Dropdown „More actions” na `/gear` — Import JSON, Markdown, CSV
- [ ] Export Markdown / CSV / JSON — feedback (toast, plik, błędy walidacji)
- [ ] Import przy zalogowanym użytkowniku (regresja #004)
- [ ] Cross-check z issues #002, #003, #004

### Dialogi i akcje destrukcyjne
- [ ] Usuwanie kontenera / przedmiotu — confirm dialog, copy, anulowanie
- [ ] Delete account w settings — flow ostrzeżeń
- [ ] Nested container dialog (#005)

### Auth rozszerzone
- [ ] Rejestracja, forgot password
- [ ] 2FA setup (#016 — verification needed)
- [ ] WebAuthn / passkeys — empty state w settings
- [ ] OAuth buttons visibility (#013, #014)
- [ ] Session expiry → redirect + komunikat

### Moduły nieodwiedzone
- [ ] Admin dashboard (konto admin)
- [ ] AI chat — premium gate, loading, błędy kontekstu
- [ ] Stats / analytics
- [ ] Billing / plany — pełny flow CTA z banera
- [ ] Shopping list (`/gear/shopping` lub equivalent)
- [ ] Public containers — lista + detail jako gość/zalogowany
- [ ] User profile / public profile

### Systemowe
- [ ] 404 / NotFound
- [ ] PWA install prompt, offline (service worker)
- [ ] Rate limiting / 5xx — komunikat w UI
- [ ] V1/V2 stale cache po mutacji (#001, #007)

### Jakość przekrojowa
- [ ] Keyboard-only przejście przez główne flow
- [ ] Focus trap w dialogach
- [ ] Tablet 768×1024 — gear + settings

## Deliverable

1. Uzupełnić tabelę **Findings** w [2026-07-06-ux.md](../reviews/2026-07-06-ux.md) lub dodać sekcję „Phase 2”.
2. Nowe issue’y pod actionable findings (`docs/issues/`).
3. Status tego pliku → `done` po zakończeniu.

## Istniejące issue’y do cross-check

| ID | Temat |
|----|--------|
| 005 | Nested container dialog empty |
| 006 | Add existing item tab |
| 007 | Lista nie odświeża się po add |
| 008 | Brak obrazków na liście |
| 016 | 2FA API 404 |

## Notatki

Sesja 1 (2026-07-15) objęła: landing, login, dashboard, `/gear`, container detail, add item, create container, all items, settings, catalogue, dark mode, mobile spot-check. Findings → issues **#017–#031**.
