# Roadmap V2 - Gear Stack (Backend/DB/Auth Required)

Lista planowanych funkcjonalności wymagających backendu, bazy danych i/lub autoryzacji użytkowników.

> 📋 **Zobacz też:** 
> - [ROADMAP.md](./ROADMAP.md) - funkcjonalności front-end only (localStorage)
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

### Podstawowa autoryzacja
**Status:** 🔄 Planned | **Priority:** High | **Complexity:** Large

- Rejestracja użytkowników (email/password)
- Logowanie/Wylogowanie
- Zarządzanie sesją użytkownika
- Reset hasła
- Zmiana hasła
- **Uwaga:** Backend auth module już istnieje w `backend/app/modules/auth/`

---

## 💾 Synchronizacja i przechowywanie danych

### Synchronizacja między urządzeniami (cloud storage)
**Status:** 🔄 Planned | **Priority:** High | **Complexity:** Large

- Synchronizacja danych między różnymi urządzeniami użytkownika
- Cloud storage dla kontenerów i przedmiotów
- Automatyczna synchronizacja w tle
- Rozwiązywanie konfliktów przy równoczesnych edycjach
- Offline-first approach z synchronizacją przy połączeniu

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
**Status:** 🔄 Planned | **Priority:** High | **Complexity:** Medium

- Publiczny link do listy/kontenera
- Poziomy widoczności: publiczna / niepubliczna / prywatna
- Udostępnianie kontenerów między użytkownikami
- Uprawnienia: tylko odczyt / edycja
- Lista osób, z którymi kontener jest udostępniony

### Galeria publiczna list/kontenerów
**Status:** 🔄 Planned | **Priority:** Medium | **Complexity:** Medium

- Publiczna galeria dostępnych kontenerów
- Przeglądanie kontenerów innych użytkowników
- Filtrowanie i wyszukiwanie w galerii
- Ocenianie (gwiazdki) kontenerów
- Komentarze pod kontenerami
- Możliwość skopiowania publicznego kontenera do własnych

---

## 🗂️ Globalny katalog i linkowanie

### Globalny katalog itemów
**Status:** 🔄 Planned | **Priority:** Medium | **Complexity:** Medium

- Globalny katalog wszystkich przedmiotów (wszystkich użytkowników lub tylko własnych)
- Przeglądarka przedmiotów (globalny katalog)
- Autocomplete przy dodawaniu itemu do kontenera z globalnego katalogu
- Możliwość dodawania przedmiotów z katalogu do własnych kontenerów
- Wersjonowanie przedmiotów w katalogu

### Linkowanie przedmiotów (zmiana w jednym → zmiana w wielu listach)
**Status:** 🔄 Planned | **Priority:** Medium | **Complexity:** Large

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

---

## 🚀 Import/Export - rozszerzenia wymagające DB

### UUID support dla update workflow
**Status:** 🔄 Planned | **Priority:** Medium | **Complexity:** Medium

- Dodanie pola `uuid` do kontenerów i przedmiotów w DB
- Export zawiera UUID w nagłówku: `## Container [#slug] [uuid:abc-123] (Type)`
- Import rozpoznaje UUID i może zaktualizować istniejące kontenery/przedmioty zamiast tylko tworzyć nowe
- Umożliwia cykl export → edycja w AI → import z zachowaniem relacji
- Stabilne referencje nawet po zmianie nazw kontenerów
- Opcja w import dialog: "Aktualizuj istniejące" vs "Twórz nowe"

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

### Sugestie sprzętu (na podstawie pogody, aktywności itp.)
**Status:** 🔄 Planned | **Priority:** Low | **Complexity:** Large

- Integracja z API pogodowym
- Sugestie sprzętu na podstawie warunków pogodowych
- Sugestie na podstawie typu aktywności
- Personalizacja sugestii na podstawie historii użytkownika

### Analiza listy (co dodać, co usunąć, alternatywy)
**Status:** 🔄 Planned | **Priority:** Low | **Complexity:** Large

- AI-powered analiza kompletności listy
- Sugestie co dodać do kontenera
- Sugestie co można usunąć (redundancja)
- Propozycje alternatywnych przedmiotów
- Analiza wagi i optymalizacja

### Automatyczne oznaczanie kategorii / worn / consumable
**Status:** 🔄 Planned | **Priority:** Low | **Complexity:** Medium

- AI-powered automatyczne kategoryzowanie
- Automatyczne oznaczanie przedmiotów jako "worn" lub "consumable"
- Uczenie się na podstawie wyborów użytkownika
- Zapisywanie preferencji w DB

### Konwersja: opis → gotowy kontener
**Status:** 🔄 Planned | **Priority:** Low | **Complexity:** Large

- Konwersja tekstowego opisu na gotowy kontener z przedmiotami
- Integracja z AI (np. OpenAI API)
- Zapisywanie wygenerowanych kontenerów w DB

---

## 📱 Aplikacja mobilna

### PWA (Progressive Web App)
**Status:** 🔄 Planned | **Priority:** Medium | **Complexity:** Medium

- Konwersja aplikacji na PWA
- Instalacja na urządzenia mobilne
- Offline support z synchronizacją
- Push notifications (opcjonalnie)
- Responsywny design dla urządzeń mobilnych

---

## 📈 Priorytetyzacja

### High Priority (Następne do zrobienia)
1. **Autoryzacja i konta użytkowników** - High priority, Large complexity
2. **Synchronizacja między urządzeniami** - High priority, Large complexity
3. **Udostępnianie kontenerów** - High priority, Medium complexity

### Medium Priority
1. **Globalny katalog itemów** - Medium priority, Medium complexity
2. **Linkowanie przedmiotów** - Medium priority, Large complexity
3. **Szablony kontenerów** - Medium priority, Medium complexity
4. **PWA** - Medium priority, Medium complexity

### Low Priority
1. **Wersjonowanie danych** - Low priority, Large complexity
2. **Galeria publiczna** - Low priority, Medium complexity
3. **Funkcje AI** - Low priority, Large complexity
4. **Statystyki i raporty** - Low priority, Medium complexity

---

## 📝 Notatki

- Wszystkie funkcjonalności w tym pliku wymagają backendu, bazy danych i/lub autoryzacji
- Backend auth module już istnieje w `backend/app/modules/auth/`
- Complexity: Small (1-2 dni), Medium (3-5 dni), Large (1+ tygodnie)
- Priorytety mogą się zmieniać w zależności od potrzeb użytkowników

