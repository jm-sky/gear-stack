# CLI `users delete` — soft/hard delete (jak family-recipes)

**Status:** `done`  
**Created:** 2026-07-06  
**Source:** [family-recipes/backend/cli/commands/users.py](../../../family-recipes/backend/cli/commands/users.py) (`users delete`, ok. linii 554–691)  
**Backport:** [backport-progress.md](../../../backport-progress.md)

## Problem

Obecna implementacja w `backend/cli/commands/users.py`:

- **brak** flagi `--hard` — zawsze fizyczne `db.delete(user_db)` (omija `UserRepository.delete_user` i GDPR soft delete)
- brak rozróżnienia komunikatów soft vs hard delete
- domyślnie powinno być **soft delete** (dezaktywacja + anonimizacja PII przez repozytorium)

Repozytorium (`auth/repositories.py`) już obsługuje `delete_user(user_id, soft_delete=True)` z pełnym GDPR cleanup — CLI tego nie używa.

## Oczekiwane zachowanie

| Tryb | Flaga | Efekt |
|------|-------|--------|
| Soft (domyślny) | — | `repo.delete_user(id, soft_delete=True)` — anonimizacja, `token_version++`, OAuth/2FA cleanup |
| Hard | `--hard` | `repo.delete_user(id, soft_delete=False)` — trwałe usunięcie z bazy |

Dodatkowo:

- osobne komunikaty ostrzegawcze dla soft vs hard w trybie interaktywnym
- osobne komunikaty sukcesu („soft-deleted” vs „permanently deleted”)
- `_delete_user_from_db(user_id, *, hard: bool = False)` przez `UserRepository`, nie raw SQLAlchemy delete

**Uwaga:** W family-recipes hard delete czyści też dane rodzin użytkownika — w gear-stack backportować tylko warstwę CLI + repozytorium (bez modułu family).

## Zakres zmian

- [x] `users delete` — dodać `--hard`
- [x] `_users_delete_async` — parametr `hard`, komunikaty soft/hard
- [x] `_delete_user_from_db` — użyć `UserRepository.delete_user(soft_delete=not hard)`
- [x] Usunąć bezpośrednie `db.delete(user_db)` z CLI

## Weryfikacja

```bash
./exec.sh users delete test@example.com          # soft — email do ponownego użycia
./exec.sh users delete test@example.com --hard --yes   # hard — rekord znika z DB
```
