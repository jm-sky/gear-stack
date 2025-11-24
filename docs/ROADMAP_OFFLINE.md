# Roadmap Offline - Gear Stack

<!-- 
AI_METADATA:
- Type: Offline roadmap (localStorage-based)
- Requirements: localStorage only, no backend/DB/auth needed
- Status: Active development
- Related: See ROADMAP_ONLINE.md for online/backend features
- Total Features: ~50+ features
-->

Lista planowanych funkcjonalności i ulepszeń aplikacji - **offline features** (działające z localStorage, bez potrzeby backendu, bazy danych lub autoryzacji).

> 📋 **Zobacz też:** 
> - [ROADMAP.md](./ROADMAP.md) - główny indeks roadmap
> - [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md) - funkcjonalności wymagające backendu/DB/auth
> - [Features Implementation Plans](./features/README.md) - szczegółowe plany implementacji

---

## 📊 Status Overview

- ✅ **Completed** - Zaimplementowane i przetestowane
- 🚧 **In Progress** - W trakcie implementacji
- 🔄 **Planned** - Zaplanowane, nie rozpoczęte
- ⏸️ **On Hold** - Tymczasowo wstrzymane
- ❌ **Cancelled** - Anulowane

---

## 🌐 Internacjonalizacja

### ✅ Wykrywanie języka (locale) z ustawień przeglądarki
**Status:** ✅ Completed | **Priority:** Medium | **Feature:** [FEATURE-001](./features/FEATURE-001-locale-detection.md)

- ✅ Automatyczne wykrywanie języka użytkownika na podstawie ustawień przeglądarki
- ✅ Fallback do domyślnego języka (np. polski)
- ✅ Możliwość ręcznej zmiany języka w ustawieniach
- ✅ HTML lang attribute automatycznie ustawiany na podstawie wykrytego języka
- ✅ Wykryty język zapisywany w localStorage

### ✅ Preferowana jednostka wagi
**Status:** ✅ Completed | **Priority:** Medium

- ✅ Użytkownik może ustawić preferowaną jednostkę wagi w ustawieniach (g lub kg)
- ✅ Wszystkie wyświetlane wagi na dashboard, w tabelach i kartach będą konwertowane do preferowanej jednostki
- ✅ Formularze nadal mogą używać różnych jednostek, ale wyświetlanie będzie spójne
- ✅ Ustawienie zapisywane w localStorage i synchronizowane w całej aplikacji

### ✅ Dodatkowe jednostki wagi (oz, lb)
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Medium

- ✅ Dodanie jednostek imperialnych: uncje (oz) i funty (lb)
- ✅ Rozszerzenie typu `TGearWeightUnit` o `'oz'` i `'lb'`
- ✅ Aktualizacja funkcji konwersji w `formatWeight.ts`:
  - ✅ Konwersja oz → g (1 oz = 28.3495 g)
  - ✅ Konwersja lb → g (1 lb = 453.592 g)
  - ✅ Konwersja g → oz i g → lb
- ✅ Aktualizacja formularzy (ItemFormFields, ContainerFormFields) - dodanie opcji oz i lb
- ✅ Aktualizacja preferowanej jednostki wagi w ustawieniach - dodanie oz i lb jako opcji
- ✅ Aktualizacja tłumaczeń (PL/EN) dla nowych jednostek
- ✅ Aktualizacja parsera markdown import - rozpoznawanie oz i lb w eksporcie/impocie
- ✅ Aktualizacja walidacji (zod schemas) - dodanie oz i lb do enum
- ✅ Wszystkie wyświetlane wagi będą konwertowane do preferowanej jednostki (w tym oz/lb)

---

## 🎨 UI/UX Ulepszenia

### ✅ Strona z listą wszystkich przedmiotów
**Status:** ✅ Completed | **Priority:** High | **Complexity:** Medium

- ✅ Nowa strona wyświetlająca listę wszystkich przedmiotów ze wszystkich kontenerów
- ✅ Dostępna jako kolejna pozycja w topbar navigation (obok "Kontenery")
- ✅ Tabela przedmiotów z kolumnami:
  - ✅ Kategoria (z ikoną)
  - ✅ Nazwa przedmiotu
  - ✅ Kontener (nazwa kontenera, z którego pochodzi przedmiot, z wizualizacją koloru)
  - ✅ Ilość
  - ✅ Waga
  - ✅ Status
  - ✅ Priorytet
  - ✅ Marka (opcjonalnie, ukryta domyślnie)
  - ✅ Kolor (opcjonalnie, ukryty domyślnie)
- ✅ Możliwość filtrowania i sortowania:
  - ✅ Filtrowanie po kategorii, statusie, priorytecie
  - ✅ Filtrowanie po kontenerze (przez wyszukiwarkę)
  - ✅ Sortowanie po dowolnej kolumnie
- ✅ Możliwość szybkiego przejścia do kontenera, w którym znajduje się przedmiot (kliknięcie w nazwę kontenera)
- ✅ Wyszukiwarka przedmiotów (globalne filtrowanie)
- ✅ Zarządzanie widocznością kolumn z zapisem w localStorage

### ✅ Strona planowania zakupów
**Status:** ✅ Completed | **Priority:** High | **Complexity:** Medium

