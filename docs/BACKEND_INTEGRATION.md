# Plan Integracji z Backendem

## 📋 Przegląd

Dokument opisuje plan integracji frontendu `gear-stack` z backendem FastAPI. Integracja będzie wzorowana na projekcie `../test`, który zawiera sprawdzone wzorce implementacji modułu autentykacji i innych funkcjonalności.

## 🎯 Cele

1. **Integracja autentykacji** - Logowanie, rejestracja, zarządzanie sesją
2. **Zachowanie kompatybilności** - Obecna wersja działająca bez backendu musi pozostać funkcjonalna
3. **Kontrola przez feature flag** - Włączanie/wyłączanie integracji przez zmienną środowiskową
4. **Bezpieczna implementacja** - Stopniowe wprowadzanie zmian bez psucia obecnej wersji

## 📁 Struktura Projektów

### Projekt referencyjny: `../test`
```
test/
├── backend/          # FastAPI backend (fastapi-blocks-registry)
│   └── app/
│       └── modules/
│           └── auth/  # Moduł autentykacji
└── frontend/          # Vue frontend (vue-blocks-registry)
    └── src/
        ├── modules/
        │   └── auth/  # Pełna implementacja auth
        └── shared/
            └── services/
                ├── apiClient.ts
                ├── auth.interceptor.ts
                └── error.interceptor.ts
```

### Nasz projekt: `gear-stack`
```
gear-stack/
├── backend/          # Backend skopiowany z test (fastapi-blocks-registry)
└── src/
    └── shared/
        └── services/
            ├── apiClient.ts          # ✅ Już istnieje
            ├── auth.interceptor.ts   # ✅ Już istnieje (podstawowa wersja)
            └── error.interceptor.ts  # ✅ Już istnieje (uproszczona wersja)
```

## 🔍 Analiza Różnic

### Co już mamy w `gear-stack`:
- ✅ Podstawowy `apiClient` z axios
- ✅ Podstawowy `auth.interceptor` (dodaje token do nagłówków)
- ✅ Uproszczony `error.interceptor` (tylko czyszczenie localStorage przy 401)

### Co trzeba dodać z projektu `test`:

#### 1. Moduł Auth (`src/modules/auth/`)
```
modules/auth/
├── components/
│   ├── LoginForm.vue
│   └── RegisterForm.vue
├── composables/
│   └── useAuth.ts (opcjonalnie)
├── config/
│   ├── auth.config.ts
│   └── routes.ts
├── guards/
│   └── authGuard.ts
├── pages/
│   ├── LoginPage.vue
│   └── RegisterPage.vue
├── services/
│   └── authService.ts
├── store/
│   └── useAuthStore.ts
├── types/
│   ├── auth.type.ts
│   └── user.type.ts
└── utils/
    └── token.utils.ts (opcjonalnie)
```

#### 2. Ulepszenia w `shared/services/`
- **error.interceptor.ts**: 
  - Automatyczne odświeżanie tokenów
  - Kolejkowanie żądań podczas refresh
  - Integracja z login modal
- **auth.interceptor.ts**: 
  - Może pozostać bez zmian (już działa)

#### 3. Nowe store w `shared/store/`
- `useTokenRefreshStore.ts` - Zarządzanie stanem odświeżania tokenów

#### 4. Routing
- Dodanie tras `/login`, `/register`
- Implementacja guardów dla chronionych tras
- Meta `requiresAuth` i `requiresGuest`

## 🚩 Feature Flag

### Zmienna środowiskowa: `VITE_ENABLE_BACKEND`

```env
# .env
VITE_ENABLE_BACKEND=false  # Domyślnie wyłączone (tryb offline)
```

### Użycie w kodzie:

```typescript
// src/shared/config/config.ts
export const config = {
  // ... istniejące config
  backend: {
    enabled: import.meta.env.VITE_ENABLE_BACKEND === 'true',
    baseUrl: import.meta.env.VITE_API_BASE_URL ?? '/api',
  },
}

// W komponentach/serwisach
import { config } from '@/shared/config/config'

if (config.backend.enabled) {
  // Użyj backend API
  await authService.login(credentials)
} else {
  // Użyj localStorage (obecna implementacja)
  // ...
}
```

### Strategia implementacji:

1. **Tryb offline (domyślny)**: 
   - `VITE_ENABLE_BACKEND=false`
   - Wszystko działa jak dotychczas (localStorage)
   - Brak zmian w UX

2. **Tryb online**:
   - `VITE_ENABLE_BACKEND=true`
   - Wymagane: `VITE_API_BASE_URL=http://localhost:8000/api`
   - Frontend komunikuje się z backendem
   - Dane synchronizowane z serwerem

## 📝 Plan Implementacji

### Faza 1: Przygotowanie (bez zmian w kodzie)
- [x] Utworzenie dokumentu integracji
- [ ] Utworzenie brancha `feature/backend-integration`
- [ ] Analiza szczegółowa różnic w kodzie

