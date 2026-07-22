# Konfiguracja 2FA nie działa — API zwraca 404 (podwójny prefix)

**Status:** `verification needed`  
**Created:** 2026-07-08  
**Updated:** 2026-07-08 — dodatkowe błędy kontraktu API (passkey options jako string, lista passkeys, brak registrationToken)  
**Moduł:** `auth` / `two_factor` (backend + frontend)  
**Powiązane:** [plan RWD/UX strony 2FA](../../.cursor/plans/2FA%20mobile%20RWD%20UX-0c2df7b5.plan.md)

## Problem

Na stronie konfiguracji 2FA (`/auth/2fa/setup`) **ani TOTP, ani passkey (WebAuthn / fingerprint)** nie da się skonfigurować. W obu przypadkach frontend pokazuje ogólny błąd (`errors.generic` / toast).

Dotyczy m.in.:

- `POST /api/two-factor/totp/initiate` — start konfiguracji TOTP
- `POST /api/two-factor/webauthn/register/initiate` — rejestracja passkey
- `GET /api/two-factor/status`, `/totp/status`, `/webauthn/status`, `/webauthn/passkeys` — status i lista

## Logi (docker `gear-stack-app`, 2026-07-08 ~11:06–11:07 UTC)

```
INFO: 172.18.0.1 - "GET /api/two-factor/status HTTP/1.1" 404 Not Found
INFO: 172.18.0.1 - "GET /api/two-factor/totp/status HTTP/1.1" 404 Not Found
INFO: 172.18.0.1 - "GET /api/two-factor/webauthn/status HTTP/1.1" 404 Not Found
INFO: 172.18.0.1 - "GET /api/two-factor/webauthn/passkeys HTTP/1.1" 404 Not Found
INFO: 172.18.0.1 - "POST /api/two-factor/webauthn/register/initiate HTTP/1.1" 404 Not Found
INFO: 172.18.0.1 - "POST /api/two-factor/totp/initiate HTTP/1.1" 404 Not Found
```

Moduł 2FA jest załadowany (w logach widać `app.modules.two_factor.service` przy sprawdzaniu statusu użytkownika), ale **żądania HTTP trafiają pod nieistniejące ścieżki**.

## Przyczyna

**Podwójny prefix `/two-factor`** w rejestracji routera FastAPI:

1. [`backend/app/api/router.py`](../../backend/app/api/router.py) — `include_router(..., prefix="/two-factor")`
2. [`backend/app/modules/two_factor/router.py`](../../backend/app/modules/two_factor/router.py) — `APIRouter(prefix="/two-factor", ...)`

Efekt — faktyczne endpointy w OpenAPI:

```
/api/two-factor/two-factor/totp/initiate
/api/two-factor/two-factor/webauthn/register/initiate
/api/two-factor/two-factor/status
...
```

Frontend ([`twoFactorService.ts`](../../src/modules/auth/services/twoFactorService.ts)) woła poprawne ścieżki **bez** drugiego segmentu:

```
/api/two-factor/totp/initiate   → 404
```

Wzorzec w projekcie: prefix tylko w `api/router.py` (np. `auth_router` bez własnego prefixu w module).

## Oczekiwane zachowanie

- `POST /api/two-factor/totp/initiate` → 200 + QR/secret/setupToken
- `POST /api/two-factor/webauthn/register/initiate` → 200 + opcje WebAuthn
- `GET /api/two-factor/status` → 200 + status TOTP/WebAuthn

## Proponowana naprawa

- Usunąć `prefix="/two-factor"` z `APIRouter` w [`backend/app/modules/two_factor/router.py`](../../backend/app/modules/two_factor/router.py) (zostawić prefix w `api/router.py`).
- Alternatywa (gorsza): zmienić wszystkie ścieżki we frontendzie na `/two-factor/two-factor/...` — niezgodne z konwencją API.

## Zakres zmian

- [x] `backend/app/modules/two_factor/router.py` — usunąć duplikat prefixu
- [x] Weryfikacja OpenAPI: ścieżki pod `/api/two-factor/*` (bez podwójnego segmentu) — `localhost:8007`
- [ ] Test integracyjny smoke: `GET /api/two-factor/status` (autoryzowany) ≠ 404
- [ ] Manualnie: TOTP setup + dodanie passkey na `/auth/2fa/setup`

## Weryfikacja

1. `curl -s http://localhost:8000/api/openapi.json | jq '.paths | keys[]' | grep two-factor` — każda ścieżka **jeden** segment `two-factor`.
2. Settings → Zarządzaj 2FA → TOTP: QR się ładuje, weryfikacja kodu działa.
3. Zakładka Passkeys → dodaj passkey (biometria) — bez toastu błędu.
4. Settings → karta Security pokazuje poprawny status 2FA.

## Dodatkowe błędy (2026-07-08 ~12:00, po fixie prefixu)

### Passkey — dodawanie (500)

```
ValidationError: PasskeyRegistrationInitiateResponse.options
  Input should be a valid dictionary [type=dict_type, input_value='{\"rp\": ...}', input_type=str]
```

**Przyczyna:** `options_to_json()` zwraca string JSON, a schema Pydantic oczekuje `dict`.  
**Fix:** `json.loads()` w `webauthn_service.initiate_registration`.

### Passkey — usuwanie (404 `/passkeys/undefined`)

```
DELETE /api/two-factor/webauthn/passkeys/undefined HTTP/1.1" 404
```

**Przyczyna:** backend zwraca `{ passkeys: [...], total: N }`, frontend traktował całą odpowiedź jako tablicę → `passkey.id` = `undefined`.  
**Fix:** `twoFactorService.listPasskeys()` → `response.data.passkeys`.

### Kontrakt frontend ↔ backend (WebAuthn)

Frontend oczekiwał `credentialCreationOptions` / `challenge`, backend zwraca `options` + `registrationToken`.  
**Fix:** dopasowanie typów i `useWebAuthn.ts` — `startRegistration({ optionsJSON: response.options })`, `registrationToken` w complete.

## Uwagi

- To **blokuje** sensowne testowanie poprawek RWD/UX strony 2FA — najpierw naprawić API, potem UX.
- Brak testów integracyjnych routera 2FA w `backend/tests/` (tylko utils) — warto dodać przy fixie.