- ✅ Nowa strona wyświetlająca listę przedmiotów do zakupu i z bliskim terminem ważności
- ✅ Dostępna jako pozycja w topbar navigation (obok "Kontenery" i "Wszystkie przedmioty")
- ✅ Wyświetlanie przedmiotów z statusem "To buy" oraz opcjonalnie z bliskim terminem ważności
- ✅ Sortowanie według priorytetu (critical → high → medium → low)
- ✅ Filtrowanie po kategoriach (wielokrotny wybór)
- ✅ Filtrowanie po budżecie (ogranicza listę do przedmiotów mieszczących się w budżecie)
- ✅ Możliwość dodawania/usuwania pozycji z listy zakupów
- ✅ Podsumowanie listy zakupów z liczbą przedmiotów i całkowitą ceną
- ✅ Eksport listy zakupów jako markdown (z podziałem na priorytety)
- ✅ Wszystkie teksty przetłumaczone przez i18n (PL/EN)
- ✅ Lista zakupów zapisywana w localStorage (persystencja między sesjami)

### ✅ Dedykowane ikony dla kategorii
**Status:** ✅ Completed | **Priority:** High | **Feature:** [FEATURE-002](./features/FEATURE-002-category-icons.md)

- ✅ Na liście przedmiotów - dedykowana ikona do każdej kategorii
- ✅ Ikony dla kategorii: woda, ogień, jedzenie, schronienie, pierwsza pomoc, narzędzia, nawigacja, komunikacja, odzież, higiena, światło, inne
- ✅ Spójny system ikon (Lucide Icons)
- ✅ Ikony wyświetlane w tabelach i selektorach kategorii

### ✅ Kolorowanie kontenerów
**Status:** ✅ Completed | **Priority:** Medium | **Feature:** [FEATURE-003](./features/FEATURE-003-container-colors.md)

- ✅ Możliwość przypisania koloru do kontenera
- ✅ 10 dostępnych kolorów do wyboru (default, blue, green, red, yellow, purple, orange, pink, teal, indigo)
- ✅ Wizualne rozróżnienie kontenerów na liście (kolorowa kropka i ramka)
- ✅ Kolor wyświetlany w kartach kontenerów i rozwiniętych wierszach zagnieżdżonych kontenerów

### Wybór primary color (brand color)
**Status:** ⏸️ On Hold | **Priority:** Low | **Complexity:** Small

- Obecny kolor "dark orange" jest zadowalający, zadanie wstrzymane
- **Uwaga:** Warianty kolorów są już przygotowane w `src/css/style.css` jako zakomentowany kod (na wypadek potrzeby zmiany w przyszłości)

### ✅ Zintegrowany input wagi z wyborem jednostki
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Small

- ✅ Komponent `<WeightInputWithUnitPicker>` łączący input wagi z wyborem jednostki w jednym elemencie UI
- ✅ Komponent łączy:
  - ✅ Input numeryczny dla wagi
  - ✅ Select/dropdown dla jednostki wagi (g, kg, oz, lb)
- ✅ Użycie w formularzach:
  - ✅ `ItemFormFields.vue` - pole wagi przedmiotu
  - ✅ `ContainerFormFields.vue` - pola wagi kontenera (weight, maxWeight)
- ✅ Korzyści:
  - ✅ Lepszy UX - wszystko w jednym miejscu
  - ✅ Spójny wygląd we wszystkich formularzach
  - ✅ Łatwiejsze zarządzanie stanem (jedna kompozycja zamiast dwóch osobnych pól)
- ✅ Obsługa wszystkich jednostek: g, kg, oz, lb

---

## 🔗 Relacje i Nesting

### ✅ Relacja parent-children (nesting kontenerów)
**Status:** ✅ Completed | **Priority:** High | **Feature:** [FEATURE-008](./features/FEATURE-008-container-nesting.md)

- ✅ Kontener może zawierać na liście przedmiotów inny kontener
  - Przykład: W plecaku może być Pouch, a w Pouch może być Latarka
- ✅ Kontener, który ma rodzica lub jest używany jako item, można ukryć z głównej listy kontenerów
- ✅ Opcja wyświetlania tylko kontenerów głównych (bez zagnieżdżonych)
- ✅ Wizualne oznaczenie kontenerów zagnieżdżonych (ikona, badge, klikalna nazwa)
- ✅ Rekurencyjne obliczanie wagi (waga kontenera + waga jego zawartości)
- ✅ Rozwijane wiersze w tabeli przedmiotów - możliwość zobaczenia zawartości zagnieżdżonego kontenera
- ✅ Walidacja cyklicznych referencji - zapobieganie nieskończonym pętlom
- ✅ Osobne akcje "Dodaj Przedmiot" i "Dodaj Kontener" w interfejsie

> **Uwaga:** Ta funkcjonalność jest już zaimplementowana i działa z localStorage. W przyszłości może być rozszerzona o synchronizację z backendem (zobacz [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md)).

### Oznaczanie kontenerów jako fragmentów rodzica (integral part)
**Status:** 🔄 Planned | **Priority:** Medium | **Complexity:** Medium

- Kontener może być oznaczony jako "fragment rodzica" (integral part of parent)
- Przykład: Bagażnik samochodu jest częścią samochodu i nie powinien być liczony osobno
- Przykład: Pokrywa plecaka jest częścią plecaka
- Oznaczenie kontenera jako fragmentu:
  - Kontener nie jest liczony jako osobny kontener w statystykach
  - Waga kontenera-fragmentu jest zawsze wliczana do rodzica
  - Fragment nie może być przeniesiony do innego kontenera bez rodzica
  - Wizualne oznaczenie w interfejsie (ikona, badge, tooltip)
- Użycie przypadków:
  - Części samochodu (bagażnik, schowek, konsola)
  - Części plecaka (kieszenie, pokrywy, pasy)
  - Części namiotu (stelaż, podłoga)
  - Inne kontenery, które są nierozerwalnie związane z rodzicem
