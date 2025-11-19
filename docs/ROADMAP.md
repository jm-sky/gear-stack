# Roadmap - Gear Stack

Lista planowanych funkcjonalności i ulepszeń aplikacji.

---

## 🌐 Internacjonalizacja

### ✅ Wykrywanie języka (locale) z ustawień przeglądarki
- ✅ Automatyczne wykrywanie języka użytkownika na podstawie ustawień przeglądarki
- ✅ Fallback do domyślnego języka (np. polski)
- ✅ Możliwość ręcznej zmiany języka w ustawieniach
- ✅ HTML lang attribute automatycznie ustawiany na podstawie wykrytego języka
- ✅ Wykryty język zapisywany w localStorage

### Preferowana jednostka wagi
- Użytkownik może ustawić preferowaną jednostkę wagi w ustawieniach (g lub kg)
- Wszystkie wyświetlane wagi na dashboard, w tabelach i kartach będą konwertowane do preferowanej jednostki
- Formularze nadal mogą używać różnych jednostek, ale wyświetlanie będzie spójne
- Ustawienie zapisywane w localStorage i synchronizowane w całej aplikacji

---

## 🎨 UI/UX Ulepszenia

### Strona z listą wszystkich przedmiotów
- Nowa strona wyświetlająca listę wszystkich przedmiotów ze wszystkich kontenerów
- Dostępna jako kolejna pozycja w topbar navigation (obok "Kontenery")
- Tabela przedmiotów z kolumnami:
  - Kategoria (z ikoną)
  - Nazwa przedmiotu
  - Kontener (nazwa kontenera, z którego pochodzi przedmiot)
  - Ilość
  - Waga
  - Status
  - Priorytet
- Możliwość filtrowania i sortowania:
  - Filtrowanie po kategorii, statusie, priorytecie
  - Filtrowanie po kontenerze
  - Sortowanie po dowolnej kolumnie
- Możliwość szybkiego przejścia do kontenera, w którym znajduje się przedmiot (kliknięcie w nazwę kontenera)
- Wyszukiwarka przedmiotów
- Eksport danych (opcjonalnie)

### ✅ Dedykowane ikony dla kategorii
- ✅ Na liście przedmiotów - dedykowana ikona do każdej kategorii
- ✅ Ikony dla kategorii: woda, ogień, jedzenie, schronienie, pierwsza pomoc, narzędzia, nawigacja, komunikacja, odzież, higiena, inne
- ✅ Spójny system ikon (Lucide Icons)
- ✅ Ikony wyświetlane w tabelach i selektorach kategorii

### ✅ Kolorowanie kontenerów
- ✅ Możliwość przypisania koloru do kontenera
- ✅ 10 dostępnych kolorów do wyboru (default, blue, green, red, yellow, purple, orange, pink, teal, indigo)
- ✅ Wizualne rozróżnienie kontenerów na liście (kolorowa kropka i ramka)
- ✅ Kolor wyświetlany w kartach kontenerów i rozwiniętych wierszach zagnieżdżonych kontenerów

### Wybór primary color (brand color)
- Porównanie obecnego "dark orange" z alternatywnymi opcjami
- Rozważenie kolorów: coyote, olive, oraz inne opcje pasujące do tematyki survival/outdoor
- Testowanie różnych wariantów kolorystycznych
- Wybór finalnego brand color, który najlepiej oddaje charakter aplikacji
- Aktualizacja palety kolorów w całej aplikacji po wyborze

---

## 🔗 Relacje i Nesting

### ✅ Relacja parent-children (nesting kontenerów)
- ✅ Kontener może zawierać na liście przedmiotów inny kontener
  - Przykład: W plecaku może być Pouch, a w Pouch może być Latarka
- ✅ Kontener, który ma rodzica lub jest używany jako item, można ukryć z głównej listy kontenerów
- ✅ Opcja wyświetlania tylko kontenerów głównych (bez zagnieżdżonych)
- ✅ Wizualne oznaczenie kontenerów zagnieżdżonych (ikona, badge, klikalna nazwa)
- ✅ Rekurencyjne obliczanie wagi (waga kontenera + waga jego zawartości)
- ✅ Rozwijane wiersze w tabeli przedmiotów - możliwość zobaczenia zawartości zagnieżdżonego kontenera
- ✅ Walidacja cyklicznych referencji - zapobieganie nieskończonym pętlom
- ✅ Osobne akcje "Dodaj Przedmiot" i "Dodaj Kontener" w interfejsie

---

## 📝 Rozszerzone pola

### Dodatkowe pola dla przedmiotów
Przedmioty mogą mieć dodatkowe, opcjonalne pola:
- **Cena** - cena zakupu przedmiotu
- **Link URL** - link do produktu, recenzji, itp.
- **Półka cenowa / jakość** - niska półka, średnia półka, wyższa półka
- **Firma** - producent/marka przedmiotu
- **Kolor** - kolor przedmiotu

