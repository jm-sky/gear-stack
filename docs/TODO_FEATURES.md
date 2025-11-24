# Features do zaimplementowania - Podsumowanie

**Data aktualizacji:** 2025-01-21  
**Źródło:** [ROADMAP_OFFLINE.md](./ROADMAP_OFFLINE.md) + [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md)

---

## 🎯 ROADMAP_OFFLINE.md (Offline Features)

### 🔴 High Priority

#### 1. ✅ **Dodawanie własnych marek (brand)** - ZAIMPLEMENTOWANE
- **Status:** ✅ Completed
- **Priority:** High
- **Complexity:** Medium
- **Opis:** 
  - ✅ UI w ustawieniach (`BrandsSettingsCard.vue`) - dodawanie, edycja, usuwanie
  - ✅ Lista marek: domyślne (SUGGESTED_BRANDS) + własne użytkownika
  - ✅ Dostępne w autocomplete i rozpoznawaniu parametrów
  - ✅ Zapisywane w localStorage
- **Lokalizacja:** `docs/ROADMAP_OFFLINE.md:214-227`

#### 2. **Edycja bezpośrednio na liście (Inline Editing)**
- **Status:** 🔄 Planned
- **Priority:** High
- **Complexity:** Large
- **Feature:** FEATURE-007
- **Opis:**
  - Szybka edycja bez wchodzenia w formularz
  - Inline editing dla podstawowych pól (nazwa, ilość, status)
  - Szybkie akcje (zmiana statusu, priorytetu) bezpośrednio z listy
- **Lokalizacja:** `docs/ROADMAP_OFFLINE.md:455-461`

#### 3. ✅ **Error handler dla chunk loading errors** - ZAIMPLEMENTOWANE
- **Status:** ✅ Completed
- **Priority:** High
- **Complexity:** Medium
- **Opis:**
  - ✅ Obsługa błędu "ChunkLoadError" (błąd ładowania chunk po deploy)
  - ✅ Dialog z komunikatem o nowej wersji aplikacji (window.confirm)
  - ✅ Przycisk "OK" (odświeża) / "Cancel" (kontynuuje)
  - ✅ Global error handler w `main.ts`
  - ✅ Tłumaczenia PL/EN
- **Lokalizacja:** `docs/ROADMAP_OFFLINE.md:576-596`

---

### 🟡 Medium Priority

#### 4. ✅ **Zintegrowany input wagi z wyborem jednostki** - ZAIMPLEMENTOWANE
- **Status:** ✅ Completed
- **Priority:** Medium
- **Complexity:** Small
- **Opis:**
  - ✅ Komponent `<WeightInputWithUnitPicker>` łączący input wagi z wyborem jednostki
  - ✅ Użycie w `ItemFormFields.vue` i `ContainerFormFields.vue`
  - ✅ Obsługa wszystkich jednostek: g, kg, oz, lb
- **Lokalizacja:** `docs/ROADMAP_OFFLINE.md:130-144`

#### 5. **Oznaczanie kontenerów jako fragmentów rodzica (integral part)**
- **Status:** 🔄 Planned
- **Priority:** Medium
- **Complexity:** Medium
- **Opis:**
  - Kontener może być oznaczony jako "fragment rodzica"
  - Przykład: Bagażnik samochodu, pokrywa plecaka
  - Fragment nie jest liczony jako osobny kontener w statystykach
  - Waga fragmentu zawsze wliczana do rodzica
  - Checkbox w formularzu kontenera
- **Lokalizacja:** `docs/ROADMAP_OFFLINE.md:165-185`

#### 6. 🎯 **Obsługa waluty (currency)** - DO ZROBIENIA ZARAZ
- **Status:** 🚧 Partially Completed
- **Priority:** Medium
- **Complexity:** Medium
- **Opis:**
  - ✅ Pole `currency` dodane do przedmiotów i kontenerów (w typach)
  - ✅ Parsowanie waluty w markdown import (rozpoznawanie PLN, USD, EUR, GBP)
  - 🔄 Domyślna waluta użytkownika w ustawieniach - planowane
  - 🔄 Pole wyboru waluty w formularzach - planowane
  - 🔄 Formatowanie cen używając `Intl.NumberFormat` - planowane
  - 🔄 Wyświetlanie waluty w tabelach i statystykach - planowane
