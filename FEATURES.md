# Gear Stack - Lista Funkcjonalności

## 📋 O Projekcie

Gear Stack to zaawansowana aplikacja webowa do zarządzania ekwipunkiem survivalowym, plecakami bug-out oraz sprzętem outdoorowym. Aplikacja działa w architekturze full-stack z obsługą wielu użytkowników, synchronizacją w chmurze i zaawansowanymi funkcjami organizacyjnymi.

**Wersja:** 2.12.0

---

## 🔐 Bezpieczeństwo i Uwierzytelnianie

### Zarządzanie Użytkownikami
- ✅ **Rejestracja i logowanie** - klasyczna autentykacja email/hasło z bezpiecznym hashowaniem (bcrypt)
- ✅ **Weryfikacja email** - potwierdzanie adresu email dla zwiększenia bezpieczeństwa
- ✅ **Zarządzanie hasłem** - resetowanie zapomnianego hasła, zmiana hasła dla zalogowanych
- ✅ **Zarządzanie sesjami** - tokeny JWT z automatycznym odświeżaniem, bezpieczne wylogowanie
- ✅ **Usuwanie konta** - zgodne z RODO, z potwierdzeniem (soft delete)

### OAuth 2.0 - Logowanie przez Social Media
- ✅ **Google OAuth** - logowanie przez konto Google
- 🔄 **GitHub OAuth** - planowane wsparcie dla GitHub
- ✅ **Automatyczne avatary** - zdjęcia profilowe z dostawców OAuth
- ✅ **Ochrona CSRF** - zabezpieczenie przez parametr state

### Uwierzytelnianie Dwuskładnikowe (2FA)
- ✅ **TOTP (Time-based OTP)** - wsparcie dla aplikacji typu Google Authenticator, Authy
- ✅ **WebAuthn** - wsparcie dla passkeys i kluczy sprzętowych (YubiKey, itp.)
- ✅ **Kody zapasowe** - na wypadek utraty dostępu do urządzenia 2FA
- ✅ **Zarządzanie metodami 2FA** - dodawanie, usuwanie, wyświetlanie statusu bezpieczeństwa

### Dodatkowe Zabezpieczenia
- ✅ **Rate Limiting** - ochrona przed atakami brute-force
- ✅ **reCAPTCHA v3** - niewidoczna ochrona przed botami (score-based)
- ✅ **CORS Configuration** - bezpieczne zapytania cross-origin
- ✅ **Ochrona przed SQL Injection** - parametryzowane zapytania przez SQLAlchemy
- ✅ **Ochrona przed XSS** - walidacja i sanityzacja danych wejściowych

---

## 🎒 Zarządzanie Ekwipunkiem

### System Kontenerów
- ✅ **Wiele typów kontenerów** - plecaki bug-out, zestawy EDC, get-home bags, apteczki, sprzęt kempingowy, własne typy
- ✅ **Hierarchiczna organizacja** - kontenery mogą zawierać inne kontenery (zagnieżdżone plecaki, saszetki)
- ✅ **Wizualne rozróżnienie** - przypisanie kolorów do kontenerów (10+ kolorów)
- ✅ **Metadane kontenerów** - typ, opis, waga podstawowa, kodowanie kolorami
- ✅ **Detekcja cykli** - zapobiega cyklicznym odwołaniom w zagnieżdżonych kontenerach
- ✅ **Klonowanie kontenerów** - duplikowanie kontenerów ze wszystkimi przedmiotami i zagnieżdżonymi kontenerami

### Zarządzanie Przedmiotami
- ✅ **Bogate dane przedmiotów:**
  - Podstawowe: nazwa, ilość, waga (z wyborem jednostki: g, kg, oz, lb)
  - Organizacja: kategoria, priorytet, status (posiadane/brakujące/do kupienia)
  - Metadane: marka, notatki, data ważności
  - Zaawansowane: flaga materiałów zużywalnych, flaga noszenia, własne kategorie
