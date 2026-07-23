# Plan remediacji podatności (GitHub Dependabot)

Naprawa 6 alertów Dependabota (5 unikalnych pakietów). Status: **DONE** (2026-06-12) —
zweryfikowane `type-check` + `lint` + `test:run` (414 zielonych) + `pnpm build` (PWA OK).
`pnpm audit` potwierdza: żaden z 6 alertów nie pozostał. Menedżer pakietów: **pnpm 10.18.3**.

> **2026-07-22** — GitHub zgłosił kolejną falę: 5 nowych alertów (**5 high**), wszystkie
> tranzytywne, potwierdzone lokalnie przez `pnpm audit`:
> - `brace-expansion` <1.1.16 (via `eslint`→`minimatch`) — DoS (GHSA-3jxr-9vmj-r5cp)
> - `brace-expansion` ≥3.0.0 <5.0.7 (via `@sentry/vite-plugin`/`vite-plugin-pwa`→`glob`→`minimatch`) — tenże GHSA, druga gałąź wersji
> - `js-yaml` ≥4.0.0 <4.3.0 (via `eslint`→`@eslint/eslintrc`) — DoS przez YAML merge-key (GHSA-52cp-r559-cp3m)
> - `shell-quote` ≤1.8.4 (via `npm-run-all2`) — DoS w `parse()` (GHSA-395f-4hp3-45gv); poprzedni override (`<1.8.4`→`^1.8.4`) już nie wystarczał, nowy patch to `1.9.0`
> - `linkify-it` ≤5.0.1 (via **prod** `markdown-it`, używane w AI chat/markdown rendering) — DoS w skanerze `mailto:` (GHSA-v245-v573-v5vm)
>
> Wszystkie naprawione przez rozszerzenie `pnpm.overrides` (patch/minor bumpy, bez majorów):
> `brace-expansion@<1.1.16→^1.1.16`, `brace-expansion@>=3.0.0 <5.0.7→^5.0.7`,
> `js-yaml@>=4.0.0 <4.3.0→^4.3.0`, `shell-quote@<1.9.0→^1.9.0` (zastępuje stary wpis),
> `linkify-it@<5.0.2→^5.0.2`. Zweryfikowane: `pnpm audit` → **No known vulnerabilities found**,
> `type-check`, `lint`, `test:run` (375 zielonych), `pnpm build` (PWA precache 230 wpisów, OK).
> Uwaga przy okazji `pnpm install`: `axios` podbił się w zakresie caret `^1.17.0` → `1.18.0`
> (lockfile refresh, nie ręczna zmiana) — brak zmian w `package.json`.

> Zastosowane: `axios` → `^1.17.0` (bezpośredni) oraz `pnpm.overrides` dla shell-quote
> (1.8.4), @babel/plugin-transform-modules-systemjs (7.29.7), serialize-javascript (7.0.5),
> esbuild (0.28.1, via vite — patrz aktualizacja 2026-07-02 niżej).
>
> **2026-07-02** — `pnpm audit` wykrył kolejny alert (low): `esbuild` <0.28.1 (arbitrary
> file read na dev serverze, tylko Windows), przez `vite`. Naprawione: `vite` bumpnięty
> `^7.3.5` → `^7.3.6` (najnowszy patch w linii 7.x; 7.3.6 akceptuje `esbuild ^0.28.0`) +
> `pnpm.overrides["esbuild@<0.28.1"] = "^0.28.1"`. Zweryfikowane: `type-check`, czysty
> `pnpm build` (PWA precache 266 wpisów, zgodnie z build sprzed zmiany), `pnpm audit` → brak
> alertów (w tym `postcss`/`ws`/`brace-expansion`/`fast-uri` wymienione niżej — już czyste,
> naprawione przy okazji wcześniejszych bumpów tranzytywnych). Vite 8 (rolldown-based,
> major) świadomie pominięty — zbyt ryzykowny bump dla jednego low-severity alertu.

> Tylko `axios` jest zależnością bezpośrednią — resztę naprawiamy przez `pnpm.overrides`
> w `package.json` (wymuszenie wersji w zależnościach tranzytywnych).

## Podsumowanie

| # | Pakiet | Zainst. | Cel | Typ | Metoda |
|---|--------|---------|-----|-----|--------|
| 1 | shell-quote | 1.8.3 | ≥1.8.4 | dev, tranzytywny | override |
| 2–4 | axios | 1.15.0 | ≥1.16.0 (latest 1.17.0) | **prod, bezpośredni** | bump w `dependencies` |
| 5 | @babel/plugin-transform-modules-systemjs | 7.29.0 | ≥7.29.4 (latest 7.29.7) | dev, tranzytywny | override |
| 6 | serialize-javascript | 6.0.2 | ≥7.0.5 (brak patcha w 6.x) | dev, tranzytywny | override |