- **Lokalizacja:** `docs/ROADMAP_OFFLINE.md:229-252`

#### 7. **Obsługa Markdown w notatkach**
- **Status:** 🔄 Planned
- **Priority:** Medium
- **Complexity:** Medium
- **Opis:**
  - Formatowanie notatek (pole `notes`) za pomocą Markdown
  - Edytor Markdown z podglądem (split view)
  - Renderowanie Markdown do HTML
  - Wsparcie dla: bold, italic, linki, listy, code blocks
  - Dla przedmiotów (`IGearItem.notes`) i kontenerów (`IGearContainer.description`)
- **Lokalizacja:** `docs/ROADMAP_OFFLINE.md:254-266`

#### 8. 🎯 **Kolejność przedmiotów w kontenerze** - DO ZROBIENIA ZARAZ
- **Status:** 🔄 Planned
- **Priority:** Medium
- **Complexity:** Medium
- **Opis:**
  - Pole `order` (lub `sortOrder`) do przedmiotów
  - Drag & drop w tabeli (preferowane) lub przyciski "Do góry" / "Do dołu"
  - Kolejność zapisywana w localStorage
  - Opcja sortowania według innych kryteriów z możliwością powrotu do kolejności ręcznej
- **Lokalizacja:** `docs/ROADMAP_OFFLINE.md:463-473`

#### 9. 🎯 **Rozszerzenie wykresów na stronie szczegółów kontenera** - DO ZROBIENIA ZARAZ
- **Status:** 🔄 Planned
- **Priority:** Medium
- **Complexity:** Medium
- **Opis:**
  - Wykres kołowy według **ceny** (price) - rozkład kosztów według kategorii
  - Wykres kołowy według **priorytetu** (priority) - rozkład przedmiotów według priorytetu
  - Rozszerzenie przełącznika trybów wykresu o nowe opcje
- **Lokalizacja:** `docs/ROADMAP_OFFLINE.md:491-508`

#### 10. **Obsługa opisów przedmiotów w markdown import**
- **Status:** 🚧 Partially Completed
- **Priority:** Medium
- **Feature:** FEATURE-013
- **Opis:**
  - ✅ Eksport opisów - zaimplementowane (off/inline/newline)
  - 🔄 Parsowanie opisów w imporcie markdown - planowane
  - 🔄 Obsługa zagnieżdżonych nawiasów w opisach - planowane
- **Lokalizacja:** `docs/ROADMAP_OFFLINE.md:340-346`

#### 11. ✅ **Obsługa opisu kontenera w markdown import** - ZAIMPLEMENTOWANE
- **Status:** ✅ Completed
- **Priority:** Medium
- **Opis:**
  - ✅ Parser markdown wykrywa opis kontenera (tekst między nagłówkiem a pierwszą listą)
  - ✅ Opis zapisywany w polu `description` kontenera
  - ✅ Unit tests dla parsowania opisów kontenerów
- **Lokalizacja:** `docs/ROADMAP_OFFLINE.md:347-350`

#### 12. ✅ **Obsługa ceny w markdown import** - ZAIMPLEMENTOWANE
- **Status:** ✅ Completed
- **Priority:** Medium
- **Opis:**
  - ✅ Parser wykrywa ceny w różnych formatach: `100PLN`, `10 PLN`, `10,00 PLN`, `10zł`, `$50`, `50$`
  - ✅ Automatyczne rozpoznawanie waluty (PLN, zł, $, EUR, €, GBP, £)
  - ✅ Cena zapisywana w polu `price` przedmiotu/kontenera
  - ✅ Waluta zapisywana w polu `currency`
  - ✅ Unit tests dla parsowania cen (kontenery i przedmioty)
- **Lokalizacja:** `docs/ROADMAP_OFFLINE.md:351-356`

