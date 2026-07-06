# Prompt: wdrożenie struktury dokumentacji

> **Cel:** Skopiuj sekcję **„PROMPT DO WKLEJENIA”** poniżej i wklej do AI w każdym z 4 klonów `gear-stack`.
> Ten plik jest meta-dokumentem — po wdrożeniu w danym repo można go zostawić lub przenieść do `docs/research/`.

---

## PROMPT DO WKLEJENIA

```
Wdroż ustandaryzowaną strukturę dokumentacji w tym repozytorium (klon gear-stack).

## Zakres

Utwórz lub doprowadź do standardu cztery katalogi robocze pod `docs/`:

| Katalog | Przeznaczenie |
|---------|---------------|
| `docs/issues/` | Błędy, usprawnienia, dług techniczny — elementy do naprawy |
| `docs/reviews/` | Wyniki przeglądów (security, code quality, UX, performance) |
| `docs/research/` | Analizy, spike’i, porównania, notatki przed decyzją |
| `docs/plans/` | Plany implementacji funkcji i większych zmian |

Każdy katalog MUSI mieć `README.md` jako **indeks** (tabela wszystkich plików + legenda statusów).

## Konwencja nazw plików

**Tylko `docs/issues/`** używa numeru ID w nazwie pliku. Pozostałe katalogi — sama data + slug.

### issues

```
YYYY-MM-DD--NNN--kebab-tytul.md
```

- `YYYY-MM-DD` — data utworzenia wpisu (nie zmieniaj przy drobnych edycjach; opcjonalnie dopisz `Updated: YYYY-MM-DD` w nagłówku pliku)
- `NNN` — trzycyfrowy numer sekwencyjny **w obrębie `docs/issues/`** (`001`, `002`, …)
- `kebab-tytul` — krótki slug po angielsku lub polsku (bez spacji, małe litery, myślniki)

Przykłady:
- `2026-07-04--001--v2-cache-invalidation.md`
- `2026-07-05--002--export-markdown-csv-dropdown.md`

### reviews, research, plans

```
YYYY-MM-DD-kebab-tytul.md
```

- `YYYY-MM-DD` — data utworzenia (jak wyżej)
- `kebab-tytul` — krótki slug (bez `NNN` w nazwie pliku)

Przykłady:
- `2026-07-06-security-backend.md`
- `2026-07-06-stripe-webhook-spike.md`
- `2026-07-06-unified-model-migration.md`

**Nie używaj** GitHub Issues do śledzenia tych elementów — tylko pliki w `docs/`.

## Statusy

Dozwolone wartości (w indeksie i w nagłówku każdego pliku):

| Status | Znaczenie |
|--------|-----------|
| `todo` | Zidentyfikowane, nie rozpoczęte |
| `planned` | Opisane i zaplanowane |
| `in progress` | W trakcie pracy |
| `done` | Zakończone / zaakceptowane |
| `verification needed` | Poprawka wdrożona — wymaga weryfikacji manualnej lub QA |

## Szablon README.md (każdy katalog)

Każdy `docs/{issues,reviews,research,plans}/README.md`:

**issues** — kolumna `ID` w indeksie (numer z nazwy pliku):

```markdown
# Issues

{Jedno zdanie — co trafia do tego katalogu.}

## Status values

`todo` · `planned` · `in progress` · `done` · `verification needed`

## Index

| ID | File | Summary | Status |
|----|------|---------|--------|
| 001 | [2026-07-04--001--example.md](2026-07-04--001--example.md) | Krótki opis | `todo` |

When adding a new issue: pick next `NNN`, create `YYYY-MM-DD--NNN--slug.md`, add a row here.
```

**reviews, research, plans** — bez kolumny `ID`:

```markdown
# {Reviews | Research | Plans}

{Jedno zdanie — co trafia do tego katalogu.}

## Status values

`todo` · `planned` · `in progress` · `done` · `verification needed`

## Index

| File | Summary | Status |
|------|---------|--------|
| [2026-07-06-security-backend.md](2026-07-06-security-backend.md) | Krótki opis | `todo` |

When adding a new entry: create `YYYY-MM-DD-slug.md`, add a row here.
```

## Szablon pojedynczego pliku

```markdown
# Tytuł czytelny dla człowieka

**Status:** `todo`  
**Created:** YYYY-MM-DD  
**Updated:** YYYY-MM-DD  

## Context

Dlaczego ten wpis istnieje.

## …

Treść zależna od typu (patrz poniżej).

## Follow-ups

