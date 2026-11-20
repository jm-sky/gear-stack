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

## Dla agentów AI: co czytać, czego nie

- Start: [../CLAUDE.md](../CLAUDE.md) (+ `src/CLAUDE.md`, `backend/CLAUDE.md` ładowane przy pracy w tych katalogach). Architektura: [claude/architecture.md](./claude/architecture.md).
- **Historyczne / ukończone — pomijaj, chyba że zadanie dotyczy historii:**
  - `archive/` (w tym `archive/cancelled/`, `archive/v2-unified-model/`) — zamknięte
  - `../V2_MIGRATION_STATUS.md` — status ukończonej migracji V1 -> V2 (kandydat do przeniesienia do `archive/v2-unified-model/`)
  - `deployment/PHASE-6-*.md`, `plans/PHASE-5-COMPLETION-SUMMARY.md`, `testing/MIGRATION_V2_TESTING_REPORT.md` — raporty faz/migracji (sprawdź status w indeksie przed użyciem)
  - `../CHANGELOG.md` (~130KB) — nie czytaj w całości
- Aktualne punkty wejścia: `issues/`, `reviews/`, `plans/`, `deployment/` (indeksy README w każdym).
- Uwaga: `ROADMAP_OFFLINE.md` opisuje tryb localStorage; dane gear są dziś V2 (backend + cache lokalny `gear-stack:items-v2`).

## Dokumenty operacyjne

- [deployment/](./deployment/README.md) — deployment, produkcja, Caddy, hardening Docker/DB
- [plans/security-dependabot-remediation.md](./plans/security-dependabot-remediation.md) — alerty zależności (Dependabot)

---

**Ostatnia aktualizacja:** 2026-07-06