#### 13. 🎯 **Pokazywanie cen w eksporcie markdown** - DO ZROBIENIA ZARAZ
- **Status:** 🔄 Planned
- **Priority:** Medium
- **Opis:**
  - Opcja w dialogu eksportu: "Pokazywanie cen przedmiotów"
  - Dodatkowe podsumowanie "Do kupienia" na końcu eksportu
- **Lokalizacja:** `docs/ROADMAP_OFFLINE.md:337-339`

---

### 🟢 Low Priority

#### 14. **Funkcje AI z API calls (bez auth)**
- **Status:** 🔄 Planned
- **Priority:** Low
- **Complexity:** Medium
- **Opis:**
  - Sugestie sprzętu (na podstawie pogody, aktywności)
  - Analiza listy (co dodać, co usunąć, alternatywy)
  - Generowanie gotowych presetów (UL, bushcraft, EDC)
  - Konwersja: opis → gotowy kontener
  - Przez API calls bez autoryzacji
- **Lokalizacja:** `docs/ROADMAP_OFFLINE.md:624-632`

#### 15. **Wielowymiarowe wykresy**
- **Status:** 🔄 Planned
- **Priority:** Low
- **Complexity:** High
- **Opis:**
  - Wykresy pokazujące relacje między wymiarami danych
  - Przykłady: Kategoria × Cena, Kategoria × Priorytet, Priorytet × Cena
  - Typy: Heatmap, wykres słupkowy grupowany, wykres bąbelkowy
  - Interaktywne narzędzia (zoom, filtrowanie, tooltips)
- **Lokalizacja:** `docs/ROADMAP_OFFLINE.md:510-523`

---

## 🌐 ROADMAP_ONLINE.md (Online Features)

### 🔴 High Priority

#### 16. **Synchronizacja między urządzeniami (cloud storage)**
- **Status:** 🚧 Partially Completed
- **Priority:** High
- **Complexity:** Large
- **Opis:**
  - ✅ Cloud storage dla kontenerów i przedmiotów (PostgreSQL database)
  - ✅ API endpoints dla wszystkich operacji CRUD
  - ✅ Factory pattern wybierający między localStorage a API
  - ✅ Migracja danych z localStorage do API
  - 🔄 Automatyczna synchronizacja w tle - planowane
  - 🔄 Rozwiązywanie konfliktów przy równoczesnych edycjach - planowane
  - ✅ Offline-first approach z synchronizacją przy połączeniu (podstawowa implementacja)
- **Lokalizacja:** `docs/ROADMAP_ONLINE.md:81-88`

#### 17. **Udostępnianie kontenerów**
- **Status:** 🚧 Partially Completed
- **Priority:** High
- **Complexity:** Medium
- **Opis:**
  - ✅ Publiczne kontenery (`isPublic` flag)
  - ✅ Publiczny link do kontenera (`/gear/public/:id`)
  - ✅ Przeglądarka publicznych kontenerów
  - ✅ Strona szczegółów publicznego kontenera
  - 🔄 Udostępnianie nie-publicznych kontenerów przez token w query params - planowane
  - 🔄 Uprawnienia: tylko odczyt / edycja - planowane
  - 🔄 Lista osób, z którymi kontener jest udostępniony - planowane
- **Lokalizacja:** `docs/ROADMAP_ONLINE.md:103-110`

---

### 🟡 Medium Priority

#### 18. **Globalny katalog itemów**
- **Status:** 🔄 Planned
- **Priority:** Medium
- **Complexity:** Medium
- **Opis:**
  - Globalny katalog wszystkich przedmiotów (wszystkich użytkowników lub tylko własnych)
  - Przeglądarka przedmiotów (globalny katalog)
  - Autocomplete przy dodawaniu itemu do kontenera z globalnego katalogu
  - Możliwość dodawania przedmiotów z katalogu do własnych kontenerów
  - Wersjonowanie przedmiotów w katalogu
- **Lokalizacja:** `docs/ROADMAP_ONLINE.md:126-133`

