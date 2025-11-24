# AI w Gear Stack — Podsumowanie

## Podstawowe zasady
- Backend korzysta tylko z **OpenRouter**.
- Użytkownik może wybierać **5–15 modeli**, różnych firm, czasem kilka modeli od tej samej firmy.
- Na razie tylko **modele tekstowe**; vision zostawiamy na później.
- Każdy użytkownik może podać **własny token**:
  - Darmowy plan → AI działa tylko z własnym tokenem.
  - Plany płatne → użytkownik wybiera jawnie: własny token lub token systemowy.
- Wybór modelu jest zawsze dowolny, niezależnie od planu.
- **Limity** dotyczą tylko użycia **systemowego tokena**.
- Endpointy są **osobne**: `/ai/chat`, `/ai/classify`, `/ai/embed`, `/ai/vision` (vision później).
- **Preferencje użytkownika** (model, token, parametry) są zapisywane w bazie.

## Zastosowania AI
1. **Rozpoznawanie właściwości przedmiotów**
   - Kategorie, brandy, kolory itp.
   - Tryby: import Markdown (opcjonalnie), tworzenie/edycja pojedynczego przedmiotu, grupowo dla wielu przedmiotów.
2. **Sugestie i optymalizacja packów**
   - Jeden kontener, kilka lub wszystkie.
   - Co dodać / usunąć, priorytety, waga.
3. **Generowanie listy gearu na podstawie scenariusza**
   - Wejście: typ bag, budżet, warunki itp.
   - Wyjście: lista rekomendowanych przedmiotów z kategoriami, wagą, ilością.

## Mechanika użycia AI
- Backend tworzy **initial prompt**, użytkownik może go zmienić.
- Dodawany jest **kontekst**: lista sprzętu wg wybranych opcji (tylko nazwy, nazwy + opisy, wagi itp.).
- Historia jest **zawsze przechowywana**:
  - Maksymalny rozmiar; po przekroczeniu kasowanie najstarszych wpisów.
  - Użytkownik może przeglądać i usuwać historię.
  - W historii zapisujemy wszystko: prompt, modyfikacje, kontekst, odpowiedź AI, model, token, czas.
- Możliwość **re-run** zapisanych interakcji (opcjonalnie).

## Interakcja użytkownika — wersja 1
- AI działa przez **okienko chatu**.
- Treść chatu może być zaimportowana, co tworzy nowe wpisy lub aktualizuje istniejące.
- Trzeba dodać obsługę **kasowania wpisów**.

## Interakcja użytkownika — wersja 2 (przyszłość)
- Wyniki działania AI mogą tworzyć **nowe przedmioty**, które są podświetlone.
- Istniejące przedmioty będą miały **przycisk wyboru alternatywnej opcji**.
