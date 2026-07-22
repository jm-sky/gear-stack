# Catalogue image copy issues

**Status:** `in progress`  
**Created:** 2026-07-05  
**Updated:** 2026-07-06  
**Related:** [2026-07-05--008--item-images-missing-on-list.md](2026-07-05--008--item-images-missing-on-list.md)

## Opis problemów

Podczas implementacji funkcji dodawania itemów z katalogu i pobierania obrazków z katalogu napotkano kilka problemów związanych z transakcjami bazy danych i zarządzaniem sesją SQLAlchemy.

## Problem 1: Foreign Key Violation przy dodawaniu itemu z katalogu — `in progress`

### Symptomy
- Błąd: `insert or update on table "item_images" violates foreign key constraint "item_images_item_id_fkey"`
- Szczegóły: `Key (item_id)=(...) is not present in table "gear_items_v2"`
- Endpoint: `POST /api/gear/containers/{container_id}/items/from-catalogue/{catalogue_item_id}`

### Przyczyna
Metoda `add_catalogue_item_to_container`:
1. Tworzy item przez `create_item()` - który commit'uje transakcję
2. Natychmiast wywołuje `_copy_catalogue_images_to_item()` - która próbuje dodać obrazy
3. Problem: Item może nie być jeszcze widoczny w bazie z powodu izolacji transakcji lub problemów z cache sesji

### Próby rozwiązania
1. ✅ Dodano weryfikację istnienia itemu przed kopiowaniem obrazów
2. ✅ Dodano rollback w obsłudze błędów przy kopiowaniu obrazów
3. ⚠️ Problem nadal występuje w niektórych przypadkach

### Aktualny stan
- Item jest tworzony poprawnie
- Obrazki nie są kopiowane z powodu foreign key violation
- Endpoint zwraca sukces, ale obrazki nie są widoczne w UI

---

## Problem 2: MissingGreenlet Error przy pobieraniu obrazków z katalogu — `done`

### Symptomy
- Błąd: `sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called; can't call await_only() here`
- Endpoint: `POST /api/gear/items/{item_id}/fetch-images-from-catalogue`
- Lokalizacja: Linia 1493 w `service.py` - próba dostępu do `catalogue_image.id` w bloku `except`

### Przyczyna
W bloku `except` próbowano uzyskać dostęp do `catalogue_image.id`, ale obiekt `catalogue_image` był w stanie "expired" (wygasły). SQLAlchemy próbował załadować atrybut asynchronicznie, ale był to kontekst, który nie obsługuje operacji async.

### Rozwiązanie
✅ Zapisywanie wszystkich potrzebnych wartości z `catalogue_image` przed blokiem `try`:
- `catalogue_image_id`
- `catalogue_image_file_path`
- `catalogue_image_file_name`
- `catalogue_image_mime_type`
- itd.

Dzięki temu w bloku `except` mamy dostęp do wartości bez potrzeby ładowania z bazy danych.

---

## Problem 3: Foreign Key Violation przy pobieraniu obrazków z katalogu — `in progress`

### Symptomy
- Błąd: `insert or update on table "item_images" violates foreign key constraint "item_images_item_id_fkey"`
- Endpoint: `POST /api/gear/items/{item_id}/fetch-images-from-catalogue`
- Toast pokazuje sukces, ale obrazki nie są widoczne

### Przyczyna
Metoda `fetch_images_from_catalogue`:
1. Pobiera item przez `get_item()` - który może zwrócić obiekt z cache sesji
2. Wywołuje `_copy_catalogue_images_to_item()` - która próbuje dodać obrazy
3. Problem: Item może nie być widoczny w bazie z powodu izolacji transakcji lub problemów z cache

### Próby rozwiązania
1. ✅ Dodano weryfikację istnienia itemu przed kopiowaniem obrazów w `fetch_images_from_catalogue`
2. ✅ Dodano weryfikację przed każdym obrazem w pętli
3. ✅ Dodano weryfikację bezpośrednio przed commit'em
4. ✅ Dodano rollback przed każdą iteracją pętli
5. ✅ Użyto `flush()` przed `commit()` aby wcześniej wykryć błędy
6. ⚠️ Problem nadal występuje - item nie istnieje w bazie podczas commit'u

### Aktualny stan
- Endpoint zwraca sukces (200 OK)
- Toast pokazuje sukces
- Obrazki nie są kopiowane z powodu foreign key violation
- Obrazki nie są widoczne w UI

---

## Szczegóły techniczne

### Używane technologie
- **Backend**: FastAPI + SQLAlchemy 2.0+ (async)
- **Baza danych**: PostgreSQL (asyncpg)
- **ORM**: SQLAlchemy z AsyncSession

### Struktura kodu

#### Metoda `add_catalogue_item_to_container`
```python
async def add_catalogue_item_to_container(...):
    # 1. Tworzy item
    created_item = await self.create_item(container_id, user_id, item_data)
    
    # 2. Weryfikuje item (dodane)
    verified_item = await self.repository.get_item(created_item.id, user_id)
    
    # 3. Kopiuje obrazy
    if copy_image:
        await self._copy_catalogue_images_to_item(...)
```

#### Metoda `fetch_images_from_catalogue`
```python
async def fetch_images_from_catalogue(...):
    # 1. Pobiera item
    item = await self.repository.get_item(item_id, user_id)
    
    # 2. Weryfikuje item w bazie (dodane)
    item_verify = await self.repository.db.execute(select(GearItemDB)...)
    
    # 3. Kopiuje obrazy
    await self._copy_catalogue_images_to_item(...)
```