- ✅ **Inteligentna kategoryzacja** - automatyczne rozpoznawanie kategorii na podstawie nazwy przedmiotu
- ✅ **Śledzenie statusu** - oznaczanie jako posiadane, brakujące lub do kupienia
- ✅ **Poziomy priorytetu** - niski, średni, wysoki, krytyczny
- ✅ **Śledzenie daty ważności** - monitorowanie materiałów zużywalnych
- ✅ **Dodawanie istniejących przedmiotów** - dodawanie przedmiotów z innych kontenerów przez selektor katalogu
- ✅ **Rozpoznawanie parametrów** - automatyczne wykrywanie marki i koloru z nazw przedmiotów

### Analityka i Statystyki
- ✅ **Obliczenia wagi:**
  - Całkowita waga plecaka z rekursywnym obliczaniem dla zagnieżdżonych kontenerów
  - Rozkład wagi według kategorii
  - Śledzenie wagi podstawowej vs. materiałów zużywalnych
- ✅ **Wskaźniki gotowości** - procent kompletności zestawu (posiadane vs. brakujące)
- ✅ **Wykresy pierścieniowe (donut)** - wizualny rozkład wagi lub ilości według kategorii
- ✅ **Statystyki przedmiotów** - liczenie według statusu, kategorii lub priorytetu

### Wyszukiwanie i Filtrowanie
- ✅ **Inteligentne wyszukiwanie** - znajdowanie przedmiotów po nazwie, marce lub notatkach we wszystkich kontenerach
- ✅ **Filtrowanie wielokryteriowe** - filtrowanie według kategorii, statusu, priorytetu lub kontenera
- ✅ **Opcje sortowania** - sortowanie według nazwy, wagi, daty ważności lub priorytetu
- ✅ **Podświetlanie przedmiotów przeterminowanych** - wizualne ostrzeżenia
- ✅ **Strona "Wszystkie przedmioty"** - dedykowana strona pokazująca wszystkie przedmioty ze wszystkich kontenerów
- ✅ **Strona planowania zakupów** - zarządzanie przedmiotami do kupienia i wkrótce przeterminowanymi

### Import/Export
- ✅ **Export/Import JSON** - pełna kopia zapasowa i przywracanie danych
- ✅ **Export do Markdown dla AI** - export kontenerów do formatu markdown dla przetwarzania przez AI
  - Strukturalny format z metadanymi (waga, marka, kolor, status)
  - Wsparcie dla zagnieżdżonych kontenerów z obliczonymi wagami
  - Legenda wyjaśniająca strukturę danych
  - Kopiowanie jednym kliknięciem do schowka
- ✅ **Import z Markdown** - import kontenerów z plików markdown
- ✅ **Transfer między urządzeniami** - export z jednego urządzenia, import na drugim

### Galeria Zdjęć Przedmiotów
- ✅ **Upload zdjęć** - możliwość dodawania zdjęć do przedmiotów (wymaga uprawnień admina)
- ✅ **Wiele zdjęć na przedmiot** - galeria obrazów dla każdego przedmiotu
- ✅ **Zmiana kolejności** - drag & drop do zmiany kolejności zdjęć
- ✅ **Główne zdjęcie** - oznaczanie zdjęcia jako głównego dla przedmiotu
- ✅ **Usuwanie zdjęć** - możliwość usunięcia pojedynczych zdjęć z galerii
- ✅ **Storage adapter pattern** - wsparcie dla local filesystem i S3 (Scaleway)
- ✅ **Automatyczne przetwarzanie** - resize, optymalizacja JPEG, walidacja formatów
- ✅ **Limity** - maksymalny rozmiar pliku (10 MB), maksymalna liczba zdjęć na przedmiot (10)
- 🔄 **Automatyczne pobieranie zdjęć** - integracja z wyszukiwarkami obrazów (planowane)

### Cloud Storage (S3)
- ✅ **Scaleway S3 Integration** - wsparcie dla Scaleway jako providera S3
- ✅ **Local storage fallback** - lokalny filesystem dla środowiska deweloperskiego
- ✅ **Konfiguracja przez ENV** - elastyczna konfiguracja przez zmienne środowiskowe
- ✅ **Storage type selection** - wybór między local a S3 przez `STORAGE_TYPE`
- ✅ **Przyszłe rozszerzenia** - gotowość na inne providery (AWS S3, MinIO, itp.)