#### 19. **Linkowanie przedmiotów**
- **Status:** 🔄 Planned
- **Priority:** Medium
- **Complexity:** Large
- **Opis:**
  - Przedmioty mogą być linkowane między kontenerami
  - Zmiana w jednym miejscu aktualizuje wszystkie referencje
  - Możliwość "odlinkowania" przedmiotu (tworzenie kopii)
  - Wizualne oznaczenie linkowanych przedmiotów
  - Zarządzanie referencjami
- **Lokalizacja:** `docs/ROADMAP_ONLINE.md:143-150`

#### 20. **Szablony kontenerów (predefiniowane zestawy)**
- **Status:** 🔄 Planned
- **Priority:** Medium
- **Complexity:** Medium
- **Opis:**
  - Predefiniowane szablony kontenerów (UL, bushcraft, EDC, itp.)
  - Możliwość tworzenia własnych szablonów
  - Udostępnianie szablonów między użytkownikami
  - Galeria szablonów
  - Tworzenie kontenera z szablonu
- **Lokalizacja:** `docs/ROADMAP_ONLINE.md:204-211`

#### 21. ✅ **PWA (Progressive Web App)** - ZAIMPLEMENTOWANE
- **Status:** ✅ Completed
- **Priority:** Medium
- **Complexity:** Medium
- **Opis:**
  - ✅ Konwersja aplikacji na PWA (`vite-plugin-pwa`)
  - ✅ Manifest.json z konfiguracją PWA
  - ✅ Service Worker (Workbox)
  - ✅ Instalacja na urządzenia mobilne
  - ✅ Offline support z cache'owaniem
  - ✅ Komponent `PwaUpdatePrompt` do aktualizacji
  - ✅ Runtime caching dla API, fonts, assets
  - 🔄 Push notifications - opcjonalnie (planowane)
  - ✅ Responsywny design dla urządzeń mobilnych
- **Lokalizacja:** `docs/ROADMAP_ONLINE.md:314-321`

#### 22. **Rozszerzone ustawienia użytkownika**
- **Status:** 🔄 Planned
- **Priority:** Medium
- **Complexity:** Small
- **Opis:**
  - Domyślna waluta użytkownika (per kontener + domyślna waluta użytkownika)
  - Domyślna widoczność nowych kontenerów
  - Preferowana jednostka wagi (zapisywana w DB)
  - Dodawanie nowych kategorii (zapisywane w DB)
  - Dodawanie firm / marek (brand) - zapisywane w DB
  - Uczenie się na podstawie wcześniejszych wyborów użytkownika
- **Lokalizacja:** `docs/ROADMAP_ONLINE.md:156-164`

#### 23. **UUID support dla update workflow**
- **Status:** 🔄 Planned
- **Priority:** Medium
- **Complexity:** Medium
- **Opis:**
  - Pole `uuid` do kontenerów i przedmiotów w DB
  - Export zawiera UUID w nagłówku
  - Import rozpoznaje UUID i może zaktualizować istniejące kontenery/przedmioty
  - Umożliwia cykl export → edycja w AI → import z zachowaniem relacji
  - Opcja w import dialog: "Aktualizuj istniejące" vs "Twórz nowe"
- **Lokalizacja:** `docs/ROADMAP_ONLINE.md:178-186`

#### 24. **Zdjęcia przedmiotów (wymaga S3)**
- **Status:** 🔄 Planned
- **Priority:** Medium
- **Complexity:** Medium
- **Prerequisite:** S3 Storage
- **Opis:**
  - Możliwość dodawania zdjęć do przedmiotów w kontenerach
  - Wielokrotne zdjęcia per przedmiot (galeria)
  - Limity przestrzeni per użytkownik
  - Automatyczne skalowanie i kompresja
  - Obsługa formatów: JPG, PNG, WebP
- **Lokalizacja:** `docs/ROADMAP_ONLINE.md:270-279`

#### 25. **Automatyczne wyszukiwanie obrazków dla przedmiotów**
- **Status:** 🔄 Planned
- **Priority:** Medium
- **Complexity:** Large
- **Feature:** FEATURE-016
- **Prerequisite:** Admin access
- **Opis:**
  - Opcja "Wyszukaj obrazki w web" przy tworzeniu przedmiotu
  - Konfiguracja wielu wyszukiwarek obrazków (militaria.pl, allegro.pl, itp.)
  - Wyszukiwanie na podstawie nazwy, marki, parametrów
  - Możliwość wyboru obrazu z wyników
  - Cache wyszukanych obrazów
  - **Dostęp tylko dla adminów**
