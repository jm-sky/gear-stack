# Roadmap Index - Gear Stack

<!-- 
AI_METADATA:
- Type: Roadmap index/overview
- Purpose: Entry point for understanding project roadmap structure
- Last Updated: 2025-01-21
-->

Ten dokument jest punktem wejścia do roadmap projektu Gear Stack. Projekt ma **2 osobne roadmapy** ze względu na architekturę aplikacji (offline-first z opcjonalnym backendem).

## 📋 Struktura Roadmap

### [ROADMAP.md](./ROADMAP.md) - Frontend Only
**688 linii** | **~50+ funkcji**

Funkcjonalności działające z **localStorage**, bez potrzeby backendu:
- ✅ Zarządzanie kontenerami i przedmiotami
- ✅ Eksport/import markdown
- ✅ Wykresy i analityka
- ✅ Kolorowanie kontenerów
- ✅ Rozpoznawanie kategorii i parametrów
- 🔄 Inline editing (planowane)
- 🔄 Custom brand management (planowane)

**Kiedy sprawdzać:** Gdy implementujesz funkcje frontend-only lub funkcje działające offline.

---

### [ROADMAP_V2.md](./ROADMAP_V2.md) - Backend Required
**342 linie** | **~30+ funkcji**

Funkcjonalności wymagające **backendu, bazy danych i/lub autoryzacji**:
- ✅ OAuth authentication (completed)
- ✅ reCAPTCHA integration (completed)
- ✅ 2FA (completed)
- 🔄 Multi-device synchronization (planowane)
- 🔄 Container sharing (planowane)
- 🔄 Global item catalog (planowane)
- 🔄 PWA (planowane)

**Kiedy sprawdzać:** Gdy implementujesz funkcje wymagające serwera, bazy danych lub systemu użytkowników.

---

## 🎯 Jak używać z AI Agentem

### Dla funkcji frontend-only:
```
Sprawdź: docs/ROADMAP.md
Filtruj: Szukaj sekcji z tagiem "front-end only" lub "localStorage"
```

### Dla funkcji backend:
```
Sprawdź: docs/ROADMAP_V2.md
Filtruj: Szukaj sekcji z tagiem "Backend/DB/Auth Required"
```

### Dla pełnego obrazu:
```
Sprawdź: Oba pliki (ROADMAP.md + ROADMAP_V2.md)
Uwaga: Większość funkcji jest w ROADMAP.md (frontend-first approach)
```

---

## 📊 Statystyki

| Plik | Linie | Funkcje | Status |
|------|-------|---------|--------|
| ROADMAP.md | 688 | ~50+ | ✅ Aktywny |
| ROADMAP_V2.md | 342 | ~30+ | ✅ Aktywny |
| **Razem** | **1030** | **~80+** | - |

---

## 🔍 Szybkie wyszukiwanie

### Frontend Features (ROADMAP.md):
- Kategorie: 🌐 Internacjonalizacja, 🎨 UI/UX, 🔗 Relacje, 📝 Pola, 🚀 Import/Export, ⚡ Usprawnienia, ✏️ Edycja, 📊 Wizualizacje, ⚖️ Kontrola wagi, 🛠️ Obsługa błędów

### Backend Features (ROADMAP_V2.md):
- Kategorie: 🔐 Autoryzacja, 💾 Synchronizacja, 👥 Udostępnianie, 🗂️ Katalog, ⚙️ Ustawienia, 🚀 Import/Export, 📊 Statystyki, 🎯 Szablony, 🤖 AI, 📷 Media, 📱 PWA

---

## 💡 Uwagi dla AI

1. **Zawsze sprawdzaj oba pliki** jeśli nie jesteś pewien, gdzie szukać
2. **ROADMAP.md jest głównym** - większość funkcji jest tam
3. **ROADMAP_V2.md jest uzupełnieniem** - tylko funkcje wymagające backendu
4. **Statusy są aktualizowane na bieżąco** - sprawdź emoji (✅ Completed, 🔄 Planned, 🚧 In Progress)
5. **Każda funkcja ma link do szczegółowego planu** w `docs/features/`

---

**Ostatnia aktualizacja:** 2025-01-21

