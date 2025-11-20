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

## [0.18.0] - 2025-01-21

### Added
- **Modular Settings Architecture**:
  - Separated core settings (locale, dark mode, preferred weight unit) from gear-specific settings (custom categories, container types)
  - Created dedicated services: `CoreSettingsService` and `GearSettingsService`
  - Created separate Pinia stores: `useCoreSettingsStore` and `useGearSettingsStore`
  - Created separate composables: `useCoreSettings()` and `useGearSettings()`
  - Modular SettingsPage component with slot-based architecture for extensibility
  - Settings page now supports adding module-specific settings via slots

### Changed
- **Settings Architecture Refactoring**:
  - Split monolithic settings into core and gear modules
  - Core settings stored in `core-settings` localStorage key
  - Gear settings stored in `gear-settings` localStorage key
  - Automatic migration from old unified settings storage
  - Settings page structure: core settings in module, gear settings added via slot in `/src/pages/settings/`
  - All components updated to use appropriate settings composables

### Fixed
- Improved code organization and maintainability through modular architecture
- Better separation of concerns between core application settings and module-specific settings

---

## [0.17.0] - 2025-01-21

### Added
- **Imperial Weight Units Support**:
  - Added support for ounces (oz) and pounds (lb) as weight units
  - Users can now select oz and lb in item and container forms
  - Preferred weight unit setting now includes oz and lb options
  - All weight conversion functions updated to support imperial units
  - Conversion rates: 1 oz = 28.3495 g, 1 lb = 453.592 g

### Changed
- **Weight Unit Type**: Extended `TGearWeightUnit` type from `'g' | 'kg'` to `'g' | 'kg' | 'oz' | 'lb'`
- **Weight Conversion Functions**: Updated all conversion functions in `formatWeight.ts` to handle oz and lb
- **Form Validation**: Updated zod schemas to accept oz and lb as valid weight units
- **Markdown Import/Export**: Parser now recognizes and handles oz and lb in markdown format
- **Translations**: Added translations for oz and lb in both English and Polish

### Technical Details
- Added constants: `GRAMS_PER_OUNCE = 28.3495` and `GRAMS_PER_POUND = 453.592`
- Updated all weight-related interfaces and types to support imperial units
- All weight displays automatically convert to preferred unit (including oz/lb)

---

## [0.16.0] - 2025-01-21

### Added
- **Guidelines Dialog Component**:
  - Created dedicated `GuidelinesDialog` component for displaying formatting guidelines
  - Reusable component used in both Export and Import dialogs
  - Guidelines are now shown in a modal dialog instead of being copied directly
  - Users can view guidelines and copy them manually when needed

### Changed
- **Guidelines Display**:
  - Guidelines button now opens a dialog instead of copying to clipboard immediately
  - Guidelines template has been shortened while keeping essential information
  - Reduced number of examples to make guidelines more concise
  - Dialog is smaller than parent dialogs for better UX

- **Code Refactoring**:
  - Extracted Guidelines functionality into reusable component
  - Removed code duplication between Export and Import dialogs
  - Improved maintainability and consistency

---

## [0.15.0] - 2025-01-21

### Added
- **Preferred Weight Unit Setting**:
  - Users can now set their preferred weight unit (g or kg) in settings
  - All displayed weights across the application (tables, cards, headers) are automatically converted to the preferred unit
  - Forms can still use different units, but display is consistent
  - Setting is saved in localStorage and synchronized throughout the application
  - UI option added to Preferences settings page

- **Export Configuration Options**:
  - Added export options dialog with checkboxes to control markdown export content:
    - Show UUID in export
    - Show weight
    - Show color
    - Show brand
    - Show nested container reference (e.g., `[#bagaznik]`)
    - Show legend
  - All options are reactive - markdown updates in real-time when toggling options
  - Options are saved per export session

### Changed
- **Export Dialog**: Refactored to accept container/containers directly instead of pre-generated markdown, allowing real-time updates based on options
- **Weight Display**: All weight displays now use preferred unit from settings instead of automatic unit selection
- **Export Format**: Container ID references (`[#id]`) in headers and items are now controlled by export options

### Fixed
- Fixed legend duplication when exporting multiple containers - legend now appears only once at the end
- Fixed Checkbox component usage - now uses standard `v-model` instead of deprecated `v-model:checked` for regular refs

### Documentation
- Added `.cursorrules` file with Reka-ui Checkbox usage guidelines
- Updated `CLAUDE.md` with UI component notes about Checkbox usage
- Split ROADMAP into front-end only (`ROADMAP.md`) and backend-required (`ROADMAP_V2.md`) features

---

## [0.14.0] - 2025-01-20

### Added
- **Container Weight and URL Fields**:
  - Containers can now have weight and weight unit (g/kg) fields
  - Containers can now have URL field for linking to product pages or resources
  - Weight and URL fields added to container form
  - Container header displays weight and URL (if provided)
  - Weight displayed as badge in container header
  - URL displayed as clickable link in container header

- **Enhanced Export/Import**:
  - Export now includes container weight in format: `## Container Name [#id] (Type) <URL> - [weight]g`
  - Import parser now extracts container weight and URL from markdown headers
  - Guidelines template updated to document container weight and URL format

### Changed
- **Guidelines Template**: Moved from `ExportToPromptDialog.vue` to `markdownImportService.ts` for better code organization and reusability
- **Container Form**: Added weight, weightUnit, and URL input fields with proper validation

### Fixed
- Fixed TypeScript errors in markdown import service (containerUrl undefined check, container type definition)