- Opcja w formularzu kontenera: checkbox "Fragment rodzica" (dostępne tylko gdy kontener ma rodzica)
- Wpływ na obliczenia:
  - Waga fragmentu zawsze wliczana do rodzica
  - Fragment nie jest liczony jako osobny kontener w statystykach
  - Fragment nie może być wyświetlony jako główny kontener (jeśli opcja "Pokaż tylko główne" jest włączona)

---

## 📝 Rozszerzone pola

### ✅ Dodatkowe pola dla przedmiotów i kontenerów
**Status:** ✅ Completed | **Priority:** Medium | **Feature:** FEATURE-006 | **Complexity:** Medium

**Dla przedmiotów:**
- ✅ **Cena** - cena zakupu przedmiotu
- ✅ **Link URL** - link do produktu, recenzji, itp.
- ✅ **Półka cenowa / jakość** - niska półka, średnia półka, wyższa półka
- ✅ **Firma** - producent/marka przedmiotu (z ComboBox i sugerowanymi wartościami)
- ✅ **Kolor** - kolor przedmiotu (z ComboBox i sugerowanymi wartościami)
- ✅ **Wearable** - opcja oznaczania przedmiotu jako noszonego na sobie (np. odzież, zegarek, buty)
- ✅ **Consumable** - opcja oznaczania przedmiotu jako zużywalnego (np. jedzenie, lekarstwa, paliwo)

**Dla kontenerów:**
- ✅ **Firma** - producent/marka kontenera
- ✅ **Cena** - cena zakupu kontenera

**Ujednolicenie modelu:**
- ✅ Wspólne pola (firma, cena) zaimplementowane w modelu danych
- ✅ Wizualizacja kolorów w tabelach (kolorowa kropka)
- ✅ Zarządzanie widocznością kolumn (marka, kolor) w tabelach

> **Uwaga:** Ta funkcjonalność jest już zaimplementowana i działa z localStorage. W przyszłości może być rozszerzona o synchronizację z backendem (zobacz [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md)).

### ✅ Dodawanie własnych marek (brand)
**Status:** ✅ Completed | **Priority:** High | **Complexity:** Medium

- ✅ UI w ustawieniach do zarządzania markami (`BrandsSettingsCard.vue`) - dodawanie, edycja, usuwanie
- ✅ Marki mają strukturę `id`, `value`, `createdAt`, `updatedAt`
- ✅ Lista marek łączona: domyślne (SUGGESTED_BRANDS) + własne użytkownika
- ✅ Własne marki dostępne w:
  - ✅ Autocomplete przy wyborze marki w formularzach przedmiotów i kontenerów
  - ✅ Rozpoznawaniu parametrów przedmiotów (fuzzy matching)
- ✅ Marki zapisywane w localStorage
- ✅ Integracja z istniejącym polem `brand` w modelu danych
- ✅ Funkcja `getBrandOptions()` łącząca domyślne i własne marki

> **Uwaga:** Ta funkcjonalność działa z localStorage (front-end only). W przyszłości może być rozszerzona o synchronizację z backendem (zobacz [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md)).

### ✅ Obsługa waluty (currency)
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Medium | **Feature:** [FEATURE-017](./features/FEATURE-017-currency-support.md)

- ✅ Pole `currency` dodane do przedmiotów i kontenerów (w typach `IGearItem`, `IGearContainer`)
- ✅ Parsowanie waluty w markdown import (rozpoznawanie PLN, USD, EUR, GBP z różnych formatów)
- ✅ Obsługiwane waluty: PLN, EUR, USD, GBP
- ✅ Domyślna waluta użytkownika w ustawieniach (localStorage)
- ✅ Automatyczne rozpoznawanie domyślnej waluty na podstawie języka
- ✅ Wyświetlanie waluty:
  - ✅ W formularzach: pole wyboru waluty obok pola ceny
  - ✅ W tabelach: cena z walutą (np. "100,00 PLN")
  - ✅ W statystykach kontenera: suma cen z odpowiednimi walutami
- ✅ Formatowanie cen używając `Intl.NumberFormat`
- ✅ Logika wyboru waluty w UI

> **Uwaga:** Ta funkcjonalność działa z localStorage (front-end only). W przyszłości może być rozszerzona o synchronizację z backendem (zobacz [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md)).

### Obsługa Markdown w notatkach
**Status:** 🔄 Planned | **Priority:** Medium | **Complexity:** Medium

- Możliwość formatowania notatek (pole `notes`) za pomocą Markdown
- W formularzach: edytor Markdown (z podglądem na żywo lub split view)
- W wyświetlaniu: renderowanie Markdown do HTML (linki, **pogrubienie**, *kursywa*, listy, itp.)
- Podstawowe wsparcie dla:
  - **Bold** i *italic*
  - Linki `[text](url)`
  - Listy (ul/ol)
  - `code` i bloki kodu
- Opcjonalnie: edytor WYSIWYG dla Markdown lub składnia Markdown z podglądem
- Obsługa dla przedmiotów (`IGearItem.notes`) i kontenerów (`IGearContainer.description`)

---

## 🚀 Import/Export i Markdown

### ✅ Eksport i import markdown (AI-friendly format)
**Status:** ✅ Completed | **Priority:** High | **Feature:** FEATURE-009, FEATURE-011 | **Complexity:** Large

