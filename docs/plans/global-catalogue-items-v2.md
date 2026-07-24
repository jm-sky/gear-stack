# Nowe przedmioty katalogu globalnego

> **Status:** `done` (2026-07-24)  
> **Co to jest:** praca **content/seed** — dopisanie realnych przedmiotów do globalnego katalogu i powiązanie ich z example sets.  
> **To nie jest:** refaktor kodu funkcji „Global Catalogue” (ta jest już ✅ Completed w ROADMAP).  
> Plan / indeks: [plans/README.md](./README.md)

## Zakres (zrealizowany)

1. Przykładowe zestawy Budget EDC + Medium EDC (kod, i18n, generator).
2. Uzupełnienie seedu katalogu o brakujące realne produkty.
3. Powiązanie example sets z `catalogueItemId` (wszystkie warianty).

## Mapowanie plan NEW000x → seed ULID

| Plan ID | Produkt | Seed ULID |
|---------|---------|-----------|
| NEW0001 | Mil-Tec Emergency Thermal Blanket | `01KBQ9MKG500FXNVND2X3J4AYW` |
| NEW0002 | CNOC Vecto 1L | `01KBQ9MKG500FXNVND2X3J4AYX` |
| NEW0003 | Aquamira Water Purification Tablets | `01KBQ9MKG500FXNVND2X3J4AYY` |
| NEW0004 | GSI Stainless Steel Cup 700 ml | `01KBQ9MKG500FXNVND2X3J4AYZ` |
| NEW0005 | UCO Stormproof Matches | `01KBQ9MKG500FXNVND2X3J4AZ0` |
| NEW0006 | Compact Duct Tape 10 m | `01KBQ9MKG500FXNVND2X3J4AZ1` |
| NEW0007 | Metal Spork | `01KBQ9MKG500FXNVND2X3J4AZ2` |
| NEW0008 | Emergency Poncho | `01KBQ9MKG500FXNVND2X3J4AZ3` |
| NEW0009 | Olight i3T EOS 2 | `01KBQ9MKG500FXNVND2X3J4AZ4` |
| NEW0010 | Light My Fire Swedish FireSteel 2.0 | `01KBJXFP7WMDKNJ8HNMBW1CZZG` |
| NEW0011 | Victorinox Huntsman | `01KBQ9MKG50801WW461XE4JJA4` |
| NEW0012 | Ferrocerium Rod 8 mm | `01KBQ9MKG60801WW461XE4JJA5` |
| NEW0013 | Rite in the Rain Notepad 3x5 | `01KBQ9MKG60801WW461XE4JJA6` |
| NEW0014 | Sharpie Permanent Marker | `01KBQ9MKG60801WW461XE4JJA7` |
| NEW0015 | Fenix E01 V2.0 | `01KBQ9MKG60801WW461XE4JJA8` |
| FA001 | Adventure Medical Kits Ultralight/.5 | `01KY9VGB98ARP029M07P4Q5J5N` |

## Dodatkowe produkty (P2 — starsze zestawy)

| Produkt | Seed ULID | Użyte w |
|---------|-----------|---------|
| Coghlan's Tinder Quik | `01KY9VGB99XSMGPPVG37Y0DXJ0` | Fire Pouch, BOB fire pouch |
| SOL Emergency Bivvy | `01KY9VGB99CCE53TV6XQJ88X4Y` | Bug Out Bag |
| Victorinox Classic SD | `01KY9VGB9981K988Q7V8ZBDW70` | EDC |
| Zippo Classic Lighter | `01KY9VGB99YGBS8K37VZZD4HSK` | EDC |
| Field Notes Original Kraft | `01KY9VGB99TYV40Y1T91MQCKCN` | EDC |
| Fisher Space Pen Bullet | `01KY9VGB99D51F4EM2W3A3QJ5G` | EDC |
| Fenix PD36R | `01KY9VGB99Y8FMPMPNEPV8AYN5` | Bug Out Bag |

Istniejące linki bez nowych seedów: Morakniv Companion, Paracord Badger Outdoor 500.

## Pliki

- Seed: `backend/app/seeders/catalogue_items.json`
- Example sets: `src/modules/gear/services/exampleSets.ts`
- Generator: `src/modules/gear/services/sampleSetGenerator.ts` (`budgetEdc` / `mediumEdc`)
- i18n: `src/modules/gear/i18n/index.ts` (`sampleSet.items` + variants)

## Seed CLI

```bash
docker exec gear-stack-app python -m cli db seed catalogue
```

(tylko jeśli CWD projektu **nie** zaczyna się od `_`)

## Example sets (docelowe)

### Budget EDC Survival Kit — 9/9 linked

Olight i3T, FireSteel, Rite in the Rain, Sharpie, Duct Tape, Spork, CNOC Vecto, UCO Matches, Fenix E01.

### Medium EDC / Urban Survival Kit — 11/11 linked

Olight i3T, Huntsman, FireSteel, Rite in the Rain, Sharpie, Duct Tape, CNOC Vecto, Mil-Tec blanket, Ferro 8 mm, GSI cup, AMK Ultralight/.5.

## Notes

- Drafty `NEW000x` w tym pliku są historyczne — kanoniczne ID to ULID w seedzie.
- Anker w EDC nadal wskazuje PowerCore **20100** (najbliższy match w katalogu; zestaw ma nazwę 10000).
- Po wdrożeniu: re-seed katalogu na środowisku docelowym.