---

## [0.13.1] - 2025-01-19

### Fixed
- **Nested Container Import**: Fixed issue where nested containers were not properly linked during markdown import
  - Import now correctly resolves `nestedContainerId` (slug) to actual container UUID
  - Two-phase import process: containers created first, then items with nested container relationships resolved
  - Nested containers (e.g., "Bagażnik" inside "Samochód Opel Zafira") now properly create parent-child relationships

---

## [0.13.0] - 2025-01-19

### Added
- **UUID Support for Import/Export Workflow**:
  - Export now includes `[uuid:xxx]` for both containers and items
  - Import parser extracts UUIDs from markdown format
  - Import mode selection: "Update Existing (by UUID)" vs "Create New"
  - Update workflow: items/containers with matching UUIDs are updated instead of created
  - Radio Group UI component for import mode selection
  - Success message differentiates between created and updated items

- **Enhanced Guidelines Template**:
  - Added UUID documentation to formatting guidelines
  - Updated examples to show UUID format in all samples
  - Documented update vs create workflow in guidelines

### Changed
- **Export Format**: All items and containers now include `[uuid:xxx]` after name/header
  - Container format: `## Name [#slug-id] [uuid:xxx] (Type)`
  - Item format: `- **Name** [uuid:xxx] x2 (Brand, Color) ...`
- **Import Dialog**: Shows mode selection only when UUIDs are detected in markdown
- **Import Logic**: Automatically detects UUIDs and enables update workflow

### Fixed
- Import now properly handles UUID-based updates for existing items and containers

---

## [0.12.0] - 2025-01-19

### Added
- **AI Prompt Export Enhancements**:
  - "Export to Prompt (AI)" button for all containers on ContainersListPage
  - "Guidelines" button in ExportToPromptDialog with comprehensive markdown formatting template
  - URL support in items (auto-detected from `http://`, `https://`, `www.`)
  - Nested container support with ID references using `[#slug-id]` format
  - Container IDs auto-generated as slugs from container names

- **Enhanced Markdown Import/Export**:
  - Unified format for import and export with flexible parsing
  - Parser recognizes URLs in angle brackets or plain format
  - Parser extracts `[#id]` from container headers and items
  - Support for nested container relationships via ID references
  - Weight is now optional (defaults to 100g if not specified)
  - Quantity can appear anywhere in the line (flexible regex matching)

- **Mobile/RWD Improvements**:
  - Click-based dropdown menu for UserNav (replaces hover-only)
  - Proper overflow handling for tables on mobile devices
  - Added `min-width: 640px` to tables with horizontal scroll
  - Responsive dialogs with `w-[95vw]` on mobile
  - Gap between search and column visibility in DataTable toolbar
  - Increased card padding on mobile (p-4 instead of p-2)

### Changed
- **Table Overflow Chain**: Fixed multi-layer overflow issues by adding `max-w-full overflow-hidden` to all page wrappers and DataTable root
- **AuthenticatedLayout**: Reduced padding on mobile (px-2) for more content space
- **Global CSS**: Added `overflow-x-hidden` to html, body, and #app to prevent horizontal scroll
- **UserNav**: Migrated from CSS hover to DropdownMenu component for better mobile support
- **Export Format**: All container headers now include `[#id]` for identification
- **Guidelines Template**: Updated with complete formatting rules, examples, and nested container documentation

### Fixed
- Tables exceeding viewport width on mobile devices
- Dropdown menus not opening on touch devices
- Multiple overflow wrappers causing scroll issues
- Missing gap between DataTable toolbar elements
- Dialog max-width issues on small screens

---

## [0.11.1] - 2025-01-19

### Added
- "Delete All Containers" button in containers page dropdown menu
- Confirmation dialog for deleting all containers with warning message
- `deleteAllContainers()` method in store, service, and composable
- Success toast notification after deleting all containers
- Translations for delete all feature (English and Polish)

---

## [0.11.0] - 2025-01-19

### Added
- Markdown import feature - import containers and items from markdown files
- `ImportMarkdownDialog` component with preview and error handling
- `markdownImportService` with intelligent parsing:
  - Parses `## Container` headers as containers
  - Parses `- Item` lines as items
  - Extracts brands from bold text (`**Brand**`)
  - Parses parameters from parentheses `(color, x5, 500g)`
  - Detects quantity from `x5` or `×5` patterns
  - Auto-categorizes items based on keywords
  - Matches colors and brands against predefined lists
  - Sets default weight (100g) for items without specified weight
- Import button in containers page dropdown menu
- Translations for import feature (English and Polish)
- `.claude/commands/release-version.md` - slash command for Claude Code

### Fixed
- Mobile responsiveness - tables now have horizontal scroll on mobile devices
- Mobile navigation - nav links now available in user dropdown menu on mobile
- All data table components updated with `overflow-x-auto` for better mobile UX

---

## [0.10.0] - 2025-01-20

### Added
- All Items page - view and manage all items from all containers in one unified table
- `AllItemsPage` component with full item listing across all containers
- `getAllItems` utility function to aggregate items from all containers
- `allItemsColumns` utility for All Items table column definitions
- Navigation link to All Items page in main navigation
- Container information column in All Items table (shows container name and color)
- Translations for All Items page (English and Polish)
- `ALL_ITEMS_TABLE_COLUMN_VISIBILITY_KEY` for storing All Items table column visibility preferences

### Fixed
- Nested container weight now displays sum of all items in container instead of 0g
- Weight column alignment improved with right-aligned text in items table

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

