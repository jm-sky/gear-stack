# Wykonać zaplanowane review (security, code quality, UX, performance)

**Status:** `in progress`  
**Created:** 2026-07-06  
**Updated:** 2026-07-15 — UX review (sesja 1) ukończona → v2.51.0
**Related:** [docs/reviews/README.md](../reviews/README.md)

## Cel

W `docs/reviews/` są szablony do zapełnienia wynikami analiz. Każdy plik to **jedna dedykowana sesja AI** — należy przeprowadzić wszystkie zaplanowane review i uzupełnić sekcje **Findings** oraz **Follow-ups**.

## Zakres (7 sesji)

| # | Review | Scope | Plik | Status |
|---|--------|-------|------|--------|
| 1 | Security | Backend | [2026-07-06-security-backend.md](../reviews/2026-07-06-security-backend.md) | `planned` |
| 2 | Security | Frontend | [2026-07-06-security-frontend.md](../reviews/2026-07-06-security-frontend.md) | `planned` |
| 3 | Code quality | Backend | [2026-07-06-code-quality-backend.md](../reviews/2026-07-06-code-quality-backend.md) | `planned` |
| 4 | Code quality | Frontend | [2026-07-06-code-quality-frontend.md](../reviews/2026-07-06-code-quality-frontend.md) | `planned` |
| 5 | UX | Full stack (FE primary) | [2026-07-06-ux.md](../reviews/2026-07-06-ux.md) | `done` |
| 6 | Performance | Backend | [2026-07-06-performance-backend.md](../reviews/2026-07-06-performance-backend.md) | `planned` |
| 7 | Performance | Frontend | [2026-07-06-performance-frontend.md](../reviews/2026-07-06-performance-frontend.md) | `planned` |

## Instrukcja wykonania

1. Otwórz jeden plik review — **jedna sesja = jeden plik** (nie łączyć scope'ów w jednej sesji).
2. Przed startem przeczytaj sekcję **Baseline** w pliku oraz dokumenty wskazane w [reviews/README.md](../reviews/README.md) — nie duplikuj ślepo istniejących analiz.
3. Przejdź checklistę w pliku; zapisuj wyniki w tabeli **Findings** (severity, location, finding, recommendation).
4. Ustaw status w pliku review i w tabeli programu w [reviews/README.md](../reviews/README.md) (`in progress` → `done`).
5. Dla actionable follow-upów dodaj lub zaktualizuj wpisy w [issues/README.md](README.md).
6. Podczas security/UX review skrzyżuj z otwartymi issue'ami w [issues/](.).

## Baseline (nie powielać bez weryfikacji)

- [REVIEW_AND_REFACTOR_PLAN.md](../plans/REVIEW_AND_REFACTOR_PLAN.md) — security + code quality (2026-07-03)
- [plans/SECURITY_IMPROVEMENT_PLAN.md](../plans/SECURITY_IMPROVEMENT_PLAN.md) — production security roadmap
- [research/refactor/README.md](../research/refactor/README.md) — code quality refactor program
- [UX_REVIEW.md](../reviews/UX_REVIEW.md) — częściowy UX (2025-01-20)
- [research/billing-performance-recommendations.md](../research/billing-performance-recommendations.md) — billing performance
- [security-dependabot-remediation.md](../plans/security-dependabot-remediation.md) — alerty zależności

## Kryterium ukończenia

- Wszystkie 7 plików review ma status `done` (lub `verification needed` jeśli wymaga ręcznej weryfikacji).
- Tabela programu w `docs/reviews/README.md` jest zsynchronizowana ze statusami plików.
- Nowe, actionable ustalenia mają odpowiadające issue w `docs/issues/`.

## Sugerowana kolejność

1. Security (backend, potem frontend) — najwyższy priorytet
2. Code quality (backend, frontend)
3. UX
4. Performance (backend, frontend)