- **Lokalizacja:** `docs/ROADMAP_ONLINE.md:281-298`

---

### 🟢 Low Priority

#### 26. **Wersjonowanie danych (historia zmian)**
- **Status:** 🔄 Planned
- **Priority:** Low
- **Complexity:** Large
- **Opis:**
  - Historia zmian kontenerów i przedmiotów
  - Możliwość cofnięcia zmian (undo/redo)
  - Porównywanie wersji
  - Przywracanie poprzednich wersji
  - Audit log wszystkich operacji
- **Lokalizacja:** `docs/ROADMAP_ONLINE.md:90-97`

#### 27. **Galeria publiczna list/kontenerów**
- **Status:** 🔄 Planned
- **Priority:** Low
- **Complexity:** Medium
- **Opis:**
  - Publiczna galeria dostępnych kontenerów
  - Przeglądanie kontenerów innych użytkowników
  - Filtrowanie i wyszukiwanie w galerii
  - Ocenianie (gwiazdki) kontenerów
  - Komentarze pod kontenerami
  - Możliwość skopiowania publicznego kontenera do własnych
- **Lokalizacja:** `docs/ROADMAP_ONLINE.md:112-120`

#### 28. **Wyświetlanie kontenerów na liście wszystkich przedmiotów**
- **Status:** 🔄 Planned
- **Priority:** Low
- **Complexity:** Small
- **Opis:**
  - Kontenery (plecaki, torby) widoczne na liście wszystkich przedmiotów
  - Wizualne rozróżnienie między kontenerami a zwykłymi przedmiotami
  - Możliwość filtrowania: tylko kontenery / tylko przedmioty / wszystkie
- **Lokalizacja:** `docs/ROADMAP_ONLINE.md:135-141`

#### 29. **Profil użytkownika - link do Gravatara**
- **Status:** 🔄 Planned
- **Priority:** Low
- **Complexity:** Small
- **Opis:**
  - Umożliwienie zapisania URL do obrazu awatara użytkownika
  - Integracja z Gravatar (automatyczne pobieranie awatara na podstawie email)
  - Pole `avatar_url` w profilu użytkownika (już istnieje w DB)
  - Możliwość podania własnego URL do awatara
- **Lokalizacja:** `docs/ROADMAP_ONLINE.md:166-172`

#### 30. **Statystyki i raporty (multi-user)**
- **Status:** 🔄 Planned
- **Priority:** Low
- **Complexity:** Medium
- **Opis:**
  - Statystyki użytkownika (liczba kontenerów, przedmiotów, całkowita waga)
  - Porównywanie z innymi użytkownikami (opcjonalnie)
  - Raporty okresowe
  - Analiza trendów w czasie
- **Lokalizacja:** `docs/ROADMAP_ONLINE.md:192-198`

#### 31. **Generowanie gotowych presetów (UL, bushcraft, EDC)**
- **Status:** 🔄 Planned
- **Priority:** Low
- **Complexity:** Medium
- **Opis:**
  - AI-powered generowanie presetów na podstawie typu aktywności
  - Zapisywanie wygenerowanych presetów jako szablonów
  - Możliwość edycji i personalizacji presetów
- **Lokalizacja:** `docs/ROADMAP_ONLINE.md:213-218`

#### 32. **Funkcje AI (wymagające backend)**
- **Status:** 🔄 Planned
- **Priority:** Low
- **Complexity:** Large
- **Opis:**
  - Sugestie sprzętu (na podstawie pogody, aktywności)
  - Analiza listy (co dodać, co usunąć, alternatywy)
  - Automatyczne oznaczanie kategorii / worn / consumable
  - Konwersja: opis → gotowy kontener
  - Personalizacja na podstawie historii użytkownika
- **Lokalizacja:** `docs/ROADMAP_ONLINE.md:224-254`

