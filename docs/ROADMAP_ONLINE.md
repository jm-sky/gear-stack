# Roadmap Online - Gear Stack

<!-- 
AI_METADATA:
- Type: Online roadmap (backend/cloud-dependent)
- Requirements: Backend, PostgreSQL, user authentication required
- Status: Active development (auth features completed)
- Related: See ROADMAP_OFFLINE.md for offline/localStorage features
- Total Features: ~30+ features
-->

Lista planowanych funkcjonalności wymagających backendu, bazy danych i/lub autoryzacji użytkowników (online/cloud features).

> 📋 **Zobacz też:** 
> - [ROADMAP.md](./ROADMAP.md) - główny indeks roadmap
> - [ROADMAP_OFFLINE.md](./ROADMAP_OFFLINE.md) - funkcjonalności offline (localStorage)
> - [Features Implementation Plans](./features/README.md) - szczegółowe plany implementacji

---

## 📊 Status Overview

- ✅ **Completed** - Zaimplementowane i przetestowane
- 🚧 **In Progress** - W trakcie implementacji
- 🔄 **Planned** - Zaplanowane, nie rozpoczęte
- ⏸️ **On Hold** - Tymczasowo wstrzymane
- ❌ **Cancelled** - Anulowane

---

## 🔐 Autoryzacja i konta użytkowników

### ✅ Podstawowa autoryzacja
**Status:** ✅ Completed | **Priority:** High | **Complexity:** Large

- ✅ Rejestracja użytkowników (email/password)
- ✅ Logowanie/Wylogowanie
- ✅ Zarządzanie sesją użytkownika
- ✅ Reset hasła
- ✅ Zmiana hasła
- ✅ Weryfikacja email
- ✅ 2FA (TOTP + WebAuthn/Passkeys)
- ✅ Backend auth module w `backend/app/modules/auth/`
- ✅ Frontend auth module w `src/modules/auth/`

### ✅ reCAPTCHA Bot Protection
**Status:** ✅ Completed | **Priority:** High | **Feature:** [FEATURE-015](./features/FEATURE-015-recaptcha-integration.md)

- ✅ Backend reCAPTCHA service (score-based verification)
- ✅ Frontend reCAPTCHA integration (invisible v3)
- ✅ Protected endpoints: login, register, forgot-password, OAuth callback
- ✅ Auto-loads reCAPTCHA script on app startup
- ✅ Score threshold configuration (0.5 default)
- ✅ Action verification (prevents token reuse)
- ✅ Environment variable configuration fixed (v2.2.1)
- ✅ Comprehensive logging for debugging
- 📝 **Status**: Fully operational with `RECAPTCHA_ENABLED=true`

### ✅ OAuth Social Login
**Status:** ✅ Completed | **Priority:** Medium | **Feature:** [FEATURE-014](./features/FEATURE-014-oauth-authentication.md)

- ✅ Backend OAuth service with Google provider
- ✅ Database migration for OAuth fields
- ✅ Repository methods for OAuth users
- ✅ User model supports nullable passwords
- ✅ OAuth schemas and types defined
- ✅ Auth service OAuth method (`login_with_oauth`)
- ✅ OAuth router endpoints (auth-url, callback)
- ✅ Frontend OAuth integration (OAuthCallbackPage)
- ✅ OAuth button component (already existing)
- ✅ OAuth callback page with state verification
- ✅ Fixed camelCase/snake_case compatibility (v2.2.1)
- ✅ Fixed settings path and logger imports (v2.2.1)
- ✅ Enhanced error handling on frontend (v2.2.1)
- 📝 **Status**: Fully functional end-to-end with Google OAuth

---

## 💾 Synchronizacja i przechowywanie danych

### Synchronizacja między urządzeniami (cloud storage)
**Status:** 🚧 Partially Completed | **Priority:** Medium | **Complexity:** Large

