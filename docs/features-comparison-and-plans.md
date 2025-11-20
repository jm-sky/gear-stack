# Zestawienie funkcjonalności aplikacji

Legenda:
- **[=]** – funkcjonalność pokrywa się z LighterPack  
- **[≠]** – funkcjonalność jest, ale działa inaczej niż w LighterPack  
- **[+]** – nowość w Waszej aplikacji (LighterPack tego nie ma)  
- **[→]** – funkcjonalność planowana  

---

## 1. Struktura danych
- **Hierarchiczne kontenery (kontener w kontenerze)** — **[+]**  
- **Lista / kontener główny** — **[≠]** (LP ma „lists”, ale bez hierarchii)  
- **Przedmioty (items) z wagą, ilością, opisem, ceną** — **[=]**

## 2. Waga / jednostki
- **Automatyczne sumowanie wag kontenera i podkontenerów** — **[≠]** (rekurencyjne)  
- **Wykresy wagowe** — **[=]**  
- **Jednostki: kg / g** — **[=]**  
- **Jednostki: lb / oz** — **[→]** (planowane)

## 3. Ceny / waluta
- **Cena produktu** — **[=]**  
- **Brak waluty** — **[≠]** (LP ma)  
- **Waluta per kontener + domyślna waluta użytkownika** — **[→]**

## 4. Notatki i opisy
- **Notatki tekstowe** — **[=]**  
- **Markdown w notatkach / opisach list i przedmiotów** — **[→]**  
- **Eksport do Markdown** — **[+]**  
- **Import z Markdown** — **[+]**

## 5. Zarządzanie elementami
- **Kopiowanie / klonowanie kontenerów** — **[→]**  
- **Globalny katalog itemów** — **[→]**  
- **Autocomplete przy dodawaniu itemu do kontenera** — **[→]**  
- **Linkowanie przedmiotów (zmiana w jednym → zmiana w wielu listach)** — **[→]**  
- **Typy przedmiotów: worn / consumable** — **[→]**

## 6. Udostępnianie i widoczność
- **Publiczny link do listy/kontenera** — **[→]**  
- **Poziomy widoczności: publiczna / niepubliczna / prywatna** — **[+]**  
- **Galeria publiczna list/kontenerów** — **[+]**  
- **Ocenianie (gwiazdki)** — **[+]**  
- **Komentarze** — **[+]**

## 7. Przeglądarki
- **Przeglądarka kontenerów** — **[+]** (pokazuje drzewo kontenerów i zawartość)  
- **Przeglądarka przedmiotów (globalny katalog)** — **[+]**  
- **Dodawanie itemu do kontenera przez autocomplete z globalnego katalogu** — **[→]**  

## 8. UI / UX
- **Nowoczesny wygląd, lepszy UI/UX niż LP** — **[+]**  
- **Lepsza responsywność** — **[+]**

## 9. Funkcje AI
- **Sugestie sprzętu (na podstawie pogody, aktywności itp.)** — **[→]**  
- **Analiza listy (co dodać, co usunąć, alternatywy)** — **[→]**  
- **Automatyczne oznaczanie kategorii / worn / consumable** — **[→]**  
- **Generowanie gotowych presetów (UL, bushcraft, EDC)** — **[→]**  
- **Konwersja: opis → gotowy kontener** — **[→]**

## 10. Ustawienia użytkownika
- **Referowana jednostka wagi (domyślna)** — **[= / →]** (plan na lb/oz)  
- **Dodawanie nowych kategorii** — **[+]**  
- **Dodawanie firm / marek (brand)** — **[+]**  
- **Opcjonalnie: domyślna waluta i widoczność nowych kontenerów** — **[→]**
