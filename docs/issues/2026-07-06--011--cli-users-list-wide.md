# CLI `users list` — flaga `--wide` (jak ops-monitor)

**Status:** `done`  
**Created:** 2026-07-06  
**Source:** [ops-monitor/backend/cli/commands/users.py](../../../ops-monitor/backend/cli/commands/users.py) (`users list`, ok. linii 332–509)  
**Backport:** [backport-progress.md](../../../backport-progress.md)

## Problem

`./exec.sh users list` nie ma parametryzacji wyświetlania jak w **ops-monitor**:

- brak `--wide` / `--no-wide` / `-w` (pełne ID zamiast `truncate_id`, email bez obcinania kolumny)
- `--detailed` to zwykły `bool` — brak interaktywnego promptu „Show detailed info…?” / „Show full IDs and emails?” gdy nie użyto `--json`

## Oczekiwane zachowanie

| Flaga | Efekt |
|-------|--------|
| `--wide` | Pełne UUID w kolumnie ID; kolumna Email bez `max_width` / `ellipsis` |
| `--no-wide` | Domyślne skrócone ID (`truncate_id`) |
| `--detailed` / `--no-detailed` | Kolumny Email Verified, 2FA |
| (interaktywnie) | Przy braku `--json` i bez jawnych flag — `typer.confirm` dla `detailed` i `wide` |
| `--json` | Pełne dane; pomija prompty interaktywne |

## Zakres zmian

- [x] `backend/cli/commands/users.py` — komenda `list` i `_users_list_async`
- [x] Backport z ops-monitor (dostosować tylko jeśli różni się import/formatowanie)

## Weryfikacja

```bash
./exec.sh users list
./exec.sh users list --wide --detailed
./exec.sh users list --json
```
