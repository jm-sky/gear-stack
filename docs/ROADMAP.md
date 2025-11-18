# Roadmap - Gear Stack

Lista planowanych funkcjonalności i ulepszeń aplikacji.

---

## 🌐 Internacjonalizacja

### Wykrywanie języka (locale) z ustawień przeglądarki
- Automatyczne wykrywanie języka użytkownika na podstawie ustawień przeglądarki
- Fallback do domyślnego języka (np. polski)
- Możliwość ręcznej zmiany języka w ustawieniach

---

## 🎨 UI/UX Ulepszenia

### Dedykowane ikony dla kategorii
- Na liście przedmiotów - dedykowana ikona do każdej kategorii
- Ikony dla kategorii: woda, ogień, jedzenie, schronienie, pierwsza pomoc, narzędzia, nawigacja, komunikacja, odzież, higiena, inne
- Spójny system ikon (np. Lucide Icons)

### Kolorowanie kontenerów
- Możliwość przypisania koloru do kontenera
- Kilka dostępnych kolorów do wyboru
- Wizualne rozróżnienie kontenerów na liście

### Wybór primary color (brand color)
- Porównanie obecnego "dark orange" z alternatywnymi opcjami
- Rozważenie kolorów: coyote, olive, oraz inne opcje pasujące do tematyki survival/outdoor
- Testowanie różnych wariantów kolorystycznych
- Wybór finalnego brand color, który najlepiej oddaje charakter aplikacji
- Aktualizacja palety kolorów w całej aplikacji po wyborze

---

## 🔗 Relacje i Nesting

### Relacja parent-children (nesting kontenerów)
- Kontener może zawierać na liście przedmiotów inny kontener
  - Przykład: W plecaku może być Pouch, a w Pouch może być Latarka
- Kontener, który ma rodzica, można ukryć z głównej listy kontenerów
- Opcja wyświetlania tylko kontenerów głównych (bez zagnieżdżonych)
- Wizualne oznaczenie kontenerów zagnieżdżonych
- Rekurencyjne obliczanie wagi (waga kontenera + waga jego zawartości)

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

### Domyślne wartości dla nowych przedmiotów
- Nowy przedmiot powinien mieć większość pól z domyślnymi wartościami (jeżeli pole jest wymagane)
- Przykłady domyślnych wartości:
  - Waga: 0.1 kg
  - Ilość: 1
  - Status: "owned"
  - Priorytet: "medium"
  - Kategoria: "other" (lub wykryta automatycznie)

### Rozpoznawanie kategorii po nazwie
- Na podstawie słów kluczowych w nazwie dobieramy kategorię oraz ew. inne pola
- Przykłady:
  - `nóż`, `knife` → kategoria: narzędzia
  - `woda`, `water` → kategoria: woda
  - `zapałki`, `matches` → kategoria: ogień
  - `apteczka`, `first aid` → kategoria: pierwsza pomoc
- Podobnie dla kontenerów (rozpoznawanie typu kontenera)
- Słownik słów kluczowych dla każdej kategorii
- Możliwość uczenia się na podstawie wcześniejszych wyborów użytkownika

---

## ✏️ Szybka edycja

### Edycja bezpośrednio na liście
- Możliwość szybkiej edycji listy - dodawanie i zmienianie przedmiotów bezpośrednio na liście
- Bez wchodzenia w formularz
- Inline editing dla podstawowych pól (nazwa, ilość, status)
- Szybkie akcje (zmiana statusu, priorytetu) bezpośrednio z listy
- Drag & drop do zmiany kolejności przedmiotów

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