## Szczegóły i łańcuchy zależności

### 1. shell-quote `quote()` nie escapuje nowych linii — **Critical**
- Łańcuch: `npm-run-all2 8.0.4 → shell-quote 1.8.3`
- Cel: `^1.8.4` (najnowsza 1.8.4). Patch, bez breaking changes.
- Ryzyko: minimalne (narzędzie dev do uruchamiania skryptów).

### 2–4. axios — 3 CVE (MITM via proxy prototype pollution, NO_PROXY bypass dla IPv4-mapped IPv6, wyciek Proxy-Authorization przy redirect HTTP→HTTPS)
- Zależność bezpośrednia: `dependencies.axios: ^1.15.0`.
- Cel: `^1.16.0` (zalecane `^1.17.0` — najnowsza, zawiera wszystkie poprawki).
- Ryzyko: **wymaga weryfikacji** — to klient HTTP całej aplikacji (`src/shared/services/apiClient.ts`,
  interceptory auth/error). 1.15→1.17 to bump minor; API stabilne, ale przetestować logowanie,
  refresh tokenu, interceptory i obsługę błędów.

### 5. @babel/plugin-transform-modules-systemjs — generowanie dowolnego kodu na złośliwym wejściu
- Łańcuch: `@babel/preset-env 7.29.2 (devDependency) → @babel/plugin-transform-modules-systemjs 7.29.0`
- Cel: `^7.29.7`. Patch w obrębie 7.29.x.
- Alternatywa: bump `@babel/preset-env` do najnowszej 7.x (pociągnie naprawiony plugin), ale
  override jest deterministyczny i węższy.
