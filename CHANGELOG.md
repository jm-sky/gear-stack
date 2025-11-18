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