- ✅ Cloud storage dla kontenerów i przedmiotów (PostgreSQL database)
- ✅ API endpoints dla wszystkich operacji CRUD
- ✅ Factory pattern wybierający między localStorage a API
- ✅ Migracja danych z localStorage do API
- 🔄 Automatyczna synchronizacja w tle - planowane
- 🔄 Rozwiązywanie konfliktów przy równoczesnych edycjach - planowane
- ✅ Offline-first approach z synchronizacją przy połączeniu (podstawowa implementacja)

### Wersjonowanie danych (historia zmian)
**Status:** 🔄 Planned | **Priority:** Medium | **Complexity:** Large

- Historia zmian kontenerów i przedmiotów
- Możliwość cofnięcia zmian (undo/redo)
- Porównywanie wersji
- Przywracanie poprzednich wersji
- Audit log wszystkich operacji

---

## 👥 Udostępnianie i współpraca

### Udostępnianie kontenerów
**Status:** 🚧 Partially Completed | **Priority:** Medium | **Complexity:** Medium

- ✅ Publiczne kontenery (`isPublic` flag)
- ✅ Publiczny link do kontenera (`/gear/public/:id`)
- ✅ Przeglądarka publicznych kontenerów (`PublicContainersBrowserPage`)
- ✅ Strona szczegółów publicznego kontenera (`PublicContainerDetailPage`)
- ✅ Publiczna strona szczegółów przedmiotu (`PublicItemDetailPage`)
- ✅ Pole `isPublic` w formularzu kontenera
- ✅ Domyślna widoczność w ustawieniach użytkownika
- 🔄 Udostępnianie nie-publicznych kontenerów przez token w query params - planowane
  - Link w formacie: `/gear/public/:id?token=abc123`
  - Token generowany przez właściciela kontenera
  - Możliwość odwołania tokena
  - Minimalny layout przy share (podobnie jak LighterPack) - uproszczony widok bez pełnego UI
- 🔄 Uprawnienia: tylko odczyt / edycja - planowane
- 🔄 Lista osób, z którymi kontener jest udostępniony - planowane

### ✅ Galeria publiczna list/kontenerów
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Medium

- ✅ Publiczna galeria dostępnych kontenerów (`PublicContainersBrowserPage`)
- ✅ Przeglądanie kontenerów innych użytkowników
- ✅ Filtrowanie i wyszukiwanie w galerii
- ✅ Strona szczegółów publicznego kontenera (`PublicContainerDetailPage`)
- ✅ Publiczna strona szczegółów przedmiotu (`PublicItemDetailPage`)
- ✅ Backend endpoint `/gear/public/containers` dla pobierania publicznych kontenerów
- 🔄 Ocenianie (gwiazdki) kontenerów - planowane
- 🔄 Komentarze pod kontenerami - planowane
- 🔄 Możliwość skopiowania publicznego kontenera do własnych - planowane

---

## 🗂️ Globalny katalog i linkowanie

### Globalny katalog itemów
**Status:** 🔄 Planned | **Priority:** High | **Complexity:** Medium

- Globalny katalog wszystkich przedmiotów (wszystkich użytkowników lub tylko własnych)
- Przeglądarka przedmiotów (globalny katalog)
- Autocomplete przy dodawaniu itemu do kontenera z globalnego katalogu
- Możliwość dodawania przedmiotów z katalogu do własnych kontenerów
- Wersjonowanie przedmiotów w katalogu

### ✅ Wyświetlanie kontenerów na liście wszystkich przedmiotów
**Status:** ✅ Completed | **Priority:** Low | **Complexity:** Small

- ✅ Kontenery (plecaki, torby, itp.) są widoczne na liście wszystkich przedmiotów
- ✅ Plecak to też przedmiot - traktowany jako taki w katalogu
- ✅ Wizualne rozróżnienie między kontenerami a zwykłymi przedmiotami na liście (ikona Box, badge "Container")
- ✅ Możliwość filtrowania: tylko kontenery / tylko przedmioty / wszystkie
- ✅ Kontenery wyświetlane z całkowitą wagą (waga kontenera + zawartość)