- Ryzyko: minimalne (toolchain build/transform; nie trafia do bundle'a runtime aplikacji Vue).

### 6. serialize-javascript — RCE przez `RegExp.flags` / `Date.prototype.toISOString()`
- Łańcuch: `vite-plugin-pwa 1.2.0 → workbox-build 7.4.0 (peer) → @rollup/plugin-terser 0.4.4 → serialize-javascript 6.0.2`
- **Brak patcha w linii 6.x** (6.0.2 to najnowsza 6.x) → override na `^7.0.5`.
- Ryzyko: **wymaga weryfikacji buildu** — to bump major (6→7) w narzędziu build (terser cache).
  `serialize-javascript` jest używany tylko do serializacji opcji w czasie buildu; API stabilne,
  ale po zmianie uruchomić pełny `pnpm build` (z generacją service workera PWA).

## Proponowana zmiana w `package.json`

```jsonc
{
  "dependencies": {
    // ...
    "axios": "^1.17.0"
  },
  "pnpm": {
    "overrides": {
      "shell-quote@<1.8.4": "^1.8.4",
      "@babel/plugin-transform-modules-systemjs@<7.29.4": "^7.29.7",
      "serialize-javascript@<7.0.0": "^7.0.5"
    }
  }
}
```

> Uwaga: w repo nie ma jeszcze sekcji `pnpm.overrides` — dodajemy ją.

## Procedura wykonania

```bash
# 1. axios (bezpośredni)
pnpm add axios@^1.17.0

# 2. overrides (po dodaniu sekcji pnpm.overrides do package.json)
pnpm install

# 3. Weryfikacja, że wersje się podbiły
pnpm why shell-quote
pnpm why serialize-javascript
pnpm why @babel/plugin-transform-modules-systemjs
pnpm ls axios
```

## Weryfikacja (gate przed mergem)

```bash
pnpm type-check          # TS bez błędów
pnpm lint                # ESLint czysto
pnpm test:run            # testy jednostkowe zielone
pnpm build               # KLUCZOWE: build + generacja SW (PWA) — waliduje serialize-javascript 7.x
pnpm audit               # potwierdzenie braku pozostałych alertów (high/critical)
```

Dodatkowo ręcznie (axios): logowanie (WebAuthn), auto-refresh tokenu, wylogowanie po wygaśnięciu,
poprawna obsługa błędów przez interceptory.

## Kolejność / ryzyko

1. **Najpierw, niskie ryzyko (osobny commit):** shell-quote + @babel/plugin-transform-modules-systemjs
   (tylko toolchain dev). `pnpm install` + `pnpm build` + testy.
2. **axios (osobny commit):** bump + ręczny test ścieżki auth/API.
3. **serialize-javascript (osobny commit):** override 7.x + pełny `pnpm build` z PWA.

Rozbicie na osobne commity ułatwia rollback, gdyby któraś zmiana zepsuła build/runtime.

## Uwagi

- Po mergu Dependabot powinien zamknąć alerty automatycznie po przeskanowaniu nowego `pnpm-lock.yaml`.
- Jeśli `pnpm build` zaprotestuje przy serialize-javascript 7.x (np. wymóg nowszego Node u terser),
  fallbackiem jest bump `vite-plugin-pwa`/`@rollup/plugin-terser` do wersji ciągnącej naprawiony
  `serialize-javascript`, zamiast twardego override.

---

# Bump wszystkich zależności (npm + Python)

## npm — stan

- ✅ **In-range (minor/patch)** — zrobione `pnpm update`: vue 3.5.38, vite 7.3.5, vitest 4.1.8,
  vue-tsc 3.3.4, tailwind 4.x, @tanstack/vue-query, @sentry/vue, vue-i18n, reka-ui, playwright 1.60,
  date-fns i in. Zweryfikowane (type-check, lint, 414 testów, build+PWA).
  - Uwaga: vue-tsc 3.3 zgłasza dwa `@keydown.*` na jednym elemencie jako TS1117 — połączono w
    jeden `handleKeydown` w `ItemHeaderName`/`ContainerHeaderName`.

### npm — pozostałe MAJORY (do zrobienia ostrożnie, pojedynczo, z `type-check`+`lint`+`test`+`build`)

Ranking od najniższego ryzyka. Każdy w osobnym commicie; rollback jeśli psuje.

| Pakiet | Z → Na | Ryzyko | Uwagi |
|--------|--------|--------|-------|
| @vue/tsconfig | 0.8 → 0.9 | niskie | preset tsconfig; sprawdzić `type-check` |
| npm-run-all2 | 8 → 9 | niskie | runner skryptów (`run-p` w `build`); sprawdzić `pnpm build` |
| @sentry/vite-plugin | 4 → 5 | niskie | plugin build (upload sourcemap); sprawdzić `pnpm build` |
| @types/node | 22 → 25 | niskie–średnie | **zostawić na 22** — `engines` wspiera node ^20.19/>=22.12; typy ahead of runtime |
| eslint-plugin-perfectionist | 4 → 5 | średnie | zmiany reguł sortowania → duży diff po `lint --fix` |
| lucide-vue-next | 0.554 → 1.0 | średnie | możliwe zmiany nazw ikon → `type-check` wyłapie brakujące importy |
| eslint | 9 → 10 | średnie | nowe domyślne reguły/flat config; spodziewać się lint-fixów |
| vite | 7 → 8 | **wysokie** | major narzędzia build; konfiguracja/plugin API; pełny `build`+`preview` |
| typescript | 5.9 → 6.0 | **wysokie** | nowe błędy typów w całym repo; robić z dużym buforem czasu |
| zod | 3 → 4 | **wysokie** | breaking API; krytyczna zgodność z `vee-validate`/`@vee-validate/zod` |
| vue-router | 4 → 5 | **wysokie** | major API routera; **zweryfikować, czy 5.x jest przeznaczone dla Vue 3** przed bumpem |

Dodatkowo z `pnpm audit` (poza listą Dependabota, dev/build): `esbuild` (<0.28.1, ciągnięty przez
vite — naprawi się przy vite 8 lub override), `postcss`, `ws`, `brace-expansion`, `fast-uri`.

## Python (backend) — stan: `TODO`

Wymaga uruchomienia kontenera i `pytest` (zob. CLAUDE.md → Backend Testing). Procedura:

```bash
# (katalog NIE zaczyna się od '_' → Docker dozwolony)
docker compose -f backend/docker-compose.yml up -d
# przegląd nieaktualnych
docker exec gear-stack-app pip list --outdated
# bump w backend/requirements.txt (ostrożnie: FastAPI/Pydantic/SQLAlchemy to majory wysokiego ryzyka)
docker compose -f backend/docker-compose.yml up -d --build
docker exec gear-stack-app python -m pytest tests/ -v
docker exec gear-stack-app python -m black . && docker exec gear-stack-app python -m mypy .
```

Kolejność: najpierw patch/minor (bezpieczne CVE), potem majory pojedynczo. Pydantic v1→v2 lub
SQLAlchemy 1.x→2.x (jeśli dotyczy) traktować jako osobne, duże zadania z pełnym przebiegiem testów.
