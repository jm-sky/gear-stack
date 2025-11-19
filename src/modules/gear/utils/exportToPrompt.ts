/**
 * Export container data to markdown format for AI prompts
 */

import type { IGearContainer, IGearItem } from '../types/gear.types'
import { formatWeight, formatWeightFromGrams } from './formatWeight'

interface ExportOptions {
  t?: (key: string, ...args: unknown[]) => string
  getContainerTypeLabel?: (type: string) => string
  getContainerById?: (id: string) => IGearContainer | undefined
  calculateTotalWeight?: (containerId: string) => number
}

/**
 * Convert container name to slug for ID
 * Example: "First Aid Pouch" -> "first-aid-pouch"
 */
function slugify(text: string): string {
  return text
    .toLowerCase()
    .normalize('NFD') // Normalize unicode characters
    .replace(/[\u0300-\u036f]/g, '') // Remove diacritics
    .replace(/[^a-z0-9\s-]/g, '') // Remove special chars
    .trim()
    .replace(/\s+/g, '-') // Replace spaces with hyphens
    .replace(/-+/g, '-') // Replace multiple hyphens with single
}

/**
 * Generate ID for container from its name
 */
function generateContainerId(name: string): string {
  return `#${slugify(name)}`
}

/**
 * Format item for markdown export (compact format)
 */
function formatItem(
  item: IGearItem,
  options: ExportOptions,
  indent = 0,
): string {
  const indentStr = '  '.repeat(indent)
  const parts: string[] = []

  // Item name
  parts.push(`**${item.name}**`)

  // UUID (for stable references)
  parts.push(`[uuid:${item.id}]`)

  // Quantity after name (x4 format)
  if (item.quantity > 1) {
    parts.push(`x${item.quantity}`)
  }

  // Brand and color in first parentheses
  const brandColorParts: string[] = []
  if (item.brand) {
    brandColorParts.push(item.brand)
  }
  if (item.color) {
    brandColorParts.push(item.color)
  }
  if (brandColorParts.length > 0) {
    parts.push(`(${brandColorParts.join(', ')})`)
  }

  // Expiration and status in second parentheses
  const statusParts: string[] = []
  if (item.expirationDate) {
    const date = new Date(item.expirationDate)
    const dateStr = date.toLocaleDateString('pl-PL', { day: '2-digit', month: '2-digit', year: 'numeric' })
    statusParts.push(`Expiration: ${dateStr}`)
  }
  if (item.status && options.t) {
    const statusLabel = options.t(`gear.item.statuses.${item.status}`)
    // Only show status if it's not "owned"
    if (statusLabel !== options.t('gear.item.statuses.owned')) {
      statusParts.push(statusLabel)
    }
  }
  if (statusParts.length > 0) {
    parts.push(`(${statusParts.join(', ')})`)
  }

  // Container ID if this item is a nested container
  if (item.containerId && options.getContainerById) {
    const nestedContainer = options.getContainerById(item.containerId)
    if (nestedContainer) {
      const containerId = generateContainerId(nestedContainer.name)
      parts.push(`[${containerId}]`)
    }
  }

  // URL if provided
  if (item.url) {
    parts.push(`<${item.url}>`)
  }

  // Weight at the end
  let totalWeight: number
  let weightText: string

  // If item is a nested container, use calculated total weight
  if (item.containerId && options.calculateTotalWeight) {
    const containerWeightInGrams = options.calculateTotalWeight(item.containerId)
    totalWeight = containerWeightInGrams * item.quantity
    weightText = formatWeightFromGrams(totalWeight)
  } else {
    // Regular item weight
    totalWeight = item.weight * item.quantity
    weightText = formatWeight(totalWeight, item.weightUnit ?? 'g')
  }

  parts.push(`- ${weightText}`)

  return `${indentStr}- ${parts.join(' ')}`
}

/**
 * Format nested container items separately
 */
function formatNestedContainer(
  container: IGearContainer,
  options: ExportOptions,
  indent = 0,
): string {
  const indentStr = '  '.repeat(indent)
  const lines: string[] = []

  // Container header with ID and UUID
  const typeLabel = options.getContainerTypeLabel
    ? options.getContainerTypeLabel(container.type)
    : container.type
  const containerId = generateContainerId(container.name)
  lines.push(`${indentStr}## ${container.name} [${containerId}] [uuid:${container.id}] (${typeLabel})`)

  // Container items
  if (container.items.length === 0) {
    lines.push(`${indentStr}*Brak przedmiotów w kontenerze.*`)
  } else {
    container.items.forEach(item => {
      lines.push(formatItem(item, options, indent))
    })
  }

  return lines.join('\n')
}

/**
 * Export single container to markdown (compact format)
 */