### Linkowanie przedmiotów (zmiana w jednym → zmiana w wielu listach)
**Status:** 🔄 Planned | **Priority:** High | **Complexity:** Large

- Przedmioty mogą być linkowane między kontenerami
- Zmiana w jednym miejscu aktualizuje wszystkie referencje
- Możliwość "odlinkowania" przedmiotu (tworzenie kopii)
- Wizualne oznaczenie linkowanych przedmiotów
- Zarządzanie referencjami

---

## ⚙️ Ustawienia użytkownika (wymagające DB)

### Rozszerzone ustawienia użytkownika
**Status:** 🔄 Planned | **Priority:** Medium | **Complexity:** Small

- Domyślna waluta użytkownika (per kontener + domyślna waluta użytkownika)
- Domyślna widoczność nowych kontenerów
- Preferowana jednostka wagi (zapisywana w DB, nie tylko localStorage)
- Dodawanie nowych kategorii (zapisywane w DB)
- Dodawanie firm / marek (brand) - zapisywane w DB
- Uczenie się na podstawie wcześniejszych wyborów użytkownika (dla kategorii)

### ✅ Profil użytkownika - link do Gravatara
**Status:** ✅ Completed | **Priority:** Low | **Complexity:** Small

- ✅ Umożliwienie zapisania URL do obrazu awatara użytkownika
- ✅ Integracja z Gravatar (automatyczne pobieranie awatara na podstawie email)
- ✅ Pole `avatar_url` w profilu użytkownika (już istnieje w DB)
- ✅ Możliwość podania własnego URL do awatara

---

## 🚀 Import/Export - rozszerzenia wymagające DB

### ✅ UUID support dla update workflow
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Medium

**Koncepcja:**
Kontenery i przedmioty już mają UUID - to ich pole `id` (typu `TUUID`). UUID support to system wykorzystujący ten istniejący UUID do identyfikacji podczas importu/eksportu, co umożliwia aktualizację istniejących danych zamiast tworzenia duplikatów.

**Zaimplementowane funkcjonalności:**
- ✅ Export markdown zawiera UUID w formacie `[uuid:xxx]` (opcjonalnie, przez `showUuid`)
- ✅ Import parsuje UUID z markdowna i używa go do identyfikacji kontenerów/przedmiotów
- ✅ Import rozpoznaje UUID i może zaktualizować istniejące kontenery/przedmioty zamiast tylko tworzyć nowe
- ✅ Jeśli UUID istnieje w systemie → aktualizacja istniejącego kontenera/przedmiotu
- ✅ Jeśli UUID nie istnieje → tworzenie nowego kontenera/przedmiotu z tym samym UUID (zachowuje UUID z eksportu)
- ✅ Opcja w import dialog: "Aktualizuj istniejące (po UUID)" vs "Twórz nowe" (już działa)
- ✅ Umożliwia cykl export → edycja w AI → import z zachowaniem relacji i aktualizacją danych
- ✅ Stabilne referencje nawet po zmianie nazw kontenerów (UUID się nie zmienia)
- ✅ Wsparcie dla UUID zarówno w localStorage (local services) jak i w backend API
- ✅ Aktualizacja wszystkich parsowanych pól podczas update (nazwa, opis, waga, URL, cena, waluta)

**Zaimplementowane zmiany techniczne:**
- ✅ Dodać opcjonalne pole `id` do `ICreateContainerDto` i `ICreateItemDto` (frontend)
- ✅ Dodać opcjonalne pole `id` do `ContainerCreate` i `ItemCreate` schemas (backend)
- ✅ Zmodyfikować `createContainer` i `createItem` w local services, aby używały podanego UUID
- ✅ Zmodyfikować backend repository, aby akceptowało opcjonalny UUID
- ✅ Zaktualizować `ImportMarkdownDialog.vue`, aby przekazywał UUID podczas tworzenia i aktualizacji
- ✅ Zaktualizować API services (`gearContainerApiService.ts`, `gearItemApiService.ts`), aby przekazywały UUID do backendu
- ✅ Dodać testy jednostkowe dla UUID support w lokalnych serwisach:
  - `gearContainerLocalService.spec.ts` - 5 testów sprawdzających użycie UUID przy tworzeniu kontenerów
  - `gearItemLocalService.spec.ts` - 5 testów sprawdzających użycie UUID przy tworzeniu przedmiotów
