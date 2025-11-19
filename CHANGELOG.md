# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

---

## [0.9.0] - 2025-01-19

### Added
- Export to Prompt (AI) feature - export container data to markdown format for AI prompts
- `ExportToPromptDialog` component with markdown preview and copy functionality
- `exportToPrompt` utility function for generating markdown exports
- Support for nested containers in export with calculated total weight
- Compact export format: `x4 **Name** (Brand, Color) (Expiration: date, Status) - weight`
- AI legend explaining data structure for better AI understanding
- Translations for all export texts (title, description, legend)
- Export button in container header dropdown menu

### Changed
- Export format now shows quantity as `x4` before item name instead of `(4x)` in parentheses
- Container headers in export no longer include color suffix
- Nested containers now display calculated total weight instead of 0g
- Export format optimized for AI consumption with compact structure

### Fixed
- Removed empty line after main title in export
- Fixed nested container weight calculation in export

---

## [0.8.0] - 2025-01-19

### Added
- Extended fields for gear items and containers (brand, color, price, URL, quality)
- ComboBox component with creatable options for brand and color fields
- Suggested values for colors (Olive, Coyote, Black, Tan, etc.) and brands (Helicon, Maxpedition, Mil-Tec, etc.)
- Column visibility management in items table with localStorage persistence
- Color visualization in items table - colored circle with color name
- Command and Popover UI components (shadcn-vue based)
- `getColorHex()` utility function for mapping color names to hex values
- `ITEMS_TABLE_COLUMN_VISIBILITY_KEY` for storing column visibility preferences

### Changed
- Brand and Color fields now use ComboBox component instead of plain Input
- Items table columns (brand, color) are hidden by default
- All table columns can now be shown/hidden via column visibility dropdown
- Color column displays colored circle next to color name
- Improved DataTable column visibility synchronization with v-model
- Enhanced DataTableToolbar to properly handle column visibility toggling

### Fixed
- Column visibility state now properly syncs between table and parent component
- Fixed issue where columns could be shown but not hidden
- Improved ComboBox filtering and creatable option display

---

## [0.7.0] - 2025-11-19

### Added
- Category pie chart visualization on container detail page
- Interactive donut chart showing category distribution by weight or quantity
- Chart legend with category breakdown and totals
- Percentage labels on chart segments
- Chart tooltips with formatted values (weight in grams, quantity with units)
- `CategoryPieChart` component with mode switching (weight/quantity)
- `CategoryPieChartLabels` component for segment percentage labels
- `CategoryPieChartLegend` component for category breakdown
- Chart UI components (`ChartContainer`, `ChartTooltip`, `ChartTooltipContent`, `ChartLegendContent`)
- `usePieChartGeometry` composable for chart geometry calculations
- Footer component with links to privacy, cookies, contact pages
- Privacy policy page
- Cookies information page
- Contact page
- GitHub icon component
- Container filters component for filtering containers list
- Color dot visualization component for containers

### Changed
- Enhanced container detail page with category visualization
- Improved container header with chart toggle
- Updated container card layout
- Enhanced i18n translations for chart-related labels

### Fixed
- TypeScript type errors in pie chart geometry composable

---

## [0.6.0] - 2025-11-19

### Added
- Container nesting functionality (FEATURE-008)
- Support for nested containers - containers can be added as items to other containers
- `parentContainerId` field in container model for direct parent-child relationships
- `containerId` field in item model for referencing nested containers
- Circular reference validation to prevent infinite nesting loops
- Recursive weight calculation for nested containers
- `AddNestedContainerDialog` component for selecting containers to nest
- Expandable rows in items table - click to expand and view nested container contents
- `ItemsTableNestedContainerRow` component for displaying nested container items
- Container color visualization in expanded nested container rows
- Filter to show only root containers (containers without parents and not used as items)
- Enhanced container actions menu - different actions for nested containers vs regular items
- "View Container" action in dropdown menu for nested containers
- Visual indicators for nested containers (icon, badge, clickable name)
- Container nesting utilities (`containerNesting.ts`) with functions for:
  - Circular reference detection
  - Root container filtering
  - Nested container retrieval
  - Container path calculation

### Changed
- Separated "Add Item" and "Add Container" actions in container detail page
- Container list page now filters out containers used as items when "Show only root containers" is enabled
- Improved `getRootContainers()` to check both `parentContainerId` and usage as items
- Container color now affects the border color of expanded nested container rows
- Nested container names are now clickable and styled with container color

### Fixed
- Root container filter now correctly excludes containers used as items in other containers

---

## [0.5.0] - 2025-11-18

### Added
- Category recognition system for items based on name keywords
- Container type recognition system based on name keywords
- Keyword dictionaries supporting both Polish and English
- Automatic category/type detection on name field blur
- Recognition utilities (`categoryRecognition.ts`, `containerTypeRecognition.ts`)

### Changed
- Category/type recognition now triggers on blur event (when user leaves name field) instead of during typing
- Recognition logic prioritizes longer keywords to avoid false matches (e.g., "bagażnik" matches "bagażnik" not "bag")
- Improved UX - users can type full names without premature category changes

---

## [0.4.0] - 2025-11-18

### Added
- Container color coding system
- Color picker in container form with 10 predefined colors (default, blue, green, red, yellow, purple, orange, pink, teal, indigo)
- Color dot indicator in container cards
- Color utilities (`containerColors.ts`) with Tailwind CSS classes
- Translations for all color names (English and Polish)

### Changed
- Container model now includes optional `color` field
- Container cards display color dot for visual distinction
- Improved visual organization of containers with color coding

---

## [0.3.0] - 2025-11-18

### Added
- Default values utility for new items (`defaultValues.ts`)
- Automatic browser locale detection on first visit
- HTML lang attribute automatically set based on detected locale

### Changed
- New item forms now pre-filled with sensible defaults:
  - Weight: 0.1 kg (instead of 0)
  - Weight unit: kg (instead of g)
  - Status: owned (instead of toBuy)
  - Quantity: 1
  - Priority: medium
  - Category: other
- Browser language is automatically detected and saved to localStorage
- Improved form initialization using `toTypedSchema` for better type safety

### Fixed
- TypeScript type issues in form initialization

---

## [0.2.0] - 2025-11-18

### Added
- Category icons for all item categories (water, food, shelter, fire, first aid, tools, navigation, communication, clothing, hygiene, other)
- CategoryIcon component for displaying category icons
- Icons displayed in items table and category selectors
- Feature implementation plans structure in `docs/features/`
- Roadmap updates including brand color selection planning

### Changed
- Enhanced visual recognition of categories with dedicated icons
- Improved UX in category selection with icon indicators

---

## [0.1.0] - 2025-11-18

### Added
- Basic project structure
- Gear management module
- Container and item system
- CRUD operations for containers and items
- Data persistence in localStorage
- Import/Export data in JSON format