### Dodatkowe pola dla kontenerów
Kontener też może mieć dodatkowe pola:
- **Firma** - producent/marka kontenera
- **Cena** - cena zakupu kontenera

### Ujednolicenie modelu
- Rozważenie ujednolicenia modelu danych dla kontenerów i przedmiotów
- Wspólne pola (np. firma, cena) w jednym miejscu

---

## 🚀 Funkcjonalności eksportu

### Eksport do prompt (AI)
- Kontener oraz Kontenery powinny mieć przycisk w rodzaju "Eksport do prompt"
- Stworzy to wiadomość w markdown z kontenerem/kontenerami i ich zawartością
- Będzie też legenda/opis dla AI, aby zrozumiał co to jest
- Użytkownik będzie mógł wkleić to do ChatGPT i poprosić o sugestie
- Format eksportu:
  - Struktura kontenera z przedmiotami
  - Metadane (waga, gotowość, status)
  - Opcjonalnie: ceny, linki, firmy
  - Legenda wyjaśniająca strukturę danych dla AI

---

## ⚡ Usprawnienia dodawania przedmiotów

### ✅ Domyślne wartości dla nowych przedmiotów
- ✅ Nowy przedmiot ma większość pól z domyślnymi wartościami
- ✅ Domyślne wartości:
  - ✅ Waga: 0.1 kg
  - ✅ Ilość: 1
  - ✅ Status: "owned"
  - ✅ Priorytet: "medium"
  - ✅ Kategoria: "other" (lub wykryta automatycznie)
  - ✅ Jednostka wagi: kg

### ✅ Rozpoznawanie kategorii po nazwie
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
- ⏳ Możliwość uczenia się na podstawie wcześniejszych wyborów użytkownika (zaplanowane, ale nie zaimplementowane)

---

## ✏️ Szybka edycja

### Edycja bezpośrednio na liście
- Możliwość szybkiej edycji listy - dodawanie i zmienianie przedmiotów bezpośrednio na liście
- Bez wchodzenia w formularz
- Inline editing dla podstawowych pól (nazwa, ilość, status)
- Szybkie akcje (zmiana statusu, priorytetu) bezpośrednio z listy

### Kolejność przedmiotów w kontenerze
- Dodanie pola `order` (lub `sortOrder`) do przedmiotów w kontenerze
- Możliwość ręcznego układania przedmiotów w wybranej kolejności
- Dwa sposoby zmiany kolejności:
  - **Drag & drop** - przeciąganie wierszy w tabeli do zmiany kolejności (preferowane)
  - **Akcje "Do góry" / "Do dołu"** - przyciski w menu akcji przedmiotu (alternatywa, jeśli drag & drop jest zbyt skomplikowane)
- Kolejność zapisywana w bazie danych i wyświetlana domyślnie w tabeli przedmiotów
- Opcja sortowania według innych kryteriów (nazwa, waga, kategoria) z możliwością powrotu do kolejności ręcznej
- Wizualne wskaźniki podczas przeciągania (highlight, placeholder)

---

## 📊 Wizualizacje i analityka

### Wykres kołowy kategorii w kontenerze
- Wykres kołowy pokazujący rozkład kategorii przedmiotów w kontenerze
- Przełącznik między dwoma trybami wyświetlania:
  - **Pod względem wagi** - Jak dużo ważą narzędzia względem całości? (procentowy udział wagi każdej kategorii)
  - **Pod względem ilości** - Jak dużo mam sztuk narzędzi względem wszystkich przedmiotów? (procentowy udział ilości przedmiotów w każdej kategorii)
- Wykres wyświetlany na stronie szczegółów kontenera
- Kolorowe segmenty odpowiadające kolorom kategorii (lub dedykowanym kolorom)
- Legenda z nazwami kategorii i wartościami procentowymi
- Uwzględnienie zagnieżdżonych kontenerów w obliczeniach (opcjonalnie)

---

## 📄 Informacje prawne i footer

### Strona "Informacja o ciasteczkach"
- Strona/informacja typu "Informacja o ciasteczkach"
- Informacje o wykorzystaniu localStorage
- Zgodność z RODO (jeśli aplikacja będzie wykorzystywać cookies w przyszłości)

### Footer
- Footer z informacją typu `2025 (R) DEV Made IT`
- Linki do:
  - Informacji o ciasteczkach
  - Polityki prywatności (jeśli będzie potrzebna)
  - Kontaktu
  - GitHub/repozytorium (opcjonalnie)

---

## 🔮 Przyszłe rozważenia

- Synchronizacja między urządzeniami (cloud storage)
- Wersjonowanie danych (historia zmian)
- Statystyki i raporty
- Szablony kontenerów (predefiniowane zestawy)
- Współdzielenie kontenerów między użytkownikami
- Aplikacja mobilna (PWA)