- ✅ Testy parsowania UUID już istnieją w `markdownImportService.spec.ts`

---

## 📊 Statystyki i raporty (multi-user)

### Statystyki i raporty
**Status:** 🔄 Planned | **Priority:** Low | **Complexity:** Medium

- Statystyki użytkownika (liczba kontenerów, przedmiotów, całkowita waga)
- Porównywanie z innymi użytkownikami (opcjonalnie)
- Raporty okresowe
- Analiza trendów w czasie

---

## 🎯 Szablony i presety

### Szablony kontenerów (predefiniowane zestawy)
**Status:** 🔄 Planned | **Priority:** Medium | **Complexity:** Medium

- Predefiniowane szablony kontenerów (UL, bushcraft, EDC, itp.)
- Możliwość tworzenia własnych szablonów
- Udostępnianie szablonów między użytkownikami
- Galeria szablonów
- Tworzenie kontenera z szablonu

### Generowanie gotowych presetów (UL, bushcraft, EDC)
**Status:** 🔄 Planned | **Priority:** Low | **Complexity:** Medium

- AI-powered generowanie presetów na podstawie typu aktywności
- Zapisywanie wygenerowanych presetów jako szablonów
- Możliwość edycji i personalizacji presetów

---

## 🤖 Funkcje AI (wymagające backend)

### Infrastruktura AI
**Status:** 🔄 Planned | **Priority:** Medium | **Complexity:** Large

**Integracja z OpenRouter:**
- OpenRouter jako główny provider AI (dostęp do wielu modeli z różnych providerów)
- Użytkownik wybiera jeden aktywny model z listy 5-15 modeli
- Obsługa własnych tokenów użytkownika (opcjonalnie)
- Billing dokładnie jak OpenRouter (tokeny wejściowe + wyjściowe)
- Zero ukrytych limitów, przejrzyste statystyki
- Brak fallbacku modeli - użytkownik sam wybiera inny model przy niedostępności
- Krótka informacja ostrzegawcza przy pierwszym użyciu (AI działa na odpowiedzialność użytkownika)

**Zarządzanie tokenami:**
- Klucze encrypt-at-rest (szyfrowane w bazie danych)
- Możliwość podmiany lub usunięcia tokena przez użytkownika
- Wsparcie dla tokenów systemowych (dla użytkowników bez własnych tokenów)
- Limity dotyczą tylko użycia tokena systemowego
- Walidacja tokena przy dodawaniu (test API call)

**Konfiguracja kontekstu:**
- Użytkownik wybiera, które pola idą do kontekstu (nazwy, opisy, wagi, kategorie, etc.)
- Brak automatycznego skracania kontekstu
- Komunikat gdy kontekst przekracza limity modelu
- Brak ustawień typu temperature, max_tokens (standardowe parametry w pierwszej wersji)

**Historia AI:**
- Zapisywanie pełnych danych: finalny prompt, modyfikacje, kontekst, odpowiedź
- Metadane: model, provider, timestamp, liczba tokenów, koszt
- Nie zapisujemy template'u promptu (tylko finalny prompt)
- Mechanizm limitu historii (domyślnie 100 wpisów) + automatyczne usuwanie najstarszych
- Użytkownik może przeglądać, filtrować i zarządzać historią