---

## 👤 Profil Użytkownika

- ✅ **Zarządzanie profilem** - aktualizacja imienia, emaila i preferencji
- ✅ **Wsparcie dla avatarów** - dostawcy OAuth automatycznie dostarczają zdjęcia profilowe (Gravatar jako fallback)
- ✅ **Preferowane ustawienia** - jednostki wagi, język, motyw, preferencje wyświetlania
- ✅ **Ustawienia bezpieczeństwa** - zarządzanie metodami 2FA, wyświetlanie statusu bezpieczeństwa

---

## 🔧 Panel Administracyjny

### Admin Dashboard (`/admin`)
- ✅ **Centralny panel admina** - przegląd wszystkich funkcji administracyjnych
- ✅ **Statystyki** - szybki dostęp do zarządzania użytkownikami, kontenerami i przedmiotami
- ✅ **Ochrona dostępu** - wymagane uprawnienia admina (`requiresAdmin: true`)

### Zarządzanie Użytkownikami (`/admin/users`)
- ✅ **Lista wszystkich użytkowników** - przegląd kont z paginacją
- ✅ **Wyszukiwanie użytkowników** - szybkie wyszukiwanie po nazwie lub emailu
- ✅ **Promowanie/degradowanie adminów** - zarządzanie uprawnieniami administratora
- ✅ **Usuwanie użytkowników** - możliwość usunięcia konta użytkownika z potwierdzeniem
- ✅ **Statusy użytkowników** - widoczność statusów: aktywny/nieaktywny, zweryfikowany/niezweryfikowany, admin/user
- ✅ **Sortowanie i filtrowanie** - po dacie utworzenia, statusie, uprawnieniach

### Zarządzanie Kontenerami (`/admin/containers`)
- ✅ **Lista wszystkich kontenerów** - przegląd kontenerów wszystkich użytkowników
- ✅ **Wyszukiwanie kontenerów** - po nazwie, typie, autorze
- ✅ **Informacje o kontenerach** - typ, autor, status publiczny/prywatny, liczba przedmiotów
- ✅ **Usuwanie kontenerów** - możliwość usunięcia kontenera z potwierdzeniem
- ✅ **Filtrowanie** - po typie kontenera, statusie publicznym/prywatnym, autorze

### Zarządzanie Przedmiotami (`/admin/items`)
- ✅ **Lista wszystkich przedmiotów** - przegląd przedmiotów ze wszystkich kontenerów
- ✅ **Wyszukiwanie przedmiotów** - po nazwie, kategorii, kontenerze, autorze
- ✅ **Szczegółowe informacje** - nazwa, kategoria, kontener, autor, ilość, waga, status, priorytet
- ✅ **Usuwanie przedmiotów** - możliwość usunięcia przedmiotu z potwierdzeniem
- ✅ **Sortowanie** - po wszystkich kolumnach (nazwa, waga, data utworzenia, itp.)

---

## 🌐 Wielojęzyczność (i18n)

- ✅ **Pełne wsparcie dla języków** - angielski i polski
- ✅ **Automatyczne wykrywanie języka** - z ustawień przeglądarki
- ✅ **Ręczne przełączanie języka** - w ustawieniach
- ✅ **Pełna lokalizacja** - wszystkie teksty UI, komunikaty walidacji i emaile

---

## 🎨 Wygląd i Doświadczenie Użytkownika

### Motywy
- ✅ **Tryb ciemny (Dark Mode)** - pełne wsparcie z automatycznym wykrywaniem preferencji systemowych
- ✅ **Persystencja motywu** - ustawienia zapisywane per użytkownik
- ✅ **Ikony kategorii** - dedykowane ikony dla każdej kategorii przedmiotów
- ✅ **Kolory kontenerów** - przypisywanie kolorów dla wizualnego odróżnienia

### Responsywność
- ✅ **Mobile-first design** - projektowanie najpierw dla urządzeń mobilnych
- ✅ **Adaptacyjny layout** - dostosowywanie się do różnych rozmiarów ekranów
- ✅ **Touch-friendly** - przyjazne dla ekranów dotykowych

---

## ⚡ Funkcje Produktywności