#### Metoda `_copy_catalogue_images_to_item`
```python
async def _copy_catalogue_images_to_item(...):
    # 1. Weryfikuje item przed rozpoczęciem (dodane)
    initial_item_check = await self.repository.db.execute(...)
    
    # 2. Dla każdego obrazu:
    for catalogue_image in catalogue_images:
        # a. Rollback przed każdą iteracją (dodane)
        if self.repository.db.in_transaction():
            await self.repository.db.rollback()
        
        # b. Weryfikuje item przed każdym obrazem (dodane)
        item_exists = await self.repository.db.execute(...)
        
        # c. Kopiuje obraz
        # d. Weryfikuje item przed commit'em (dodane)
        item_check = await self.repository.db.execute(...)
        
        # e. Commit
        await self.repository.db.commit()
```

### Logi błędów

#### Błąd 1: Foreign Key Violation
```
ERROR: Failed to copy image 01KC58RXVQNVDBHMZGSGQN865K from catalogue item 01KBJXKU5Q6R7S8T9U0V1W2X3Y4 to item 01KDQFZ2M57NJ24TQSG13RSTX0: 
(sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.ForeignKeyViolationError'>: 
insert or update on table "item_images" violates foreign key constraint "item_images_item_id_fkey"
DETAIL: Key (item_id)=(01KDQFZ2M57NJ24TQSG13RSTX0) is not present in table "gear_items_v2".
```

#### Błąd 2: MissingGreenlet
```
sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called; can't call await_only() here. 
Was IO attempted in an unexpected place?
```

---

## Możliwe przyczyny

### 1. Izolacja transakcji PostgreSQL
- Poziom izolacji transakcji może powodować, że item nie jest widoczny w innych transakcjach
- Możliwe rozwiązanie: Zmiana poziomu izolacji lub użycie `READ COMMITTED`

### 2. Cache sesji SQLAlchemy
- Obiekt item może być w cache sesji, ale nie w bazie danych
- Możliwe rozwiązanie: Użycie `expire_all()` lub `refresh()` przed kopiowaniem obrazów

### 3. Problem z commit'em
- `create_item()` commit'uje transakcję, ale item może nie być jeszcze widoczny
- Możliwe rozwiązanie: Użycie `flush()` zamiast `commit()` w `create_item()` i commit na końcu całej operacji

### 4. Problem z sesją
- Różne metody mogą używać różnych sesji lub stanów sesji
- Możliwe rozwiązanie: Upewnienie się, że wszystkie operacje używają tej samej sesji

### 5. Problem z asynchronicznością
- Operacje async mogą być wykonywane w niewłaściwej kolejności
- Możliwe rozwiązanie: Dodanie `await asyncio.sleep(0)` lub użycie `asyncio.gather()`

---

## Sugerowane rozwiązania

### Rozwiązanie 1: Użycie flush() zamiast commit() w create_item()
```python
# W repository.create_item()
self.db.add(item)
await self.db.flush()  # Zamiast commit()
await self.db.refresh(item)
# Commit na końcu całej operacji w add_catalogue_item_to_container
```

### Rozwiązanie 2: Użycie osobnej transakcji dla każdego obrazu
```python
# W _copy_catalogue_images_to_item()
for catalogue_image in catalogue_images:
    async with self.repository.db.begin():  # Nowa transakcja
        # Kopiowanie obrazu
        await self.repository.db.commit()
```

### Rozwiązanie 3: Użycie refresh() przed kopiowaniem obrazów
```python
# W fetch_images_from_catalogue()
item = await self.repository.get_item(item_id, user_id)
await self.repository.db.refresh(item)  # Odświeżenie z bazy
```

### Rozwiązanie 4: Sprawdzenie poziomu izolacji transakcji
```python
# W konfiguracji bazy danych
engine = create_async_engine(
    DATABASE_URL,
    isolation_level="READ COMMITTED",  # Zamiast domyślnego
)
```

### Rozwiązanie 5: Użycie select_for_update()
```python
# W _copy_catalogue_images_to_item()
item_check_stmt = select(GearItemDB).where(
    GearItemDB.id == item_id
).with_for_update()  # Blokada wiersza
```

---

## Pliki do sprawdzenia

1. `backend/app/modules/gear/service.py`
   - Metoda `add_catalogue_item_to_container()` - linia ~1283
   - Metoda `fetch_images_from_catalogue()` - linia ~1631
   - Metoda `_copy_catalogue_images_to_item()` - linia ~1358

2. `backend/app/modules/gear/repository.py`
   - Metoda `create_item()` - linia ~331
   - Metoda `get_item()` - linia ~391

3. `backend/app/core/database.py`
   - Konfiguracja AsyncSession
   - Poziom izolacji transakcji

---

## Testy do wykonania

1. Sprawdzenie, czy item rzeczywiście istnieje w bazie przed kopiowaniem obrazów
2. Sprawdzenie poziomu izolacji transakcji w PostgreSQL
3. Sprawdzenie, czy wszystkie operacje używają tej samej sesji
4. Sprawdzenie, czy commit() rzeczywiście zapisuje item do bazy
5. Dodanie logów przed i po każdej operacji bazy danych

---

## Notatki

- Wszystkie weryfikacje itemu przechodzą (item istnieje w bazie)
- Błąd występuje tylko podczas commit'u obrazu
- Problem może być związany z izolacją transakcji PostgreSQL
- Możliwe, że potrzebne jest użycie `select_for_update()` lub zmiana poziomu izolacji