**Cache:**
- Cache dla powtarzalnych operacji (klasyfikacje, embeddingi)
- Zmniejsza koszty oraz liczbę requestów
- TTL: 7 dni dla klasyfikacji, 30 dni dla embedów
- Storage: Redis lub PostgreSQL JSONB

**Logi i monitoring:**
- Logowanie błędów, czasów odpowiedzi, zużycia tokenów
- Podstawowy monitoring stabilności OpenRouter API
- Health check per model (status, response times, success rate)
- Jasne komunikaty przy awarii: "Usługa OpenRouter jest niedostępna - spróbuj ponownie później"
- Integracja z Sentry dla alertów (opcjonalnie)

**Endpointy:**
- `/ai/chat` - Chat completions (generowanie tekstu, sugestie)
- `/ai/classify` - Klasyfikacje (kategorie, worn, consumable)
- `/ai/embed` - Embeddingi (semantic search w przyszłości)
- `/ai/vision` - Vision models (planowane na później)

### Sugestie sprzętu (na podstawie pogody, aktywności itp.)
**Status:** 🔄 Planned | **Priority:** Low | **Complexity:** Large

- Integracja z API pogodowym
- Sugestie sprzętu na podstawie warunków pogodowych
- Sugestie na podstawie typu aktywności
- Personalizacja sugestii na podstawie historii użytkownika
- Wykorzystanie wybranego przez użytkownika modelu AI
- Konfigurowalny kontekst (użytkownik wybiera jakie dane wysłać)

### Analiza listy (co dodać, co usunąć, alternatywy)
**Status:** 🔄 Planned | **Priority:** Low | **Complexity:** Large

- AI-powered analiza kompletności listy
- Sugestie co dodać do kontenera
- Sugestie co można usunąć (redundancja)
- Propozycje alternatywnych przedmiotów
- Analiza wagi i optymalizacja
- Konfigurowalny kontekst (użytkownik wybiera co wysłać do AI)

### Automatyczne oznaczanie kategorii / worn / consumable
**Status:** 🔄 Planned | **Priority:** Low | **Complexity:** Medium

- AI-powered automatyczne kategoryzowanie
- Automatyczne oznaczanie przedmiotów jako "worn" lub "consumable"
- Uczenie się na podstawie wyborów użytkownika
- Zapisywanie preferencji w DB
- Cache dla powtarzalnych klasyfikacji (zmniejsza koszty)

### Konwersja: opis → gotowy kontener
**Status:** 🔄 Planned | **Priority:** Low | **Complexity:** Large

- Konwersja tekstowego opisu na gotowy kontener z przedmiotami
- Integracja przez OpenRouter (dostęp do różnych modeli)
- Zapisywanie wygenerowanych kontenerów w DB
- Historia generowania w bazie danych

---

## 📷 Media i zasoby graficzne

### Upload avatarów użytkownika (wymaga S3)
**Status:** 🔄 Planned | **Priority:** Low | **Complexity:** Medium | **Prerequisite:** S3 Storage

- Możliwość wgrywania własnych avatarów użytkownika
- Alternatywa do Gravatar - użytkownik może wgrać własny obraz
- Automatyczne skalowanie i optymalizacja obrazów
- Limity rozmiaru pliku (np. 2MB max)
- Obsługa formatów: JPG, PNG, WebP
- **Wymaga:** Wdrożenie S3 lub innego cloud storage

### ✅ Zdjęcia przedmiotów
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Medium | **Feature:** [FEATURE-017](./features/FEATURE-017-item-image-gallery-upload.md) | **Version:** v2.11.0