**Eksport do markdown:**
- ✅ Przycisk "Eksport do prompt (AI)" w dropdown menu kontenera
- ✅ Przycisk "Eksport do prompt (AI) - Wszystkie" dla wszystkich kontenerów na liście
- ✅ Eksport tworzy markdown z kontenerem i jego zawartością w ujednoliconym formacie
- ✅ Dialog z markdownem i przyciskiem do kopiowania
- ✅ Przycisk "Guidelines" w dialogu - kopiuje szablon formatowania dla AI
- ✅ Legenda/opis dla AI wyjaśniająca strukturę danych

**Format markdown (ujednolicony dla import/export):**
```markdown
## [Container Name] [#container-id] ([Container Type])
- **[Item Name]** x[qty] ([Brand], [Color]) [#nested-id] ([Status]) <URL> - [weight]g
```

**Cechy formatu:**
- ✅ **Nazwa przedmiotu** (bold `**text**`) - wymagane
- ✅ **Ilość** (format: `x2`, `x10`) - opcjonalne, może być wszędzie w linii
- ✅ **Marka i kolor** w pierwszych nawiasach: `(Marka, Kolor)` - opcjonalne
- ✅ **Status i expiration** w drugich nawiasach: `(Status, Expiration: DD.MM.YYYY)` - opcjonalne
- ✅ **Container ID** w formacie `[#slug-id]` - dla identyfikacji kontenerów
  - ID generowane jako slug z nazwy: "Bug-Out Bag" → `#bug-out-bag`
  - Użyte w nagłówku kontenera i referencjach do zagnieżdżonych kontenerów
- ✅ **URL** w nawiasach kątowych lub plain: `<https://example.com>` lub `https://...` lub `www...` - opcjonalne
  - Automatyczne dodawanie `https://` do linków zaczynających się od `www.`
- ✅ **Waga** na końcu: `- 500g` lub `- 2.5kg` - opcjonalne (domyślnie 100g)
- ✅ **Zagnieżdżone kontenery**:
  - Item z `[#id]` w linii przedmiotu
  - Osobna definicja kontenera z tym samym `[#id]` w nagłówku
  - Parser automatycznie tworzy relację

**Import z markdown:**
- ✅ Przycisk "Import z markdown" w dropdown menu na liście kontenerów
- ✅ Dialog z textarea do wklejenia markdown i przyciskiem "Preview"
- ✅ Elastyczny parser:
  - ✅ Rozpoznaje pola w dowolnej kolejności (nazwa, ilość, waga, marka, kolor, status, expiration, URL, container ID)
  - ✅ Inteligentne dopasowywanie marek (fuzzy matching z SUGGESTED_BRANDS)
  - ✅ Inteligentne dopasowywanie kolorów (z SUGGESTED_COLORS)
  - ✅ Automatyczne rozpoznawanie kategorii po słowach kluczowych
  - ✅ Domyślne wartości dla brakujących pól (waga: 100g, ilość: 1, status: owned)
  - ✅ Wyciąganie `[#id]` z nagłówków kontenerów
  - ✅ Wyciąganie `[#id]` z linii przedmiotów (dla relacji zagnieżdżonych kontenerów)
  - ✅ Obsługa różnych formatów dat expiration
  - ✅ Obsługa URL w nawiasach kątowych lub plain
- ✅ Obsługa błędów - wyświetlanie błędów parsowania z numerami linii
- ✅ Preview przed importem - podgląd kontenerów i przedmiotów przed zapisaniem

**Szablon Guidelines:**
- ✅ Kompletny szablon formatowania w markdown
- ✅ Szczegółowe zasady dla każdego pola
- ✅ Przykłady dla wszystkich możliwych formatów
- ✅ Instrukcje dla AI jak rozpoznawać i formatować dane
- ✅ Dokumentacja zagnieżdżonych kontenerów
- ✅ Przycisk kopiowania szablonu do schowka

**Opcje konfiguracji eksportu:**
- ✅ Pokazywanie UUID w eksporcie (opcjonalnie)
- ✅ Pokazywanie wagi w eksporcie (opcjonalnie)
- ✅ Pokazywanie koloru w eksporcie (opcjonalnie)
- ✅ Pokazywanie marki w eksporcie (opcjonalnie)
- ✅ Pokazywanie powiązania z kontenerem (opcjonalnie)
- ✅ Pokazywanie legendy (opcjonalnie)
- ✅ Format opisu przedmiotów (off/inline/newline) - zaimplementowane
- ✅ Pokazywanie cen przedmiotów w eksporcie (opcjonalnie) - zaimplementowane | **Feature:** [FEATURE-020](./features/FEATURE-020-price-display-in-export.md)
- ✅ Dodatkowe podsumowanie "Do kupienia" na końcu eksportu - zaimplementowane | **Feature:** [FEATURE-020](./features/FEATURE-020-price-display-in-export.md)
- 🔄 Inne opcje konfiguracji formatu (poziom szczegółowości, metadane, itp.) - planowane
- 🚧 **Obsługa opisów przedmiotów w markdown** - częściowo zaimplementowane | **Feature:** [FEATURE-013](./features/FEATURE-013-item-descriptions.md)
  - ✅ Opcje formatu opisu w eksporcie: **OFF** (domyślnie), **Inline**, **New Line** - zaimplementowane
  - ✅ Dwie opcje formatu eksportu:
    - ✅ **Opcja A (Inline):** `- Nóż *(mały, składany)* - 100g` - opis w nawiasie kursywą zaraz po nazwie
    - ✅ **Opcja B (New Line):** opis w osobnej linii z wcięciem 2 spacje, od razu pod nazwą (przed wagą/marką)
  - 🔄 Parsowanie opisów w imporcie markdown (automatyczne rozpoznawanie obu formatów) - planowane
  - 🔄 Obsługa zagnieżdżonych nawiasów w opisach - planowane