### Faza 2: Infrastruktura (feature flag)
- [ ] Dodanie `VITE_ENABLE_BACKEND` do `.env.example`
- [ ] Rozszerzenie `config.ts` o konfigurację backendu
- [ ] Utworzenie helpera `useBackend()` composable

### Faza 3: Moduł Auth - Typy i Serwisy
- [ ] Skopiowanie typów z `test/frontend/src/modules/auth/types/`
- [ ] Implementacja `authService.ts` (z feature flag)
- [ ] Ulepszenie `error.interceptor.ts` (automatyczny refresh token)
- [ ] Utworzenie `useTokenRefreshStore.ts`

### Faza 4: Moduł Auth - Store i State
- [ ] Implementacja `useAuthStore.ts` (Pinia)
- [ ] Integracja z localStorage (fallback dla trybu offline)
- [ ] Synchronizacja tokenów między store a localStorage

### Faza 5: Moduł Auth - UI
- [ ] Komponenty: `LoginForm.vue`, `RegisterForm.vue`
- [ ] Strony: `LoginPage.vue`, `RegisterPage.vue`
- [ ] Integracja z istniejącym UI (Shadcn-Vue)

### Faza 6: Routing i Guards
- [ ] Dodanie tras `/login`, `/register`
- [ ] Implementacja `authGuard.ts`
- [ ] Oznaczenie chronionych tras (`meta.requiresAuth`)
- [ ] Redirect logic po logowaniu

### Faza 7: Integracja z istniejącym kodem
- [ ] Warunkowe użycie backendu w istniejących komponentach
- [ ] Migracja danych z localStorage do backendu (opcjonalnie)
- [ ] Obsługa błędów i fallback do trybu offline

### Faza 8: Testy i Dokumentacja
- [ ] Testy Playwright dla flow autentykacji
- [ ] Aktualizacja README.md
- [ ] Dokumentacja zmiennych środowiskowych

## 🧪 Testowanie z Playwright

### Konfiguracja

Plik `playwright.config.ts` powinien być skonfigurowany podobnie jak w projekcie `test`:

```typescript
export default defineConfig({
  testDir: './tests/e2e',
  use: {
    baseURL: 'http://localhost:5173',
  },
  // Serwery uruchamiane ręcznie przed testami
  // lub automatycznie przez webServer (opcjonalnie)
})
```

### Scenariusze testowe

1. **Rejestracja użytkownika**
   - Wypełnienie formularza
   - Weryfikacja sukcesu
   - Sprawdzenie przekierowania

2. **Logowanie**
   - Poprawne dane
   - Niepoprawne dane
   - Sprawdzenie tokenu w localStorage

3. **Chronione trasy**
   - Próba dostępu bez logowania
   - Przekierowanie do login
   - Dostęp po zalogowaniu

4. **Odświeżanie tokenu**
   - Symulacja wygasłego tokenu
   - Automatyczne odświeżenie
   - Retry oryginalnego żądania

5. **Wylogowanie**
   - Czyszczenie tokenów
   - Przekierowanie do login

### Uruchamianie testów

```bash
# Uruchom backend i frontend ręcznie
cd backend && python main.py  # Port 8000
cd frontend && pnpm dev        # Port 5173

# W innym terminalu
pnpm exec playwright test
```

## 🔄 Migracja Danych (Opcjonalnie)

Gdy użytkownik przełączy się z trybu offline na online, można zaimplementować migrację danych:

1. **Eksport z localStorage** - Użytkownik może wyeksportować dane jako JSON
2. **Import przez API** - Endpoint `/api/containers/import` przyjmuje JSON
3. **Automatyczna synchronizacja** - Opcjonalnie: automatyczne wysłanie danych przy pierwszym logowaniu

## 🚨 Uwagi i Ostrzeżenia

1. **Nie psuj obecnej wersji** - Wszystkie zmiany muszą być warunkowe przez feature flag
2. **Fallback do localStorage** - Gdy backend nie jest dostępny, użyj localStorage
3. **Obsługa błędów** - Graceful degradation przy problemach z backendem
4. **Type safety** - Wszystkie typy z backendu powinny być zsynchronizowane
5. **Security** - Tokeny przechowywane bezpiecznie, refresh token rotation

## 📚 Zasoby

- Projekt referencyjny: `../test`
- Backend docs: `backend/README.md`
- FastAPI Blocks Registry: [dokumentacja scaffoldu]
- Vue Blocks Registry: [dokumentacja scaffoldu]

## ✅ Checklist przed merge

- [ ] Feature flag działa poprawnie
- [ ] Tryb offline (bez backendu) działa jak wcześniej
- [ ] Tryb online (z backendem) działa poprawnie
- [ ] Testy Playwright przechodzą
- [ ] Dokumentacja zaktualizowana
- [ ] `.env.example` zawiera wszystkie potrzebne zmienne
- [ ] Brak console errors w trybie offline
- [ ] Brak console errors w trybie online

---

**Data utworzenia**: 2025-01-27  
**Status**: W przygotowaniu  
**Branch**: `feature/backend-integration` (do utworzenia)