- ✅ Możliwość dodawania zdjęć do przedmiotów w kontenerach (admin-only)
- ✅ Wielokrotne zdjęcia per przedmiot (galeria, max 10 zdjęć)
- ✅ Limity rozmiaru pliku (10 MB default)
- ✅ Automatyczne skalowanie i kompresja (do 1920x1920, JPEG quality 85%)
- ✅ Obsługa formatów: JPG, PNG, WebP, GIF
- ✅ Storage adapter pattern (local filesystem + S3 support)
- ✅ Drag-and-drop upload z VueUse
- ✅ Primary image selection
- ✅ Image reordering (drag-and-drop)
- ✅ FileDropZone component (reusable)
- ✅ Transaction safety (rollback on failure)
- ✅ Docker volume persistence
- ✅ Frontend integration into ItemDetailPage (ItemImageGallery component)
- ✅ ContainerItemImagesGallery component (wyświetlanie obrazków przedmiotów na stronie kontenera)
- ✅ Pole `showItemImages` w kontenerze (opcja pokazywania obrazków w widoku kontenera)
- 🔄 **Show from URL** - opcja dodawania obrazków z URL zamiast uploadu (planowane)
  - Pole URL w formularzu dodawania obrazka
  - Walidacja URL i formatu obrazka
  - Pobieranie i cache'owanie obrazka z URL
  - Alternatywa dla uploadu (szczególnie przydatne dla adminów)
- 🔄 **Primary image w wierszu tabeli** - opcjonalne wyświetlanie miniaturki primary image w tabeli przedmiotów (planowane)
  - Opcja w ustawieniach widoku tabeli
  - Miniaturka primary image w pierwszej kolumnie lub obok nazwy
  - Lazy loading dla wydajności
  - Kliknięcie w miniaturkę → przejście do szczegółów przedmiotu
- 🔄 Limity przestrzeni per użytkownik (nie zaimplementowane - future enhancement)
- **Wsparcie:** Local storage (development) + S3 (production ready)

### Automatyczne wyszukiwanie obrazków dla przedmiotów
**Status:** 🔄 Planned | **Priority:** Medium | **Complexity:** Large | **Feature:** [FEATURE-016](./features/FEATURE-016-automatic-item-image-fetching.md)

- Opcja przy tworzeniu przedmiotu "Wyszukaj obrazki w web"
- Dodatkowa akcja na żądanie dla istniejących przedmiotów
- Ustawienie w ustawieniach użytkownika: "Domyślnie wyszukaj obrazków dla nowych przedmiotów"
- **Dostęp tylko dla adminów** (isAdmin) - funkcjonalność dostępna wyłącznie dla użytkowników z uprawnieniami administratora
- Konfiguracja wielu wyszukiwarek obrazków:
  - Konfiguracja zapisywana na serwerze jako relationship do item
  - Każda wyszukiwarka ma konfigurację:
    - URL sklepu (np. militaria.pl, allegro.pl)
    - Template wyszukiwania (szablon URL z parametrami)
    - Selectors HTML (gdzie w HTML znajdują się obrazki)
    - Lub czyste API (jeśli sklep ma API)
- Wyszukiwanie na podstawie nazwy przedmiotu, marki/firmy i innych parametrów
- Możliwość wyboru obrazu z wyników wyszukiwania
- Cache wyszukanych obrazów
- Fallback do domyślnych ikon gdy brak wyników

### Generowanie SVG z obrazków
**Status:** 🔄 Planned | **Priority:** Low | **Complexity:** Large

- Konwersja obrazów rastowych → SVG
- Tworzenie kompozycji wielu przedmiotów (wizualizacja zawartości plecaka)
- Generowanie layout'u z przedmiotów
- Export do SVG/PNG
- Możliwość edycji kompozycji
- Integracja z biblioteką do wektoryzacji obrazów

---

## 🔍 Monitoring i diagnostyka

### Integracja z Sentry
**Status:** 🚧 Partially Completed | **Priority:** Medium | **Complexity:** Small

**Backend (Python):**
- ✅ Monitoring błędów w czasie rzeczywistym (backend)
- ✅ Automatyczne raportowanie wyjątków i błędów
- ✅ Performance monitoring (transakcje, zapytania DB)
- ✅ Release tracking i deployment notifications
- ✅ Contextualne informacje (user ID, environment, breadcrumbs)
- ✅ Opcjonalne włączenie przez zmienną środowiskową `SENTRY_ENABLED=true`
- ✅ Konfiguracja przez zmienne środowiskowe (DSN, environment, sample rates)

