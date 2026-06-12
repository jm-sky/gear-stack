# Plan remediacji podatności (GitHub Dependabot)

Naprawa 6 alertów Dependabota (5 unikalnych pakietów). Status: **DONE** (2026-06-12) —
zweryfikowane `type-check` + `lint` + `test:run` (414 zielonych) + `pnpm build` (PWA OK).
`pnpm audit` potwierdza: żaden z 6 alertów nie pozostał. Menedżer pakietów: **pnpm 10.18.3**.

> Zastosowane: `axios` → `^1.17.0` (bezpośredni) oraz `pnpm.overrides` dla shell-quote
> (1.8.4), @babel/plugin-transform-modules-systemjs (7.29.7), serialize-javascript (7.0.5).
>
> **Pozostałe (poza listą Dependabota, wykryte przez `pnpm audit`)** — głównie dev/build,
> do osobnego bumpu: `esbuild` (<0.28.1, via vite), `postcss`, `ws`, `brace-expansion`,
> `fast-uri`. Patrz „Bump wszystkich zależności" niżej.

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