Linki do innych plików w `docs/issues/`, `docs/plans/` itd.
```

### Różnice per katalog

**issues** — sekcje: Context, Symptoms, Root cause, Suggested fix, Files, Related

**reviews** — sekcje: Scope, Baseline (linki do istniejących docs), Checklist (`- [ ]`), Findings (tabela: Severity | Location | Finding | Recommendation), Follow-ups

**research** — sekcje: Question, Method, Findings, Conclusion, Decision (jeśli podjęta)

**plans** — sekcje: Goal, Scope, Out of scope, Phases / tasks, Acceptance criteria, Related issues

## CLAUDE.md

Dodaj lub zaktualizuj **krótką** sekcję (max ~5 linii), bez duplikowania treści:

```markdown
## Docs workflow

- **Issues:** [docs/issues/README.md](docs/issues/README.md)
- **Reviews:** [docs/reviews/README.md](docs/reviews/README.md)
- **Research:** [docs/research/README.md](docs/research/README.md)
- **Plans:** [docs/plans/README.md](docs/plans/README.md)

Statuses: `todo`, `planned`, `in progress`, `done`, `verification needed`. New issues: `YYYY-MM-DD--NNN--slug.md`; reviews/research/plans: `YYYY-MM-DD-slug.md`.
```

Zachowaj istniejące sekcje `CLAUDE.md` (komendy, architektura, konwencje kodu) — tylko dodaj/zmień sekcję Docs workflow.

## Migracja istniejących plików (jeśli są)

1. **Przeskanuj** `docs/`, root (`BUGS.md` itd.) i `CLAUDE.md` pod kątem linków do przenoszonych plików.
2. **issues** — przenieś znane listy błędów (np. `BUGS.md`, `docs/issues/*.md` bez numeru ID) do `docs/issues/YYYY-MM-DD--NNN--*.md`; scal wiele bugów w jednym pliku tylko jeśli to jeden temat; rozdziel na osobne pliki gdy to osobne zadania.
3. **reviews** — przenieś / przemianuj pliki z `docs/reviews/` na konwencję `YYYY-MM-DD-slug.md` (bez `NNN`).
4. **plans** — **nie przemieniaj masowo** starych `docs/plans/*.md` (SCREAMING_SNAKE); dodaj wiersze w `docs/plans/README.md` wskazujące na legacy pliki. Nowe plany tylko w konwencji `YYYY-MM-DD-slug.md`.
5. **research** — przenieś odpowiednie pliki z `docs/analysis/` tylko gdy to wyraźnie research (nie roadmap, nie feature spec); nazwy `YYYY-MM-DD-slug.md`; resztę zostaw i ewentualnie linkuj z README.
6. Zaktualizuj **wszystkie** linki w repo wskazujące na stare ścieżki.
7. Stare ścieżki: zostaw **stub** z jednym akapitem redirect (np. root `BUGS.md` → `docs/issues/...`) albo usuń po aktualizacji linków.

## docs/README.md

Zaktualizuj sekcję struktury katalogów — dodaj `issues/`, `reviews/`, `research/` obok istniejących `plans/`, `features/`, `analysis/`.

## Po wdrożeniu — raport

Na końcu odpowiedzi podaj:
1. Listę utworzonych / przemianowanych plików
2. Tabelę indeksów (ile wpisów w każdym README)
3. Zmiany w `CLAUDE.md`
4. Linki wymagające ręcznej weryfikacji (jeśli jakieś)
5. Sugerowany następny numer `NNN` w `docs/issues/` (tylko issues mają ID w nazwie pliku)

Nie twórz commita ani PR — tylko zmiany w working tree.
```

---

## Uwagi dla operatora (Ty)

### Kolejność we wdrożeniu w 4 repo

1. **gear-stack** (źródło prawdy) — pierwszy; ewentualnie popraw ten prompt po pierwszym przebiegu
2. Pozostałe 3 klony — ten sam prompt; AI dostosuje migrację do stanu każdego repo

### Co może różnić się między klonami

- Zawartość `docs/plans/` i `docs/analysis/`
- Czy istnieje `BUGS.md` / stara struktura `docs/issues/`
- Numeracja `NNN` — **tylko w `docs/issues/`**, per repo (nie synchronizuj ID między klonami)

### Spójność między klonami

- Ta sama konwencja nazw i statusów (`NNN` tylko w `docs/issues/`)
- Ta sama struktura README + szablon nagłówka pliku
- Ta sama sekcja w `CLAUDE.md`

### Opcjonalnie po wdrożeniu we wszystkich 4

- Przegląd programu reviews: skopiować zestaw plików `docs/reviews/2026-*-security-*.md` z gear-stack lub wygenerować na nowo per repo