**Frontend (Vue.js):**
- 🔄 **Do omówienia** - Integracja z Sentry dla Vue.js będzie omówiona w przyszłości (nie zaimplementowane na razie)
- 🔄 Source maps dla lepszego debugowania (frontend)
- 🔄 User feedback integration
- 🔄 Browser performance monitoring

**Konfiguracja (Backend):**
- ✅ Opcjonalne włączenie przez zmienną środowiskową `SENTRY_ENABLED=true`
- ✅ Wymagane zmienne: `SENTRY_DSN` (DSN z Sentry dashboard)
- ✅ Opcjonalne zmienne:
  - `SENTRY_ENVIRONMENT` - środowisko (development, staging, production)
  - `SENTRY_RELEASE` - wersja release (domyślnie APP_VERSION)
  - `SENTRY_TRACES_SAMPLE_RATE` - sample rate dla performance monitoring (0.0-1.0, domyślnie 1.0)
  - `SENTRY_PROFILES_SAMPLE_RATE` - sample rate dla profiling (0.0-1.0, domyślnie 1.0)
- ✅ Jeśli `SENTRY_ENABLED=false` lub brak `SENTRY_DSN`, Sentry nie jest inicjalizowane

**Korzyści:**
- Szybsze wykrywanie i diagnozowanie błędów w produkcji
- Proaktywne powiadomienia o problemach przed zgłoszeniem przez użytkowników
- Lepsze zrozumienie zachowania aplikacji w środowisku produkcyjnym
- Tracking wydajności i bottlenecków

---

## 📱 Aplikacja mobilna

### ✅ PWA (Progressive Web App)
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Medium

- ✅ Konwersja aplikacji na PWA (`vite-plugin-pwa`)
- ✅ Manifest.json z konfiguracją PWA
- ✅ Service Worker (Workbox)
- ✅ Instalacja na urządzenia mobilne
- ✅ Offline support z cache'owaniem
- ✅ Komponent `PwaUpdatePrompt` do aktualizacji
- ✅ Runtime caching dla API, fonts, assets
- 🔄 Push notifications - opcjonalnie (planowane)
- ✅ Responsywny design dla urządzeń mobilnych

---

## 📈 Priorytetyzacja

### High Priority (Następne do zrobienia)
1. ✅ **Autoryzacja i konta użytkowników** - High priority, Large complexity (Completed)
2. **Globalny katalog itemów** - High priority, Medium complexity
3. **Linkowanie przedmiotów** - High priority, Large complexity

### Medium Priority
1. **Synchronizacja między urządzeniami** - Medium priority, Large complexity
2. **Udostępnianie kontenerów** - Medium priority, Medium complexity
3. **Szablony kontenerów** - Medium priority, Medium complexity
4. ✅ **PWA** - Medium priority, Medium complexity (Completed)
5. ✅ **Galeria publiczna kontenerów** - Medium priority, Medium complexity (Completed)

### Low Priority
1. ✅ **Profil użytkownika - link do Gravatara** - Low priority, Small complexity (Completed)
2. **Wersjonowanie danych** - Low priority, Large complexity
3. ✅ **Galeria publiczna** - Low priority, Medium complexity (Completed - główna funkcja zaimplementowana, ocenianie i komentarze planowane)
4. **Funkcje AI** - Low priority, Large complexity
5. **Statystyki i raporty** - Low priority, Medium complexity

---

## 📝 Notatki

- Wszystkie funkcjonalności w tym pliku wymagają backendu, bazy danych i/lub autoryzacji
- Backend auth module już istnieje w `backend/app/modules/auth/`
- Complexity: Small (1-2 dni), Medium (3-5 dni), Large (1+ tygodnie)
- Priorytety mogą się zmieniać w zależności od potrzeb użytkowników