#### 33. **Upload avatarów użytkownika (wymaga S3)**
- **Status:** 🔄 Planned
- **Priority:** Low
- **Complexity:** Medium
- **Prerequisite:** S3 Storage
- **Opis:**
  - Możliwość wgrywania własnych avatarów użytkownika
  - Alternatywa do Gravatar
  - Automatyczne skalowanie i optymalizacja obrazów
  - Limity rozmiaru pliku (np. 2MB max)
  - Obsługa formatów: JPG, PNG, WebP
- **Lokalizacja:** `docs/ROADMAP_ONLINE.md:260-268`

#### 34. **Generowanie SVG z obrazków**
- **Status:** 🔄 Planned
- **Priority:** Low
- **Complexity:** Large
- **Opis:**
  - Konwersja obrazów rastowych → SVG
  - Tworzenie kompozycji wielu przedmiotów (wizualizacja zawartości plecaka)
  - Generowanie layout'u z przedmiotów
  - Export do SVG/PNG
  - Możliwość edycji kompozycji
  - Integracja z biblioteką do wektoryzacji obrazów
- **Lokalizacja:** `docs/ROADMAP_ONLINE.md:300-308`

---

## 📊 Statystyki

### Według priorytetu:
- **High Priority:** 3 funkcje (1 offline + 2 online) - 2 już zaimplementowane ✅
- **Medium Priority:** 20 funkcji (9 offline + 10 online) - 1 już zaimplementowana ✅
- **Low Priority:** 9 funkcji (2 offline + 7 online)

### Zaimplementowane (✅):
1. ✅ Dodawanie własnych marek (brand) - High, Medium
2. ✅ Error handler dla chunk loading errors - High, Medium
3. ✅ Zintegrowany input wagi z wyborem jednostki - Medium, Small
4. ✅ Obsługa opisu kontenera w markdown import - Medium
5. ✅ Obsługa ceny w markdown import - Medium
6. ✅ PWA (Progressive Web App) - Medium, Medium

### Częściowo zaimplementowane (🚧):
1. 🚧 Obsługa waluty (currency) - Medium, Medium (parsowanie w import, brak UI w formularzach) - 🎯 DO ZROBIENIA ZARAZ
2. 🚧 Synchronizacja między urządzeniami - High, Large (storage w bazie, brak automatycznej synchronizacji)
3. 🚧 Udostępnianie kontenerów - High, Medium (publiczne kontenery, brak token-based sharing)

### Według złożoności:
- **Small:** 4 funkcje
- **Medium:** 20 funkcji
- **Large:** 10 funkcji

### Według typu:
- **Offline (localStorage):** 15 funkcji
- **Online (Backend/DB/Auth):** 19 funkcji

---

## 🎯 Rekomendacje

### ✅ Ukończone (High/Medium Priority):
1. ✅ **Dodawanie własnych marek (brand)** - High, Medium - **ZAIMPLEMENTOWANE**
2. ✅ **Error handler dla chunk loading errors** - High, Medium - **ZAIMPLEMENTOWANE**
3. ✅ **Zintegrowany input wagi z wyborem jednostki** - Medium, Small - **ZAIMPLEMENTOWANE**

### Następne do rozpoczęcia (High Priority):
1. **Edycja bezpośrednio na liście** - High, Large (jedyna pozostała High Priority offline)
2. **Synchronizacja między urządzeniami** - High, Large (wymaga backendu)
3. **Udostępnianie kontenerów** - High, Medium (wymaga backendu)

### 🎯 Do zrobienia zaraz (Medium Priority):
1. 🎯 **Obsługa waluty (currency)** - Medium, Medium (częściowo zaimplementowane - brak UI)
2. 🎯 **Kolejność przedmiotów w kontenerze** - Medium, Medium
3. 🎯 **Rozszerzenie wykresów (cena, priorytet)** - Medium, Medium
4. 🎯 **Pokazywanie cen w eksporcie markdown** - Medium, Small

### Quick Wins (Medium Priority, Small/Medium Complexity):
1. **Oznaczanie kontenerów jako fragmentów** - Medium, Medium

---

**Ostatnia aktualizacja:** 2025-01-21

