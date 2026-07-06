# Dokumentacja Gear Stack

Ten katalog zawiera dokumentację projektu Gear Stack.

## Główne dokumenty

- **[ROADMAP.md](./ROADMAP.md)** — punkt wejścia — przegląd struktury roadmap
- **[ROADMAP_OFFLINE.md](./ROADMAP_OFFLINE.md)** — funkcjonalności offline (localStorage)
- **[ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md)** — funkcjonalności online (backend/DB/auth)
- **[features/](./features/)** — szczegółowe plany implementacji funkcji

## Workflow (issues, reviews, research, plans)

| Katalog | Przeznaczenie |
|---------|---------------|
| [issues/](./issues/README.md) | Błędy, usprawnienia, dług techniczny |
| [reviews/](./reviews/README.md) | Sesje przeglądu (security, code quality, UX, performance) |
| [research/](./research/README.md) | Analizy, spike'i, porównania przed decyzją |
| [plans/](./plans/README.md) | Plany implementacji większych zmian |

Statusy: `todo` · `planned` · `in progress` · `done` · `verification needed`

## Struktura katalogów

### `features/`
Szczegółowe plany implementacji poszczególnych funkcji z roadmap.

### `plans/`
Plany implementacji — indeks w [plans/README.md](./plans/README.md).

### `research/`
Analizy i porównania — indeks w [research/README.md](./research/README.md). Program refaktoru: [research/refactor/](./research/refactor/README.md).

### `reviews/`
Sesje przeglądu — indeks w [reviews/README.md](./reviews/README.md). Baseline UX: [reviews/UX_REVIEW.md](./reviews/UX_REVIEW.md).

### `examples/`
Przykładowe pliki i szablony.

### `archive/`
Przestarzałe dokumenty przeniesione do archiwum. Migracja V2: [archive/v2-unified-model/](./archive/v2-unified-model/README.md).

## Dokumenty operacyjne

- [deployment/](./deployment/README.md) — deployment, produkcja, Caddy, hardening Docker/DB
- [plans/security-dependabot-remediation.md](./plans/security-dependabot-remediation.md) — alerty zależności (Dependabot)

---

**Ostatnia aktualizacja:** 2026-07-06
