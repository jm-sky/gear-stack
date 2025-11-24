# Zestawienie funkcjonalności aplikacji

> 📋 **Zobacz też:**
> - [ROADMAP.md](./ROADMAP.md) - funkcjonalności front-end only (localStorage)
> - [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md) - funkcjonalności wymagające backendu/DB/auth

Legenda:
- **[=]** – funkcjonalność pokrywa się z LighterPack  
- **[≠]** – funkcjonalność jest, ale działa inaczej niż w LighterPack  
- **[+]** – nowość w Waszej aplikacji (LighterPack tego nie ma)  
- **[→]** – funkcjonalność planowana  
- **[🔐]** – wymaga backendu/DB/auth (zobacz [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md))

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
- **Waluta per kontener + domyślna waluta użytkownika** — **[→]** **[🔐]**

## 4. Notatki i opisy
- **Notatki tekstowe** — **[=]**  
- **Markdown w notatkach / opisach list i przedmiotów** — **[→]**  
- **Eksport do Markdown** — **[+]**  
- **Import z Markdown** — **[+]**

## 5. Zarządzanie elementami
- **Kopiowanie / klonowanie kontenerów** — **[→]** (może być front-end)  
- **Globalny katalog itemów** — **[→]** **[🔐]**  
- **Autocomplete przy dodawaniu itemu do kontenera** — **[→]** (może być front-end z localStorage)  
- **Linkowanie przedmiotów (zmiana w jednym → zmiana w wielu listach)** — **[→]** **[🔐]**  
- **Typy przedmiotów: worn / consumable** — **[→]** (może być front-end)

## 6. Udostępnianie i widoczność
- **Publiczny link do listy/kontenera** — **[→]** **[🔐]**  
- **Poziomy widoczności: publiczna / niepubliczna / prywatna** — **[+]** **[🔐]**  
- **Galeria publiczna list/kontenerów** — **[+]** **[🔐]**  
- **Ocenianie (gwiazdki)** — **[+]** **[🔐]**  
- **Komentarze** — **[+]** **[🔐]**

## 7. Przeglądarki
- **Przeglądarka kontenerów** — **[+]** (pokazuje drzewo kontenerów i zawartość) - front-end  
- **Przeglądarka przedmiotów (globalny katalog)** — **[+]** (może być front-end z localStorage)  
- **Dodawanie itemu do kontenera przez autocomplete z globalnego katalogu** — **[→]** (może być front-end)  

## 8. UI / UX
- **Nowoczesny wygląd, lepszy UI/UX niż LP** — **[+]**  
- **Lepsza responsywność** — **[+]**

## 9. Funkcje AI
- **Sugestie sprzętu (na podstawie pogody, aktywności itp.)** — **[→]** (może być front-end z API, zaawansowane wymaga **[🔐]**)  
- **Analiza listy (co dodać, co usunąć, alternatywy)** — **[→]** (może być front-end z API, zaawansowane wymaga **[🔐]**)  
- **Automatyczne oznaczanie kategorii / worn / consumable** — **[→]** (może być front-end, uczenie się wymaga **[🔐]**)  
- **Generowanie gotowych presetów (UL, bushcraft, EDC)** — **[→]** (może być front-end z API)  
- **Konwersja: opis → gotowy kontener** — **[→]** (może być front-end z API)

## 10. Ustawienia użytkownika
- **Referowana jednostka wagi (domyślna)** — **[= / →]** (plan na lb/oz) - może być localStorage  
- **Dodawanie nowych kategorii** — **[+]** (może być localStorage, synchronizacja wymaga **[🔐]**)  
- **Dodawanie firm / marek (brand)** — **[+]** (może być localStorage, synchronizacja wymaga **[🔐]**)  
- **Opcjonalnie: domyślna waluta i widoczność nowych kontenerów** — **[→]** **[🔐]**