- ✅ **Szybkie wprowadzanie przedmiotów** - inteligentne domyślne wartości i skróty klawiszowe
- ✅ **Rozszerzalne wiersze** - rozwijanie w tabelach przedmiotów, aby zobaczyć zawartość zagnieżdżonych kontenerów
- ✅ **Preferowana jednostka wagi** - ustawienie użytkownika dla spójnego wyświetlania wag
- ✅ **Limit maksymalnej wagi** - ustawianie maksymalnej wagi dla kontenerów z wizualnymi ostrzeżeniami
- ✅ **Strona 404** - przyjazna dla użytkownika strona "nie znaleziono" z sugestiami nawigacji
- ✅ **Footer i strony prawne** - informacje o cookies, zgodność z RODO, polityka prywatności

---

## 🏗️ Architektura Techniczna

### Frontend
- **Vue 3.5+** z TypeScript i Composition API
- **Pinia** - zarządzanie stanem
- **Vue Router** - nawigacja
- **TailwindCSS v4** + shadcn-vue
- **VeeValidate + Zod** - walidacja formularzy
- **TanStack Query** - zarządzanie stanem serwera
- **vue-i18n** - internacjonalizacja

### Backend
- **FastAPI** (Python) z async/await
- **PostgreSQL** - baza danych
- **SQLAlchemy ORM** - z wsparciem async
- **JWT** - autentykacja z refresh tokens
- **Rate limiting** - ochrona przed nadmiernym ruchem
- **Modularna architektura** - auth, two-factor, email

### Infrastruktura
- **Docker** - konteneryzacja
- **Nginx** - reverse proxy
- **Docker Compose** - orkiestracja usług

---

## 📊 Persystencja Danych

### Hybrydowa Architektura
- ✅ **Client-side** - `localStorage` dla funkcjonalności offline-first
- ✅ **Server-side** - baza PostgreSQL dla synchronizacji między urządzeniami
- ✅ **Automatyczna synchronizacja** - zmiany synchronizują się z chmurą gdy online
- ✅ **Rozwiązywanie konfliktów** - inteligentne łączenie zmian offline

---

## 🔮 Planowane Funkcje (Roadmap)

### Wysokopriorytetowe
- 🔄 **Edycja inline** - szybka edycja przedmiotów bezpośrednio na liście
- 🔄 **Drag & drop** - ręczne zmienianie kolejności przedmiotów

### Średniopriorytetowe
- 🔄 **Zarządzanie markami** - własne marki z kolorami
- 🔄 **Wsparcie dla walut** - ceny w różnych walutach
- 🔄 **Markdown w notatkach** - formatowane notatki

### Backend i Online
- 🔄 **Synchronizacja wielourządzeniowa** - dane zsynchronizowane między wszystkimi urządzeniami
- 🔄 **Udostępnianie kontenerów** - między użytkownikami
- 🔄 **Publiczna galeria kontenerów** - przeglądanie zestawów innych użytkowników
- 🔄 **Globalny katalog przedmiotów** - baza wspólnych przedmiotów
- 🔄 **Progressive Web App (PWA)** - instalacja jak natywna aplikacja
- 🔄 **Funkcje AI** - rekomendacje, analiza, optymalizacja
- 🔄 **Upload zdjęć przedmiotów** - wsparcie S3 (Scaleway)

---

## 🎯 Podsumowanie

Gear Stack to zaawansowana, bezpieczna aplikacja do zarządzania ekwipunkiem z:
- 🔐 **Profesjonalnym systemem bezpieczeństwa** (OAuth, 2FA, rate limiting, reCAPTCHA)
- 🎒 **Zaawansowanym zarządzaniem ekwipunkiem** (hierarchia, analityka, eksport AI)
- 🌐 **Pełną internacjonalizacją** (PL/EN)
- 📱 **Responsywnym designem** (mobile-first)
- ☁️ **Hybrydową architekturą** (offline + cloud sync)
- 🚀 **Nowoczesnym stackiem technologicznym** (Vue 3, FastAPI, PostgreSQL)

Idealny dla entuzjastów outdooru, preperów i osób planujących wyprawy survivalowe!