- ✅ **Obsługa opisu kontenera w markdown import** - ZAIMPLEMENTOWANE
  - ✅ Parser markdown wykrywa opis kontenera (tekst między nagłówkiem a pierwszą listą przedmiotów)
  - ✅ Opis zapisywany w polu `description` kontenera
  - ✅ Unit tests dla parsowania opisów kontenerów
- ✅ **Obsługa ceny w markdown import** - ZAIMPLEMENTOWANE
  - ✅ Parser wykrywa ceny przedmiotów i kontenerów w różnych formatach
  - ✅ Obsługiwane formaty: `100PLN`, `10 PLN`, `10,00 PLN`, `1 000,00 PLN`, `10zł`, `$50`, `50$`
  - ✅ Automatyczne rozpoznawanie waluty (PLN, zł, $, EUR, €, GBP, £)
  - ✅ Cena zapisywana w polu `price` przedmiotu/kontenera
  - ✅ Waluta zapisywana w polu `currency`
  - ✅ Unit tests dla parsowania cen (kontenery i przedmioty)

> **Uwaga:** UUID support dla update workflow wymaga backendu/DB - zobacz [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md)

---

## ⚡ Usprawnienia dodawania przedmiotów

### ✅ Domyślne wartości dla nowych przedmiotów
**Status:** ✅ Completed | **Priority:** High | **Feature:** [FEATURE-004](./features/FEATURE-004-default-values.md)

- ✅ Nowy przedmiot ma większość pól z domyślnymi wartościami
- ✅ Domyślne wartości:
  - ✅ Waga: 0.1 kg
  - ✅ Ilość: 1
  - ✅ Status: "owned"
  - ✅ Priorytet: "medium"
  - ✅ Kategoria: "other" (lub wykryta automatycznie)
  - ✅ Jednostka wagi: kg

### ✅ Rozpoznawanie kategorii po nazwie
**Status:** ✅ Completed | **Priority:** Medium | **Feature:** [FEATURE-005](./features/FEATURE-005-category-recognition.md)

- ✅ Na podstawie słów kluczowych w nazwie dobieramy kategorię
- ✅ Przykłady:
  - ✅ `nóż`, `knife` → kategoria: narzędzia
  - ✅ `woda`, `water` → kategoria: woda
  - ✅ `zapałki`, `matches` → kategoria: ogień
  - ✅ `apteczka`, `first aid` → kategoria: pierwsza pomoc
- ✅ Podobnie dla kontenerów (rozpoznawanie typu kontenera)
- ✅ Słownik słów kluczowych dla każdej kategorii i typu kontenera
- ✅ Rozpoznawanie uruchamiane na zdarzeniu blur (po opuszczeniu pola nazwy)
- ✅ Priorytetyzacja dłuższych słów kluczowych (np. "bagażnik" zamiast "bag")

> **Uwaga:** Uczenie się na podstawie wcześniejszych wyborów użytkownika wymaga backendu/DB - zobacz [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md)

---

## 🔄 Zarządzanie kontenerami i przedmiotami

### ✅ Kopiowanie/klonowanie kontenerów
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Small | **Version:** v0.21.0

- Możliwość sklonowania całego kontenera wraz z jego zawartością
- Akcja "Duplikuj kontener" w menu akcji kontenera (dropdown na liście kontenerów)
- Klonowanie tworzy nowy kontener z:
  - Nazwą: "[Kopia] Nazwa oryginału" (edytowalna)
  - Wszystkimi przedmiotami z oryginału (głębokie kopiowanie)
  - Zagnieżdżonymi kontenerami (opcjonalnie - checkbox "Klonuj z zagnieżdżonymi kontenerami")
  - Wszystkimi metadanymi (typ, kolor, brand, opis, itp.)
- Dialog potwierdzający klonowanie z opcjami:
  - Nowa nazwa kontenera (domyślnie: "[Kopia] Original Name")
  - Checkbox: "Uwzględnij zagnieżdżone kontenery"
  - Checkbox: "Uwzględnij ceny" (dla przedmiotów)
- Klonowanie zapisuje w localStorage
- Toast potwierdzający sukces z linkiem do nowego kontenera