export function exportContainerToPrompt(
  container: IGearContainer,
  options: ExportOptions = {},
): string {
  const {
    t,
    getContainerTypeLabel,
    getContainerById,
  } = options

  const lines: string[] = []

  // Header
  const titleText = t ? t('gear.export.title', 'Lista sprzętu') : 'Lista sprzętu'
  const descriptionText = t ? t('gear.export.description', 'Lista mojego sprzętu w różnych kontenerach, wygenerowana przez Gear Stack') : 'Lista mojego sprzętu w różnych kontenerach, wygenerowana przez Gear Stack'

  lines.push(`# ${titleText}`)
  lines.push(descriptionText)
  lines.push('')

  // Container header with ID and UUID
  const typeLabel = getContainerTypeLabel
    ? getContainerTypeLabel(container.type)
    : container.type
  const containerId = generateContainerId(container.name)
  lines.push(`## ${container.name} [${containerId}] [uuid:${container.id}] (${typeLabel})`)

  // Collect nested containers to show separately
  const nestedContainers: Array<{ item: IGearItem; container: IGearContainer }> = []

  // Items
  const emptyText = t ? t('gear.export.emptyContainer', '*Brak przedmiotów w kontenerze.*') : '*Brak przedmiotów w kontenerze.*'
  if (container.items.length === 0) {
    lines.push(emptyText)
  } else {
    container.items.forEach(item => {
      // Check if item is a nested container
      if (item.containerId && getContainerById) {
        const nestedContainer = getContainerById(item.containerId)
        if (nestedContainer) {
          // Add as regular item (without content, but with calculated weight)
          lines.push(formatItem(item, options, 0))
          // Store for later display
          nestedContainers.push({ item, container: nestedContainer })
        } else {
          // Regular item
          lines.push(formatItem(item, options, 0))
        }
      } else {
        // Regular item
        lines.push(formatItem(item, options, 0))
      }
    })
  }

  // Add nested containers with full content below
  if (nestedContainers.length > 0) {
    lines.push('')
    nestedContainers.forEach(({ container: nestedContainer }) => {
      lines.push('')
      lines.push(formatNestedContainer(nestedContainer, options, 0))
    })
  }

  // Legend for AI
  lines.push('')
  lines.push('---')
  lines.push('')
  const legendTitle = t ? t('gear.export.legendTitle', '## Legenda dla AI') : '## Legenda dla AI'
  const legendIntro = t ? t('gear.export.legendIntro', 'To jest system zarządzania sprzętem/ekwipunkiem. Oto co oznaczają dane:') : 'To jest system zarządzania sprzętem/ekwipunkiem. Oto co oznaczają dane:'
  const legendContainer = t ? t('gear.export.legendContainer', '- **Kontener**: Plecak, torba, saszetka lub inna jednostka przechowywania przedmiotów') : '- **Kontener**: Plecak, torba, saszetka lub inna jednostka przechowywania przedmiotów'
  const legendItems = t ? t('gear.export.legendItems', '- **Przedmioty**: Pojedyncze elementy wyposażenia przechowywane w kontenerze') : '- **Przedmioty**: Pojedyncze elementy wyposażenia przechowywane w kontenerze'
  const legendWeight = t ? t('gear.export.legendWeight', '- **Waga**: Całkowita waga uwzględniająca ilość') : '- **Waga**: Całkowita waga uwzględniająca ilość'
  const legendBrand = t ? t('gear.export.legendBrand', '- **Marka**: Producent/marka przedmiotu') : '- **Marka**: Producent/marka przedmiotu'
  const legendColor = t ? t('gear.export.legendColor', '- **Kolor**: Kolor przedmiotu') : '- **Kolor**: Kolor przedmiotu'
  const legendNested = t ? t('gear.export.legendNested', '- **Zagnieżdżone kontenery**: Kontener może zawierać inny kontener jako przedmiot. Zagnieżdżone kontenery są wyświetlane jako pozycja w liście oraz osobno z pełną zawartością poniżej.') : '- **Zagnieżdżone kontenery**: Kontener może zawierać inny kontener jako przedmiot. Zagnieżdżone kontenery są wyświetlane jako pozycja w liście oraz osobno z pełną zawartością poniżej.'

  lines.push(legendTitle)
  lines.push('')
  lines.push(legendIntro)
  lines.push('')
  lines.push(legendContainer)
  lines.push(legendItems)
  lines.push('- **Status**:')
  if (t) {
    const ownedDesc = t('gear.export.legendStatusOwned', 'Przedmiot jest posiadany i dostępny')
    const missingDesc = t('gear.export.legendStatusMissing', 'Przedmiot jest brakujący lub niedostępny')
    const toBuyDesc = t('gear.export.legendStatusToBuy', 'Przedmiot należy zakupić')
    lines.push(`  - ${t('gear.item.statuses.owned')}: ${ownedDesc}`)
    lines.push(`  - ${t('gear.item.statuses.missing')}: ${missingDesc}`)
    lines.push(`  - ${t('gear.item.statuses.toBuy')}: ${toBuyDesc}`)
  } else {
    lines.push('  - owned: Przedmiot jest posiadany i dostępny')
    lines.push('  - missing: Przedmiot jest brakujący lub niedostępny')
    lines.push('  - toBuy: Przedmiot należy zakupić')
  }
  lines.push(legendWeight)
  lines.push(legendBrand)
  lines.push(legendColor)
  lines.push(legendNested)
  lines.push('')

  return lines.join('\n')
}

/**
 * Export multiple containers to markdown
 */
export function exportContainersToPrompt(
  containers: IGearContainer[],
  options: ExportOptions = {},
): string {
  const { t } = options
  const lines: string[] = []

  const titleText = t ? t('gear.export.title', 'Lista sprzętu') : 'Lista sprzętu'
  lines.push(`# ${titleText}`)
  lines.push('')

  containers.forEach((container, index) => {
    if (index > 0) {
      lines.push('')
    }
    const containerMarkdown = exportContainerToPrompt(container, options)
    // Remove the header and description from nested containers
    const containerLines = containerMarkdown.split('\n')
    const titleLine = `# ${titleText}`
    if (containerLines[0] === titleLine) {
      containerLines.shift() // Remove title
      containerLines.shift() // Remove description
      if (containerLines[0] === '') {
        containerLines.shift() // Remove empty line
      }
    }
    lines.push(...containerLines)
  })

  return lines.join('\n')
}
