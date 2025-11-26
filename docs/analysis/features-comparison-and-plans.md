# Zestawienie funkcjonalności aplikacji

> 📋 **Zobacz też:**
> - [ROADMAP.md](./ROADMAP.md) - funkcjonalności front-end only (localStorage)
> - [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md) - funkcjonalności wymagające backendu/DB/auth

Legenda:
- **[=]** – funkcjonalność pokrywa się z LighterPack  
- **[≠]** – funkcjonalność jest, ale działa inaczej niż w LighterPack  
- **[+]** – nowość w Waszej aplikacji (LighterPack tego nie ma)  
- **[→]** – funkcjonalność planowana  
- **[✓]** – funkcjonalność zaimplementowana (gotowa)  
- **[🔐]** – wymaga backendu/DB/auth (zobacz [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md))

---

## 1. Struktura danych
- **Hierarchiczne kontenery (kontener w kontenerze)** — **[+]** **[✓]**
- **Lista / kontener główny** — **[≠]** **[✓]** (LP ma „lists", ale bez hierarchii)  
- **Przedmioty (items) z wagą, ilością, opisem, ceną** — **[=]** **[✓]**

## 2. Waga / jednostki
- **Automatyczne sumowanie wag kontenera i podkontenerów** — **[≠]** **[✓]** (rekurencyjne)  
- **Wykresy wagowe** — **[=]** **[✓]**  
- **Jednostki: kg / g** — **[=]** **[✓]**  
- **Jednostki: lb / oz** — **[✓]** (zaimplementowane)

## 3. Ceny / waluta
- **Cena produktu** — **[=]** **[✓]**  
- **Waluta per kontener + domyślna waluta użytkownika** — **[✓]** (localStorage, synchronizacja z backendem planowana)

## 4. Notatki i opisy
- **Notatki tekstowe** — **[=]** **[✓]**  
- **Markdown w notatkach / opisach list i przedmiotów** — **[→]** (planowane)  
- **Eksport do Markdown** — **[+]** **[✓]**  
- **Import z Markdown** — **[+]** **[✓]**

## 5. Zarządzanie elementami
- **Kopiowanie / klonowanie kontenerów** — **[✓]** (front-end, localStorage)  
- **Globalny katalog itemów** — **[✓]** (lista wszystkich przedmiotów, front-end z localStorage)  
- **Autocomplete przy dodawaniu itemu do kontenera** — **[✓]** (front-end z localStorage)  
- **Linkowanie przedmiotów (zmiana w jednym → zmiana w wielu listach)** — **[→]** **[🔐]** (planowane)  
- **Typy przedmiotów: worn / consumable** — **[✓]** (front-end)

## 6. Udostępnianie i widoczność
- **Publiczny link do listy/kontenera** — **[✓]** **[🔐]**  
- **Poziomy widoczności: publiczna / niepubliczna / prywatna** — **[+]** **[✓]** **[🔐]**  
- **Galeria publiczna list/kontenerów** — **[+]** **[✓]** **[🔐]**  
- **Ocenianie (gwiazdki)** — **[+]** **[→]** **[🔐]** (planowane)  
- **Komentarze** — **[+]** **[→]** **[🔐]** (planowane)

## 7. Przeglądarki
- **Przeglądarka kontenerów** — **[+]** **[✓]** (pokazuje drzewo kontenerów i zawartość) - front-end  
- **Przeglądarka przedmiotów (globalny katalog)** — **[+]** **[✓]** (front-end z localStorage)  
- **Dodawanie itemu do kontenera przez autocomplete z globalnego katalogu** — **[✓]** (front-end)  

## 8. UI / UX
- **Nowoczesny wygląd, lepszy UI/UX niż LP** — **[+]** **[✓]**  
- **Lepsza responsywność** — **[+]** **[✓]**
- **PWA (Progressive Web App)** — **[+]** **[✓]** **[🔐]** (instalacja, offline support, service worker)

## 9. Media i zasoby
- **Zdjęcia przedmiotów (galeria obrazów)** — **[+]** **[✓]** **[🔐]** (admin-only, multi-image, drag-and-drop upload, local/S3 storage)

## 10. Funkcje AI
- **Sugestie sprzętu (na podstawie pogody, aktywności itp.)** — **[→]** (może być front-end z API, zaawansowane wymaga **[🔐]**)  
- **Analiza listy (co dodać, co usunąć, alternatywy)** — **[→]** (może być front-end z API, zaawansowane wymaga **[🔐]**)  
- **Automatyczne oznaczanie kategorii / worn / consumable** — **[→]** (może być front-end, uczenie się wymaga **[🔐]**)  
- **Generowanie gotowych presetów (UL, bushcraft, EDC)** — **[→]** (może być front-end z API)  
- **Konwersja: opis → gotowy kontener** — **[→]** (może być front-end z API)

## 11. Ustawienia użytkownika
- **Preferowana jednostka wagi (domyślna)** — **[✓]** (g, kg, oz, lb) - localStorage  
- **Dodawanie nowych kategorii** — **[+]** **[✓]** (localStorage, synchronizacja z backendem planowana)  
- **Dodawanie firm / marek (brand)** — **[+]** **[✓]** (localStorage, synchronizacja z backendem planowana)  
- **Domyślna waluta i widoczność nowych kontenerów** — **[✓]** (localStorage, synchronizacja z backendem planowana)
