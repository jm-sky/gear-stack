# Roadmap Index - Gear Stack

<!-- 
AI_METADATA:
- Type: Roadmap index/overview
- Purpose: Entry point for understanding project roadmap structure
- Last Updated: 2025-01-21
-->

Ten dokument jest punktem wejścia do roadmap projektu Gear Stack. Projekt ma **2 osobne roadmapy** ze względu na architekturę aplikacji (offline-first z opcjonalnym backendem).

---

## 🎯 Nadchodzące zadania (Prioritized)

Lista zadań, którymi chcę się zająć w najbliższym czasie:

### Wysoki priorytet

1. ✅ **UUID support dla update workflow** - Zakończone
   - 📍 Lokalizacja: [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md#uuid-support-dla-update-workflow)
   - Wykorzystanie istniejącego UUID (`id`) do aktualizacji istniejących kontenerów/przedmiotów podczas importu markdown
   - Status: ✅ Completed | Priority: Medium | Complexity: Medium

2. ✅ **Media** - Zakończone (v2.15.0)
   - 📍 Lokalizacja: [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md#-media-i-zasoby-graficzne)
   - ✅ **Show from URL** — opcja dodawania obrazków z URL
   - ✅ **Primary image w wierszu tabeli** — opcjonalne wyświetlanie miniaturki primary image w tabeli przedmiotów
   - Status: ✅ Completed

3. **Katalog i linkowanie**
   - 📍 Lokalizacja: [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md#-globalny-katalog-i-linkowanie)
   - **Globalny katalog itemów** — High priority, Medium complexity (na później)
   - ✅ **Linkowanie przedmiotów** — High priority, Large complexity (Completed)
   - Status: ✅ Linkowanie completed | 🔄 Katalog planned

4. **Rozszerzone ustawienia użytkownika (waluta, widoczność, kategorie, marki w DB)**
   - 📍 Lokalizacja: [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md#-ustawienia-użytkownika-wymagające-db)
   - Domyślna waluta użytkownika (zapisywana w DB)
   - Domyślna widoczność nowych kontenerów
   - Dodawanie nowych kategorii (zapisywane w DB)
   - Dodawanie firm/marek (brand) — zapisywane w DB
   - Status: 🔄 Planned | Priority: Medium | Complexity: Small

5. **Funkcje AI**
   - 📍 Lokalizacja: [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md#-funkcje-ai-wymagające-backend)
   - Infrastruktura AI (OpenRouter, zarządzanie tokenami, historia, cache)
   - Status: 🔄 Planned | Priority: Medium | Complexity: Large

### Obniżony priorytet (trudne zadania)

1. **Automatyczne wyszukiwanie obrazków dla przedmiotów**
   - 📍 Lokalizacja: [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md#automatyczne-wyszukiwanie-obrazków-dla-przedmiotów)
   - Status: 🔄 Planned | Priority: Medium | Complexity: Large

2. **Generowanie SVG z obrazków**
   - 📍 Lokalizacja: [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md#generowanie-svg-z-obrazków)
   - Status: 🔄 Planned | Priority: Low | Complexity: Large

---

## 📋 Struktura Roadmap

### [ROADMAP_OFFLINE.md](./ROADMAP_OFFLINE.md) - Offline Features
**688 linii** | **~50+ funkcji**

Funkcjonalności działające z **localStorage**, bez potrzeby backendu (offline-first):
- ✅ Zarządzanie kontenerami i przedmiotami
- ✅ Eksport/import markdown
- ✅ Wykresy i analityka
- ✅ Kolorowanie kontenerów
- ✅ Rozpoznawanie kategorii i parametrów
- 🔄 Inline editing (planowane)
- 🔄 Custom brand management (planowane)

**Kiedy sprawdzać:** Gdy implementujesz funkcje działające offline lub z localStorage.

---

### [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md) - Online Features
**342 linie** | **~30+ funkcji**

Funkcjonalności wymagające **backendu, bazy danych i/lub autoryzacji** (online/cloud):
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

### Dla funkcji offline:
```
Sprawdź: docs/ROADMAP_OFFLINE.md
Filtruj: Szukaj sekcji z tagiem "offline" lub "localStorage"
```

### Dla funkcji online:
```
Sprawdź: docs/ROADMAP_ONLINE.md
Filtruj: Szukaj sekcji z tagiem "Backend/DB/Auth Required" lub "online"
```

### Dla pełnego obrazu:
```
Sprawdź: Oba pliki (ROADMAP_OFFLINE.md + ROADMAP_ONLINE.md)
Uwaga: Większość funkcji jest w ROADMAP_OFFLINE.md (offline-first approach)
```

---

## 📊 Statystyki

| Plik | Linie | Funkcje | Status |
|------|-------|---------|--------|
| ROADMAP_OFFLINE.md | 688 | ~50+ | ✅ Aktywny |
| ROADMAP_ONLINE.md | 342 | ~30+ | ✅ Aktywny |
| **Razem** | **1030** | **~80+** | - |

---

## 🔍 Szybkie wyszukiwanie

### Offline Features (ROADMAP_OFFLINE.md):
- Kategorie: 🌐 Internacjonalizacja, 🎨 UI/UX, 🔗 Relacje, 📝 Pola, 🚀 Import/Export, ⚡ Usprawnienia, ✏️ Edycja, 📊 Wizualizacje, ⚖️ Kontrola wagi, 🛠️ Obsługa błędów

### Online Features (ROADMAP_ONLINE.md):
- Kategorie: 🔐 Autoryzacja, 💾 Synchronizacja, 👥 Udostępnianie, 🗂️ Katalog, ⚙️ Ustawienia, 🚀 Import/Export, 📊 Statystyki, 🎯 Szablony, 🤖 AI, 📷 Media, 📱 PWA

---

## 💡 Uwagi dla AI

1. **Zawsze sprawdzaj oba pliki** jeśli nie jesteś pewien, gdzie szukać
2. **ROADMAP_OFFLINE.md jest głównym** - większość funkcji jest tam (offline-first approach)
3. **ROADMAP_ONLINE.md jest uzupełnieniem** - tylko funkcje wymagające backendu/cloud
4. **Statusy są aktualizowane na bieżąco** - sprawdź emoji (✅ Completed, 🔄 Planned, 🚧 In Progress)
5. **Każda funkcja ma link do szczegółowego planu** w `docs/features/`

---

**Ostatnia aktualizacja:** 2025-01-28

