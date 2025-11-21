import type { TGearItemCategory } from '../types/gear.types'

/**
 * Keywords for category recognition
 * Supports both Polish and English keywords
 */
export const CATEGORY_KEYWORDS: Record<TGearItemCategory, string[]> = {
  water: [
    // English
    'water', 'bottle', 'canteen', 'hydration', 'filter', 'purifier', 'aqua',
    // Polish
    'woda', 'butelka', 'bidon', 'filt', 'oczyszczacz', 'hydratacja',
  ],
  food: [
    // English
    'food', 'meal', 'ration', 'snack', 'bar', 'energy', 'nutrition', 'eat', 'mess', 'spork', 'utensil', 'spoon', 'fork',
    // Polish
    'jedzenie', 'posiłek', 'racja', 'przekąska', 'bat', 'energia', 'żywność', 'jeść', 'menażka', 'łyżka', 'widelec',
  ],
  shelter: [
    // English
    'tent', 'shelter', 'tarp', 'bivy', 'hammock', 'sleeping', 'bag', 'bivouac',
    // Polish
    'namiot', 'schronienie', 'plachta', 'śpiwór', 'hamak', 'spanie',
  ],
  fire: [
    // English
    'fire', 'lighter', 'match', 'flint', 'spark', 'ignition', 'torch', 'flame', 'candle',
    // Polish
    'ogień', 'zapałki', 'zapalniczka', 'krzesiwo', 'iskra', 'płomień', 'pochodnia', 'świeczka',
  ],
  firstAid: [
    // English
    'first', 'aid', 'medical', 'bandage', 'medicine', 'kit', 'health', 'wound', 'injury',
    // Polish
    'apteczka', 'pierwsza', 'pomoc', 'medyczny', 'bandaż', 'lek', 'zdrowie', 'rana', 'uraz',
  ],
  tools: [
    // English
    'tool', 'knife', 'multitool', 'axe', 'hatchet', 'saw', 'hammer', 'screwdriver', 'wrench', 'pliers', 'shovel', 'trowel', 'entrenching',
    // Polish
    'narzędzie', 'nóż', 'siekiera', 'toporek', 'piła', 'młotek', 'śrubokręt', 'klucz', 'obcęgi', 'niezbędnik', 'saperka', 'łopatka',
  ],
  navigation: [
    // English
    'compass', 'map', 'gps', 'navigation', 'direction', 'bearing', 'route',
    // Polish
    'kompas', 'mapa', 'nawigacja', 'kierunek', 'azymut', 'trasa',
  ],
  communication: [
    // English
    'radio', 'phone', 'communication', 'signal', 'whistle', 'mirror', 'beacon',
    // Polish
    'radio', 'telefon', 'komunikacja', 'sygnał', 'gwizdek', 'lustro', 'nadajnik',
  ],
  clothing: [
    // English
    'clothing', 'clothes', 'jacket', 'pants', 'shirt', 'socks', 'boots', 'gloves', 'hat',
    // Polish
    'odzież', 'ubranie', 'kurtka', 'spodnie', 'koszula', 'skarpety', 'buty', 'rękawice', 'czapka',
  ],
  hygiene: [
    // English
    'hygiene', 'soap', 'toothbrush', 'toothpaste', 'towel', 'sanitizer', 'clean',
    // Polish
    'higiena', 'mydło', 'szczoteczka', 'pasta', 'ręcznik', 'środek', 'czysty',
  ],
  light: [
    // English
    'light', 'flashlight', 'torch', 'lamp', 'lantern', 'headlamp', 'headlight', 'illumination', 'led',
    // Polish
    'światło', 'latarka', 'lampa', 'lampion', 'reflektor', 'oświetlenie', 'świetlówka',
  ],
  other: [], // No keywords for "other" category
}

/**
 * Recognize category from item name
 * Checks keywords from longest to shortest to avoid false matches
 * (e.g., "first aid kit" should match "first aid" not just "first")
 * @param name - Item name to analyze
 * @returns Detected category or null if no match
 */
export function recognizeCategory(name: string): TGearItemCategory | null {
  if (!name || name.trim().length === 0) {
    return null
  }

  const normalizedName = name.toLowerCase().trim()

  // Collect all (category, keyword) pairs with keyword length
  const categoryKeywordPairs: Array<{ category: string; keyword: string; length: number }> = []
  for (const [category, keywords] of Object.entries(CATEGORY_KEYWORDS)) {
    if (category === 'other') continue // Skip "other" category

    for (const keyword of keywords) {
      categoryKeywordPairs.push({
        category,
        keyword: keyword.toLowerCase(),
        length: keyword.length,
      })
    }
  }

  // Sort by keyword length (longest first) to check longer matches first
  categoryKeywordPairs.sort((a, b) => b.length - a.length)

  // Check matches starting from longest keywords
  for (const { category, keyword } of categoryKeywordPairs) {
    if (normalizedName.includes(keyword)) {
      return category as TGearItemCategory
    }
  }

  return null
}

