# OAuth GitHub — logowanie przez GitHub

**Status:** `done`  
**Created:** 2026-07-07  
**Moduł:** `auth` (shared core)  
**Source:** [AI-workspace](../../AI-workspace) (`GitHubOAuthProvider`, `OAuthGitHubButton`, `useOAuth.ts`)

## Problem

Brak logowania przez GitHub OAuth — tylko Google i Facebook. AI-workspace ma już pełną implementację (backend + przycisk na login/register).

## Oczekiwane zachowanie

- Przycisk „GitHub” na stronach login i register gdy `VITE_GITHUB_OAUTH_CLIENT_ID` jest ustawiony
- Callback na `/auth/github` (osobna trasa — GitHub App wymaga stałego redirect URI)
- Backend: `GitHubOAuthProvider` w `oauth.py`, zmienne `GITHUB_OAUTH_*` w `.env`

## Zakres

- [x] `backend/app/core/oauth.py` — `GitHubOAuthProvider`
- [x] `backend/app/core/config.py` — pola GitHub w `OAuthSettings`
- [x] `backend/.env.example`, `.env.example` — `GITHUB_OAUTH_*`, `VITE_GITHUB_OAUTH_CLIENT_ID`
- [x] `src/modules/auth/components/OAuthGitHubButton.vue`
- [x] `LoginForm.vue`, `RegisterForm.vue`
- [x] `useOAuth.ts`, `config.ts`, `routes.ts`, `OAuthCallbackPage.vue`
- [x] i18n `continue_with_github`

## Weryfikacja

```bash
# Po ustawieniu GITHUB_OAUTH_* i VITE_GITHUB_OAUTH_CLIENT_ID
pnpm type-check
# Login → GitHub → callback /auth/github → dashboard
```