**Use cases:**
- Tworzenie wariantu plecaka (np. "Plecak letni" → "Plecak zimowy")
- Backup przed modyfikacją
- Tworzenie podobnych zestawów (EDC #1, EDC #2)

### ✅ Dodawanie istniejących przedmiotów do kontenera
**Status:** ✅ Completed | **Priority:** High | **Complexity:** Medium | **Feature:** [FEATURE-012](./features/FEATURE-012-add-existing-items.md) | **Completed in:** v0.22.0

- Możliwość dodania istniejącego przedmiotu z innego kontenera bez ręcznego przepisywania
- W ItemFormPage dodanie opcji wyboru:
  - **Nowy przedmiot** (obecny formularz) - domyślnie
  - **Istniejący przedmiot** (autocomplete) - nowy tryb
- Przycisk/toggle do przełączania między trybami lub dwa osobne buttony na stronie kontenera:
  - "Dodaj przedmiot" (obecny)
  - "Dodaj z katalogu" (nowy)
- **Tryb "Dodaj istniejący":**
  - Autocomplete/ComboBox z listą wszystkich przedmiotów ze wszystkich kontenerów
  - Wyświetlanie: nazwa + kontener źródłowy + ikona kategorii
  - Filtrowanie po nazwie (fuzzy search)
  - Po wybraniu przedmiotu:
    - Domyślnie: **kopia przedmiotu** (wszystkie pola + nowe UUID)
    - Opcjonalnie: edycja przed dodaniem (ilość, waga, status)
- Lista przedmiotów sortowana alfabetycznie
- Grupowanie według kontenera źródłowego (opcjonalnie)
- Podgląd szczegółów przedmiotu w dropdown (waga, marka, kolor)

**Globalny katalog przedmiotów (localStorage):**
- Funkcja w gearService: `getAllItems(): IGearItem[]` - zwraca wszystkie przedmioty ze wszystkich kontenerów
- Funkcja: `getItemsForAutocomplete()` - zwraca przedmioty w formacie dla ComboBox
- Cache w composable dla wydajności

**Use cases:**
- Dodawanie tego samego przedmiotu do wielu kontenerów (np. "Latarka" w różnych zestawach)
- Szybkie budowanie nowego kontenera na bazie istniejących przedmiotów
- Unikanie przepisywania tych samych danych

> **Uwaga:** Linkowanie przedmiotów (zmiana w jednym → zmiana w wielu) wymaga backendu/DB - zobacz [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md)

---

## ✏️ Szybka edycja

### Edycja bezpośrednio na liście
**Status:** 🔄 Planned | **Priority:** High | **Feature:** FEATURE-007 | **Complexity:** Large

- Możliwość szybkiej edycji listy - dodawanie i zmienianie przedmiotów bezpośrednio na liście
- Bez wchodzenia w formularz
- Inline editing dla podstawowych pól (nazwa, ilość, status)
- Szybkie akcje (zmiana statusu, priorytetu) bezpośrednio z listy

### ✅ Kolejność przedmiotów w kontenerze
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Medium | **Feature:** [FEATURE-018](./features/FEATURE-018-item-ordering.md) | **Version:** v2.9.0

- Dodanie pola `order` (lub `sortOrder`) do przedmiotów w kontenerze
- Możliwość ręcznego układania przedmiotów w wybranej kolejności
- Dwa sposoby zmiany kolejności:
  - **Drag & drop** - przeciąganie wierszy w tabeli do zmiany kolejności (preferowane)
  - **Akcje "Do góry" / "Do dołu"** - przyciski w menu akcji przedmiotu (alternatywa, jeśli drag & drop jest zbyt skomplikowane)
- Kolejność zapisywana w localStorage i wyświetlana domyślnie w tabeli przedmiotów
- Opcja sortowania według innych kryteriów (nazwa, waga, kategoria) z możliwością powrotu do kolejności ręcznej
- Wizualne wskaźniki podczas przeciągania (highlight, placeholder)

---

## 📊 Wizualizacje i analityka

### ✅ Wykres kołowy kategorii w kontenerze
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Medium

- ✅ Wykres kołowy (donut chart) pokazujący rozkład kategorii przedmiotów w kontenerze
- ✅ Przełącznik między dwoma trybami wyświetlania:
  - ✅ **Pod względem wagi** - Jak dużo ważą narzędzia względem całości? (procentowy udział wagi każdej kategorii)
  - ✅ **Pod względem ilości** - Jak dużo mam sztuk narzędzi względem wszystkich przedmiotów? (procentowy udział ilości przedmiotów w każdej kategorii)
- ✅ Wykres wyświetlany na stronie szczegółów kontenera
- ✅ Kolorowe segmenty odpowiadające kolorom kategorii (lub dedykowanym kolorom)
- ✅ Legenda z nazwami kategorii i wartościami procentowymi
- ✅ Uwzględnienie zagnieżdżonych kontenerów w obliczeniach (opcjonalnie)

### ✅ Rozszerzenie wykresów na stronie szczegółów kontenera
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Medium | **Feature:** [FEATURE-019](./features/FEATURE-019-extended-charts.md)

- ✅ Dodanie wykresu kołowego według **ceny** (price) - rozkład kosztów według kategorii
  - ✅ Suma cen przedmiotów w każdej kategorii
  - ✅ Procentowy udział każdej kategorii w całkowitym koszcie kontenera
  - ✅ Wyświetlanie tylko dla przedmiotów z ustawioną ceną
- ✅ Dodanie wykresu kołowego według **priorytetu** (priority) - rozkład przedmiotów według priorytetu
  - ✅ Liczba przedmiotów w każdej kategorii priorytetu (critical, high, medium, low)
  - ✅ Procentowy udział każdego priorytetu w całkowitej liczbie przedmiotów
- ✅ Rozszerzenie przełącznika trybów wykresu o nowe opcje:
  - ✅ Waga (istniejące)
  - ✅ Ilość (istniejące)
  - ✅ Cena (nowe)
  - ✅ Priorytet (nowe)
- ✅ Wizualne oznaczenie brakujących danych (np. gdy przedmioty nie mają ustawionej ceny)
- ✅ Wszystkie wykresy używają spójnego systemu kolorów i stylu
- ✅ Kolory dla priorytetów: Critical (czerwony), High (pomarańczowy), Medium (żółty), Low (zielony)

### Wielowymiarowe wykresy (category x price, category x priority)
**Status:** 🔄 Planned | **Priority:** Low | **Complexity:** High

- Rozważenie implementacji wielowymiarowych wykresów pokazujących relacje między różnymi wymiarami danych
- Przykłady:
  - **Kategoria × Cena** - wykres słupkowy lub heatmap pokazujący średnią/całkowitą cenę dla każdej kategorii
  - **Kategoria × Priorytet** - wykres pokazujący rozkład priorytetów w każdej kategorii
  - **Priorytet × Cena** - wykres pokazujący rozkład cen według priorytetu
- Możliwe typy wykresów:
  - Heatmap (mapa ciepła) - dla dwóch wymiarów kategorycznych
  - Wykres słupkowy grupowany (grouped bar chart) - dla kombinacji kategorii i wartości numerycznych
  - Wykres bąbelkowy (bubble chart) - dla trzech wymiarów (x, y, rozmiar bąbelka)
- Interaktywne narzędzia do eksploracji danych (zoom, filtrowanie, tooltips)
- **Uwaga:** Ta funkcjonalność wymaga dokładniejszej analizy potrzeb użytkowników i może być zaimplementowana w późniejszej wersji

---

## ⚖️ Kontrola wagi

### ✅ Maksymalna waga kontenera (maxWeight)
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Medium | **Version:** v0.20.0

- ✅ Dodanie opcjonalnego pola `maxWeight` do kontenerów
- ✅ Możliwość ustawienia maksymalnej wagi dla kontenera (użytkownik może określić limit wagi, który jest w stanie nosić/transportować)
- ✅ Wizualne ostrzeżenia gdy waga kontenera przekracza lub zbliża się do limitu:
  - ✅ **Badge "Przekroczona waga"** - gdy totalna waga > maxWeight (czerwony, 100%+)
  - ✅ **Badge "Blisko limitu"** - ostrzeżenie (pomarańczowy, 90%+)
  - ✅ **Wskaźnik procentowy** - pokazuje procent wykorzystania limitu
  - ✅ **Kolorowanie** - zielony (0-70%), żółty (70-90%), pomarańczowy (90-100%), czerwony (100%+)
- ✅ Wyświetlanie w różnych miejscach:
  - ✅ W nagłówku kontenera (ContainerHeader) - badge i wskaźnik
  - ✅ W statystykach kontenera - wizualny wskaźnik z paskiem postępu ("15kg / 20kg")
- ✅ Ustawienie maxWeight w formularzu kontenera:
  - ✅ Pole opcjonalne z inputem numerycznym
  - ✅ Wybór jednostki wagi (g, kg, oz, lb) - zgodnie z preferowaną jednostką użytkownika
  - ✅ Automatyczna konwersja do gramów w modelu danych
- ✅ Uwzględnienie zagnieżdżonych kontenerów w obliczeniach wagi
- ✅ Uwzględnienie wagi samego kontenera w obliczeniach

**Nie zaimplementowane (future):**
- Toast/notification gdy podczas dodawania przedmiotu przekroczymy limit
- Opcjonalna blokada dodawania przedmiotów gdy limit jest przekroczony (checkbox w ustawieniach)
- Badge na karcie kontenera na liście

**Use cases:**
- Backpacking: "Nie chcę nosić więcej niż 12kg"
- Travel: "Bagaż podręczny max 8kg (limit linii lotniczej)"
- EDC: "Kieszeń max 500g"
- Survival kit: "Zestaw przetrwania max 3kg"

---

## 🛠️ Obsługa błędów i UX

### ✅ Strona 404 (Not Found)
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Small

- ✅ Dedykowana strona 404 dla niepasujących tras (`NotFoundPage.vue`)
- ✅ Wildcard route `*` w Vue Router łapiący wszystkie nieistniejące ścieżki
- ✅ Przyjazny dla użytkownika interfejs:
  - ✅ Komunikat "Strona nie została znaleziona"
  - ✅ Link do strony głównej
  - ✅ Sugestie dalszych kroków (Kontenery, Dashboard, Ustawienia)
- ✅ Tłumaczenia PL/EN
- ✅ Layout: `public` (dostępna dla wszystkich)

### ✅ Error handler dla chunk loading errors
**Status:** ✅ Completed | **Priority:** High | **Complexity:** Medium

- ✅ Obsługa błędu "ChunkLoadError" (błąd ładowania chunk po deploy nowej wersji)
- ✅ Wykrywanie błędów ładowania chunk w runtime
- ✅ Dialog z komunikatem (window.confirm):
  - ✅ Tytuł: "Nowa wersja aplikacji" / "New Version Available"
  - ✅ Treść: "Aplikacja została zaktualizowana. Aby kontynuować, należy odświeżyć stronę."
  - ✅ Przycisk "OK" (odświeża stronę) / "Cancel" (kontynuuje, niektóre funkcje mogą nie działać)
- ✅ Tłumaczenia PL/EN (automatyczne wykrywanie locale)
- ✅ Global error handler w `main.ts`
- ✅ Dedykowany composable `useChunkLoadErrorHandler.ts` (opcjonalny)
- ✅ Auto-refresh po potwierdzeniu użytkownika

**Use cases:**
- Użytkownik ma otwartą aplikację
- Deploy nowej wersji następuje w tle
- Użytkownik próbuje przejść do nowej trasy
- Stara chunk jest usunięta → ChunkLoadError
- Dialog informuje użytkownika o nowej wersji i oferuje odświeżenie strony

---

## 📄 Informacje prawne i footer

### ✅ Strona "Informacja o ciasteczkach" i Footer
**Status:** ✅ Completed | **Priority:** Low | **Feature:** FEATURE-010 | **Complexity:** Small | **Completed in:** v0.15.0

**Strona "Informacja o ciasteczkach":**
- ✅ Strona `/cookies` z informacją o wykorzystaniu localStorage
- ✅ Sekcje: LocalStorage, Co przechowujemy, Prywatność, Przyszłość, RODO
- ✅ Zgodność z RODO - informacje o lokalnym przechowywaniu danych
- ✅ Tłumaczenia PL/EN

**Footer:**
- ✅ Footer z informacją `© [rok] DEV Made IT`
- ✅ Linki do:
  - ✅ Informacji o ciasteczkach (`/cookies`)
  - ✅ Polityki prywatności (`/privacy`)
  - ✅ Kontaktu (`/contact`)
  - ✅ GitHub/repozytorium
- ✅ Footer wyświetlany w `AuthenticatedLayout`

---

## 🤖 Funkcje AI (front-end only)

### Funkcje AI z API calls (bez auth)
**Status:** 🔄 Planned | **Priority:** Low | **Complexity:** Medium

- Sugestie sprzętu (na podstawie pogody, aktywności itp.) - przez API calls
- Analiza listy (co dodać, co usunąć, alternatywy) - przez API calls
- Generowanie gotowych presetów (UL, bushcraft, EDC) - przez API calls
- Konwersja: opis → gotowy kontener - przez API calls

> **Uwaga:** Podstawowe funkcje AI mogą działać przez API calls bez autoryzacji. Zaawansowane funkcje wymagające personalizacji i uczenia się na podstawie historii użytkownika wymagają backendu/DB - zobacz [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md)

### ✅ Rozpoznawanie parametrów przedmiotów na żądanie
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Medium | **Version:** v0.19.0

- ✅ Rozpoznawanie koloru, firmy (brand) i innych parametrów na podstawie nazwy przedmiotu
- ✅ Akcje dostępne w różnych miejscach:
  - ✅ **Formularz przedmiotu** - przycisk "Rozpoznaj parametry"
  - ✅ **Formularz kontenera** - przycisk "Rozpoznaj parametry" dla nazwy kontenera
  - ✅ **Strona kontenera z listą przedmiotów** - akcja "Rozpoznaj parametry wszystkich przedmiotów" (bulk action)
  - ✅ **Akcje wiersza przedmiotu w tabeli** - akcja "Rozpoznaj parametry" dla pojedynczego przedmiotu
- ✅ Automatyczne uzupełnianie pól: kolor, firma/brand (oraz innych jeżeli są dostępne)
- ✅ Integracja z istniejącymi słownikami sugerowanych wartości (SUGGESTED_BRANDS, SUGGESTED_COLORS)
- ✅ Fuzzy matching dla rozpoznawania brandów i kolorów
- ✅ Uzupełnianie tylko pustych pól (nie nadpisuje istniejących wartości)
- ✅ Integracja z importem markdown - automatyczne rozpoznawanie parametrów podczas importu

---

## 📈 Priorytetyzacja

### High Priority (Następne do zrobienia)
1. ✅ **Strona z listą wszystkich przedmiotów** - High priority, Medium complexity (Completed in v0.10.0)
2. ✅ **Dodawanie istniejących przedmiotów do kontenera** - High priority, Medium complexity (Completed in v0.22.0)
3. ✅ **Dodawanie własnych marek (brand)** - High priority, Medium complexity (Completed)
4. ✅ **Error handler dla chunk loading errors** - High priority, Medium complexity (Completed)
5. **Edycja bezpośrednio na liście** - High priority, Large complexity

### Medium Priority
1. ✅ **Kopiowanie/klonowanie kontenerów** - Medium priority, Small complexity (Completed in v0.21.0)
2. ✅ **Maksymalna waga kontenera (maxWeight)** - Medium priority, Medium complexity (Completed in v0.20.0)
3. ✅ **Zintegrowany input wagi z wyborem jednostki** - Medium priority, Small complexity (Completed)
4. **Obsługa waluty (currency)** - Medium priority, Medium complexity
5. **Kolejność przedmiotów w kontenerze** - Medium priority, Medium complexity
6. **Oznaczanie kontenerów jako fragmentów rodzica** - Medium priority, Medium complexity
7. **Obsługa Markdown w notatkach** - Medium priority, Medium complexity
8. ✅ **Rozszerzone pola** - Medium priority, Medium complexity (Completed in v0.8.0)
9. ✅ **Rozpoznawanie parametrów przedmiotów na żądanie** - Medium priority, Medium complexity (Completed in v0.19.0)

### Low Priority (Polish/Enhancement)
1. ⏸️ **Wybór primary color** - Low priority, Small complexity (On Hold - obecny kolor zadowalający)
2. ✅ **Footer i strony prawne** - Low priority, Small complexity (Completed)
3. **Funkcje AI (podstawowe)** - Low priority, Medium complexity

---

## 📝 Uwagi dotyczące funkcjonalności wymagających backendu

Wszystkie funkcjonalności wymagające backendu, bazy danych lub autoryzacji zostały przeniesione do [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md), w tym:
- Synchronizacja między urządzeniami
- Wersjonowanie danych
- Udostępnianie i współpraca
- Globalny katalog itemów (multi-user)
- Linkowanie przedmiotów (multi-user)
- Zaawansowane funkcje AI z personalizacją
- Szablony kontenerów (z udostępnianiem)
- Statystyki i raporty (multi-user)

---

## 📝 Notatki

- Wszystkie funkcjonalności w tym pliku działają z localStorage (front-end only)
- Wszystkie zaimplementowane features mają dokumentację w `docs/features/`
- Statusy są aktualizowane na bieżąco
- Priorytety mogą się zmieniać w zależności od potrzeb użytkowników
- Complexity: Small (1-2 dni), Medium (3-5 dni), Large (1+ tygodnie)
- Funkcjonalności wymagające backendu/DB/auth znajdują się w [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md)
