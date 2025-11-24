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

## [2.9.0] - 2025-01-21

### Added
- **Item Ordering (FEATURE-018)**: Manual item ordering within containers
  - Added `order` field to items for custom sorting
  - Up/Down buttons in items table to change item order
  - Items automatically sorted by order (nulls last)
  - New items automatically get `order = max(order) + 1`
  - Order persisted in localStorage and database
  - Backend support: `order` field in database schema, API, and repository
  - Database migration: `015_add_order_field.py` for adding order column
  - Toast success notification only shown when using API/backend (not for localStorage)
  - Translations for order feature (PL/EN)

### Changed
- **ItemsTable**: Default sorting now uses `order` field instead of creation date
- **Backend Repository**: `get_items()` now sorts by `order` (ascending, nulls last), then by `created_at`
- **Backend Create Item**: Automatically assigns order if not provided (max + 1)
- **ROADMAP**: Marked FEATURE-018 (Item Ordering) as completed

### Technical Details
- Frontend: `order` field added to `IGearItem`, `ICreateItemDto`, `IUpdateItemDto`
- Backend: `order` field added to `GearItemDB` model, `ItemCreate`/`ItemUpdate` schemas
- Services: Both `gearItemLocalService` and `gearItemApiService` handle order field
- UI: Up/Down buttons disabled at top/bottom of list for better UX

---

## [2.8.0] - 2025-01-21

### Added
- **Extended Charts (FEATURE-019)**: Enhanced category pie chart with additional visualization modes
  - **Price Mode**: Pie chart showing cost distribution by category
    - Sums prices per category (price × quantity)
    - Percentage distribution of total cost
    - Displays only items with price data
    - Currency formatting using `formatCurrency()` utility
  - **Priority Mode**: Pie chart showing item distribution by priority level
    - Counts items per priority (critical, high, medium, low)
    - Percentage distribution of total items
    - Color-coded segments: Critical (red), High (orange), Medium (yellow), Low (green)
  - **Chart Mode Selector**: Extended with 4 options (Weight, Quantity, Price, Priority)
  - **New Utilities**:
    - `calculatePriceByCategory()` - Calculates price distribution by category
    - `calculateItemsByPriority()` - Calculates item distribution by priority
  - **i18n Translations**: Added `gear.chart.byPrice` and `gear.chart.byPriority` (EN/PL)

### Changed
- **CategoryPieChart**: Extended to support 4 chart modes (weight, quantity, price, priority)
- **CategoryPieChartLegend**: Updated to display data for all chart modes with proper formatting
- **usePieChartGeometry**: Enhanced to handle price and priority modes
- **Chart Types**: Updated `CategoryData` and `ChartDataPoint` interfaces to support optional `price` and `priority` fields
- **ROADMAP**: Marked currency support (FEATURE-017) and extended charts (FEATURE-019) as completed

---

## [2.7.0] - 2025-01-21

### Added
- **Public Item Detail Page**: Added read-only public item detail page (`PublicItemDetailPage.vue`)
  - Public route `/gear/public/:containerId/items/:itemId` for viewing public items
  - Displays all item information including category, priority, status, weight, price, and extended fields
  - Visual indicators for expired and expiring items
  - Empty state placeholder when no additional details are available
- **ItemsTable Public Mode**: Enhanced `ItemsTable` component with public mode support
  - New `publicMode` prop to enable public viewing mode
  - New `containerId` prop for navigation in public mode
  - Clicking items in public mode navigates to public item detail page instead of edit page
  - Actions column hidden in public mode (read-only)
  - Navigation to nested containers uses public routes in public mode
- **i18n Translations**: Added translations for public item detail page (EN/PL)
  - `gear.item.details` - Details section title
  - `gear.item.openLink` - Open link button text
  - `gear.item.noDetails` - Empty state message

### Changed
- **PublicContainerDetailPage**: Updated to pass `publicMode` and `containerId` props to `ItemsTable`
- **Routes**: Added `PublicItemDetail` route and helper function `PublicItemDetailById()`

---

## [2.6.0] - 2025-01-21

### Added
- **Currency Support (FEATURE-017)**: Comprehensive currency support throughout the application
  - Default currency setting in user preferences with auto-detection based on browser locale
  - Currency selector in item and container forms (8 supported currencies: PLN, EUR, USD, GBP, JPY, CHF, CAD, AUD)
  - Proper currency formatting using `Intl.NumberFormat` for locale-aware display
  - Currency display in tables, statistics, and container details
  - Multi-currency support in statistics (totals grouped by currency)
  - Helper function `getCurrency()` for consistent currency handling
  - Currency field added to `IGearItem` and `IGearContainer` types
  - Currency validation in form schemas
- **New Utilities**:
  - `currencyFormatter.ts` - Currency formatting utilities with `formatCurrency()`, `getCurrency()`, and `detectDefaultCurrency()`
  - Enhanced `containerCalculations.ts` with `calculateTotalPriceSync()` for multi-currency price calculations
- **i18n Translations**: Added currency-related translations (EN/PL) and date format `short` for both locales
- **Settings**: Added default currency selector to `GearPreferencesCard.vue`

### Changed
- **Forms**: Updated `ItemFormFields.vue` and `ContainerFormFields.vue` to include currency selection next to price input
- **Tables**: Added price column to `ItemsTable.vue` with formatted currency display
- **Statistics**: Enhanced `ContainerHeader.vue` to show total prices grouped by currency
- **Shopping Planning**: Updated `ShoppingPlanningPage.vue` to use currency formatting throughout
- **Settings**: Extended `IGearSettings` interface with `defaultCurrency` field

---

## [2.5.1] - 2025-11-24

### Added
- **Date Handling**: Added `date-fns` library for better date/time manipulation
- **New Components**:
  - `ContainerCardBadges` - Reusable component for displaying container badges
  - `ContainerCardCreatedDate` - Component showing creation date with time-ago format
  - `ContainerCardStats` - Component for displaying container statistics
  - `PublicContainerCard` - Card component for public container browser
  - `PublicContainerAuthorBadge` - Badge showing container author information
  - `LandingPageContainerCard` - Card component for landing page statistics
- **Composables**: New `useContainerTypeLabel` composable for centralized container type label management
- **Services**: Added `publicContainersService` for public container operations
- **Utils**: Added `dateTime.ts` and `smallDateTime.ts` utility functions

### Changed
- **Component Refactoring**: Refactored `ContainerCard` to use smaller, modular sub-components for better maintainability
- **Component Enhancements**:
  - Enhanced `Card` component with `as` prop for polymorphic rendering
  - Updated `ContainerFormFields` to use `getContainerTypeLabel` from composable
  - Refactored `ContainerHeader` to use `useContainerTypeLabel` composable
  - Updated `ExportToPromptDialog` to use `getContainerTypeLabel` function
- **Pages**:
  - Renamed `HomePage.vue` to `DashboardPage.vue` for clarity
  - Enhanced `LandingPage` with improved statistics display
  - Improved `PublicContainersBrowserPage` with better responsive design
  - Enhanced `PublicContainerDetailPage` with author information
  - Updated `PublicUserProfilePage` to show user's public containers
  - Refactored `ShoppingPlanningPage` UI improvements
- **Routing**: Added new routes for public user profiles and container details
- **Internationalization**: Updated Polish translations for better consistency (auth, gear, user modules)
- **Filters**: Enhanced `ContainersFilters` component with better UX

### Fixed
- Fixed incorrect display of custom container types in `ContainerFormFields` dropdown
- Fixed type label passing in export functionality (was passing computed value instead of function)

---

## [2.5.0] - 2025-11-24

### Release: Testing Infrastructure, UI/UX Enhancements & Deployment Automation

This release focuses on improving code quality with comprehensive unit tests, enhancing user experience with app versioning and authentication improvements, and streamlining deployment workflows.

### Added
- **Testing Infrastructure**:
  - Added 1348 lines of unit tests for utility functions (#114315c)
  - Tests for: `cn` function, `valueUpdater`, category recognition, container calculations, weight formatting, item retrieval, parameter recognition, suggested values, and type guards
  - Backend unit tests for auth service and utilities (#cc93948)
  - Enhanced test environment setup with proper database engine configuration

- **App Version & Build Information**:
  - App version and build date now displayed in footer (#35, #8b2f483)
  - Created `useAppVersion` composable for centralized version management (#78f52b6)
  - Dynamic company information from environment variables
  - Build date automatically injected via Vite during build process

- **Authentication & User Experience**:
  - New `AuthenticationRequiredAlert` component for profile pages (#ab3f991)
  - `DropdownMenuItemLink` component for better navigation in UserNav
  - OAuth button added to RegisterForm (#97caa9d)
  - Improved user authentication flow with conditional rendering

- **Deployment Automation**:
  - GitHub Actions workflow for automated deployment (#ce6d3cc)
  - Backend restart and migration script (`backend_restart_migrate.sh`) (#48fcb62)
  - Frontend build and deploy script (`frontend_build_deploy.sh`)
  - Comprehensive deployment documentation in `DEPLOYMENT.md`

- **Developer Experience**:
  - VSCode settings and Pyright configuration for backend development (#f9c3452)
  - Example environment variables for backend configuration (#3126fe6)
  - `pnpm-workspace.yaml` for monorepo support

- **UI Components**:
  - `GuestLayoutFooter` component for consistent footer across guest layouts (#78f52b6)

### Changed
- **Documentation Improvements**:
  - Added comprehensive `TODO_FEATURES.md` file consolidating features from both offline and online roadmaps (#b1792d3)
  - Updated `README.md` with link to TODO features list and completed features (#7bacf27)
  - Restructured roadmap: split into `ROADMAP_OFFLINE.md` and `ROADMAP_ONLINE.md`
  - Moved analysis docs to `docs/analysis/` directory
  - Moved archived docs to `docs/archive/` directory
  - Updated cursor rules with Question vs. Action Protocol and TailwindCSS best practices

- **User Authentication Refactoring**:
  - Refactored user profile handling with consistent `avatarUrl` usage (#ab3f991)
  - UserNav now conditionally shows login/register options based on auth status
  - Improved profile page with authentication-aware components
  - Enhanced route handling with constants for user profile paths

- **Footer Component Refactoring**:
  - Replaced hardcoded footer content with reusable `GuestLayoutFooter` component
  - Centralized footer logic in `AppFooter.vue` with dynamic configuration
  - Consistent footer across `GuestLayoutCentered`, `GuestLayoutCenteredGlass`, and `GuestLayoutTwoColumns`

- **Configuration Updates**:
  - Updated `.env.example` to use array syntax for CORS settings (#6c716ac)
  - Enhanced `.gitignore` for better environment file handling
  - Removed draft deployment configurations for cleaner repo

- **Public Containers UI**:
  - Improved responsive design for public containers browser (#752e210)
  - Enhanced mobile layout for public container detail pages

- **Deployment Scripts**:
  - Refactored `deploy.sh` for better maintainability (#48fcb62)
  - Separated frontend build logic into dedicated script
  - Improved CI/CD environment variable handling

### Fixed
- **OAuth Internationalization**:
  - Fixed OAuth callback i18n interpolation syntax (#e0d2499)
  - Removed debug log from reCAPTCHA utility

- **Deployment**:
  - Fixed CI environment variable handling in deployment script
  - Removed pnpm version specification from deploy workflow (#36)
  - Updated deployment branch configuration

- **Code Quality**:
  - Automatic formatting with Black for Python backend code (#80a9012)
  - Fixed various TypeScript and ESLint issues

### Security
- Enhanced backend test coverage for authentication and authorization flows
- Improved environment variable handling and validation

### Development
- Backend restart and migration workflow streamlined
- Improved local development setup with proper configuration examples
- Better separation of concerns between frontend and backend deployment

---

## [2.4.0] - 2025-11-23

### Added
- **Shopping List Features**:
  - Shopping list persistence functionality (#24)
  - "Add All" functionality for shopping lists (#24)
  - Shopping planning page functionality (#21)
  - Enhanced shopping list functionality and item editing (#23)

- **Progressive Web App (PWA)**:
  - PWA support with Vue and Vite (#19)
  - Installable web application support
  - Offline capabilities

- **Internationalization**:
  - Email internationalization and translations (#15)

- **Documentation**:
  - AI plan documentation

### Changed
- **Data Structure**:
  - Unified brand, category, and type fields (#20)
  - Refactored to use 'value' instead of 'key' and 'label' for custom items
  - Simplified settings card components for brands, categories, and container types

- **OAuth Integration**:
  - Implemented internationalization for OAuth login
  - Improved OAuth callback page with better error handling

### Fixed
- Shopping list and item page issues (#22)
- Removed unnecessary v-if from create container button
- Improved OAuth error message display

---

## [2.3.0] - 2025-11-22

### Added
- **Testing Infrastructure**: Set up Vitest testing framework
  - Installed Vitest, @vitest/ui, and happy-dom
  - Created `vitest.config.ts` configuration
  - Added test scripts: `test`, `test:ui`, `test:run`, `test:coverage`
  - **57 unit tests** for markdown import service with 100% pass rate

- **Markdown Import Enhancements**:
  - **Container Descriptions**: Support for parsing container descriptions from markdown
    - Extracts text between container header and first item
    - Supports multi-line descriptions with empty lines
  - **Price Parsing**: Comprehensive price and currency support
    - PLN formats: `100PLN`, `10 PLN`, `10,00 PLN`, `1 000,00 PLN`, `10zł`
    - USD formats: `$50`, `50$`, `50 USD`
    - EUR formats: `€100`, `100€`, `100 EUR`
    - GBP formats: `£75`, `75£`, `75 GBP`
  - Added `price` and `currency` fields to `ICreateItemDto` type
  - Added `description`, `price`, and `currency` fields to `IMarkdownImportResult`

- **Error Handling**:
  - Global chunk loading error handler for post-deployment errors
  - User-friendly dialog with i18n support (PL/EN)
  - Automatic detection of ChunkLoadError and related failures
  - Graceful page reload option

- **404 Page**:
  - New NotFoundPage component with proper UI
  - Wildcard route `/:pathMatch(.*)*` for catching all unmatched routes
  - Helpful navigation links to Containers, Dashboard, and Settings
  - Full i18n support (PL/EN)

- **Translations**:
  - Added `errors.chunkLoadError` translations (PL/EN)
  - Added `notFound` page translations (PL/EN)

### Fixed
- **Profile Page Mobile**: Fixed email overflow on mobile devices
  - Added `break-all` class to email display
  - Added `flex-shrink-0` to Mail icon to prevent crushing

- **Markdown Export**: Fixed description format in newline mode
  - Descriptions now appear alone on second line
  - Metadata (UUID, quantity, brand, weight) stays on first line
  - No more mixing of description with other fields

### Changed
- Updated ROADMAP.md with completed features and new planned tasks
- Enhanced markdown import parser with better field extraction
- Improved type safety with currency field additions

---

## [2.2.1] - 2025-11-22

### Fixed
- **reCAPTCHA Configuration**: Fixed environment variable naming issues
  - Changed `GOOGLE_RECAPTCHA_SITE_KEY` → `RECAPTCHA_SITE_KEY` in backend
  - Changed `GOOGLE_RECAPTCHA_SECRET_KEY` → `RECAPTCHA_SECRET_KEY` in backend
  - Enabled reCAPTCHA in both frontend and backend configurations
  - Added reCAPTCHA variables to docker-compose.yml and docker-compose.dev.yml
  - Created diagnostic script `backend/scripts/check_env.py` for environment verification

- **reCAPTCHA Logging**: Enhanced debugging capabilities
  - Added detailed logging in `backend/app/core/recaptcha.py`
  - Added logging in `backend/app/modules/auth/decorators.py`
  - Logs now show configuration, request/response details, and error codes

- **OAuth Authentication**: Fixed critical bugs preventing OAuth login
  - Fixed `login_with_oauth` to support both camelCase and snake_case field names
  - Fixed missing `logger` import in `backend/app/modules/auth/router.py`
  - Fixed incorrect settings path: `settings.jwt` → `settings.security`
  - Added detailed OAuth callback logging for debugging

- **Frontend OAuth Error Handling**: Improved user experience
  - Replaced hardcoded paths with `AuthRoutePaths` variables in OAuthCallbackPage
  - Enhanced error message extraction from API responses
  - Increased error display timeout from 2s to 3s

### Security
- **reCAPTCHA v3**: Now fully operational with score-based bot detection (min score: 0.5)
- **OAuth**: Google OAuth authentication now functional end-to-end

---

## [2.2.0] - 2025-01-21

### Release: Security Enhancements - reCAPTCHA & OAuth Integration

This release introduces major security features including Google reCAPTCHA v3 protection and OAuth authentication infrastructure.

### Added
- **reCAPTCHA v3 Integration (Frontend)**: Invisible bot protection on all authentication forms
  - Auto-loads reCAPTCHA script on app startup
  - Integrated into LoginForm, RegisterForm, and ForgotPasswordPage
  - Sends reCAPTCHA tokens to backend for verification
  - Zero friction for legitimate users (invisible verification)
  - Added `useRecaptcha` composable and utility functions
  - Backend already supported reCAPTCHA, now enabled with frontend integration

- **OAuth Infrastructure (Backend - 90% Complete)**: Foundation for social login
  - Complete OAuth service with Google provider implementation (`app/core/oauth.py`)
  - OAuth configuration in settings (`OAuthSettings`)
  - Database migration for OAuth fields (provider, provider_id, avatar_url)
  - Repository methods: `create_oauth_user()`, `get_user_by_oauth_provider()`
  - OAuth schemas: `OAuthAuthUrlRequest/Response`, `OAuthCallbackRequest/Response`
  - User model updated to support nullable passwords (OAuth users)
  - OAuth fields added to UserDB model

- **2FA Settings Visibility Fix**: Security settings card now visible on Settings page
  - Shows TOTP (Authenticator App) status
  - Shows WebAuthn/Passkeys status
  - Displays preferred 2FA method selector
  - Previously existed but wasn't shown due to missing import

- **Documentation**: Comprehensive implementation guides
  - `FEATURE-014-oauth-authentication.md` - Complete OAuth implementation plan
  - `FEATURE-015-recaptcha-integration.md` - Complete reCAPTCHA implementation plan
  - `IMPLEMENTATION_STATUS.md` - Current status and remaining work tracker
  - `IMPLEMENTATION_COMPLETE.md` - Detailed progress report

### Changed
- User model `hashedPassword` field is now nullable (supports OAuth users without passwords)
- Repository `_map_user` method updated to handle OAuth fields
- Auth types updated to include `recaptchaToken` field in login/register/forgot-password requests
- Config updated with reCAPTCHA and OAuth settings

### Security
- ✅ **reCAPTCHA Protection Active**: Login, register, and forgot-password endpoints now protected against bots
- ✅ **OAuth CSRF Protection**: State parameter generation for preventing CSRF attacks
- ✅ **Score-based Verification**: reCAPTCHA uses score threshold (0.5) to detect suspicious activity
- ✅ **Action Verification**: Backend verifies reCAPTCHA action matches expected endpoint

### Technical Details

**Environment Variables**:
- Backend: `RECAPTCHA_ENABLED=true`, `GOOGLE_RECAPTCHA_SITE_KEY`, `GOOGLE_RECAPTCHA_SECRET_KEY`
- Frontend: `VITE_GOOGLE_RECAPTCHA_SITE_KEY`, `VITE_GOOGLE_OAUTH_CLIENT_ID`
- Backend OAuth: `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`, `GOOGLE_OAUTH_REDIRECT_URI`

**Database Changes**:
- New migration: `011_add_oauth_fields.py`
- Added columns: `oauth_provider`, `oauth_provider_id`, `avatar_url`
- Made `hashed_password` nullable for OAuth users
- Index created on `(oauth_provider, oauth_provider_id)` for efficient lookups

**Remaining Work** (OAuth Frontend - ~6-8 hours):
- OAuth login/callback composable (`useOAuth`)
- OAuth button component
- OAuth callback page
- Integration into login/register pages
- OAuth endpoints in auth router (backend)
- OAuth service method in auth service (backend)

---

## [2.1.1] - 2025-01-27

### Added
- **Landing Page Local Data Detection**: Landing page now detects when user is not logged in but has containers stored in localStorage
  - Shows container summary statistics (containers count, items count, ready containers count)
  - Displays login/register call-to-action buttons prominently
  - Encourages users to log in or register to synchronize their local data
  - Summary section only appears when local containers exist and user is not authenticated

### Changed
- Landing page now conditionally shows features section or local data summary based on authentication and localStorage state
- Improved user experience for users with local data who haven't logged in yet

---

## [2.1.0] - 2025-01-27

### Release: Hybrid Mode & Offline-First Architecture

This release introduces a hybrid mode that allows the application to work seamlessly both with and without user authentication. Users can now use the app immediately without creating an account, with all data stored locally. After logging in, the app automatically switches to API mode while maintaining localStorage as a backup.

**Key highlights:**
- **Hybrid Mode**: Automatic switching between localStorage (offline) and API (online) based on authentication status
- **Zero-Friction Onboarding**: Users can start using the app immediately without registration
- **Data Migration**: Optional migration dialog to transfer local data to API after first login
- **Offline-First**: All pages and features accessible without login
- **Smart Fallback**: Automatic fallback to localStorage on API errors
- **Settings Translations**: Fixed missing translations for settings page and delete account feature

**New Features:**
- **Hybrid Services**: All services (Gear, Settings, User) now support both localStorage and API modes
- **Data Migration Dialog**: User-friendly dialog to migrate local data to API after login
- **Landing Page Enhancement**: Added "Add Container" button for immediate access
- **Route Accessibility**: All gear pages accessible without authentication
- **Conditional Features**: Delete Account only visible when authenticated

**Technical improvements:**
- Extended `useBackend` composable with `isAuthenticated` and `shouldUseAPI` helpers
- Unified conditional logic across all services (Gear, Settings, User)
- Enhanced error handling with automatic localStorage fallback
- Improved service architecture with hybrid implementations
- Fixed translation structure for settings page sections

**Breaking Changes:**
- None - fully backward compatible

This release maintains full backward compatibility while adding powerful new capabilities for both offline and online usage.

---

## [2.0.0] - 2025-11-21

### Release: Backend Integration & Authentication

This is the second major release (2.0.0) of Gear Stack, introducing backend integration and full authentication system. The application now supports user accounts, authentication, and backend API integration while maintaining backward compatibility with local storage.

**Key highlights:**
- **Backend Integration**: Full API integration with backend services
- **Authentication Module**: Complete user authentication system with email verification
- **Two-Factor Authentication (2FA)**: Enhanced security with WebAuthn support
- **User Management**: User accounts, profiles, and session management
- **Logout Functionality**: Proper session cleanup and logout flow
- **Enhanced Services**: Refactored gear services with container/item API services
- **Improved Error Handling**: Enhanced Vite configuration and interceptor error handling
- **Routing Updates**: Updated routing and layout for landing and home pages
- **Container Data Handling**: Enhanced container data handling with missing fields support

**Technical improvements:**
- Service layer refactoring for better separation of concerns
- Enhanced API interceptors with improved error handling
- Updated application settings and user authentication flow
- Workflow permissions fixes for code scanning alerts

This release marks the transition from a pure local storage application to a full-stack application with backend support, while maintaining all existing features and data compatibility.

---

## [1.0.0] - 2025-11-21

### Release: Full local storage

This is the first major release (1.0.0) of Gear Stack, marking the completion of the full local storage implementation. All core features are now functional and working entirely with localStorage, without requiring a backend, database, or authentication.

**Key highlights:**
- Complete gear management system with containers and items
- Full import/export functionality (JSON and Markdown formats)
- Container nesting and relationships
- Extended fields (brand, color, price, URL, quality)
- Weight management with multiple unit support (g, kg, oz, lb)
- Category recognition and parameter recognition
- Container cloning and catalog-based item addition
- Comprehensive settings system (core and gear-specific)
- Full internationalization (PL/EN)
- Responsive design with mobile support

All features documented in the ROADMAP are now implemented and working with localStorage. Future versions may include backend integration for multi-device synchronization and collaboration features.

---

## [0.22.0] - 2025-01-21

### Added
- **Feature: Add Existing Items to Container** - Users can now add existing items from other containers to the current container using a catalog selector
  - New tabs in ItemFormPage: "New Item" and "From Catalog"
  - ItemCatalogSelector component with fuzzy search, category icons, and container badges
  - Item linking support with `linkedItemId` field (future-ready for backend integration)
  - Items already in current container are automatically excluded from catalog
  - Form resets when switching between tabs
  - Alphabetical sorting of catalog items
  - Translations for catalog mode (PL/EN)

### Changed
- Extended `IGearItem` interface with `linkedItemId?: TUUID` field for item linking
- Added `getAllItemsForCatalog()` and `getItemWithContainer()` methods to gear service
- Extended `getAllItems()` utility to support filtering by container ID

### Fixed
- Fixed TypeScript type errors in ItemCatalogSelector component

---

## [0.21.0] - 2025-01-21

### Added
- **Container Cloning Feature**:
  - Added "Duplicate Container" action in container dropdown menu
  - CloneContainerDialog with options:
    - Editable new container name (default: "[Copy] Original Name")
    - Checkbox: "Include nested containers"
    - Checkbox: "Include item prices"
  - Deep cloning with new UUIDs for all entities
  - Preserves all container metadata (type, color, brand, description, etc.)
  - Toast notification with success message
  - Translations for cloning feature (PL/EN)

- **TableEmptyDecorated Component**:
  - New reusable component for decorated empty states in tables
  - Supports custom icon, title, description
  - Optional action button support
  - Consistent styling across all empty states

- **HomePage Empty State Options**:
  - Added "Import from Markdown" option in empty state
  - Added "Generate Sample Set" option in empty state
  - Options displayed after "or" separator below main action

- **Query Parameter Support for Import**:
  - ContainersListPage now opens import dialog automatically when URL contains `?import=true`
  - Allows direct navigation to import from HomePage

### Changed
- **UI/UX Improvements**:
  - Improved empty states with decorated component (TableEmptyDecorated)
    - AllItemsPage, ItemsTable now use TableEmptyDecorated
    - DataTableEmpty refactored to use TableEmptyDecorated internally
    - Consistent styling with icon in circular background
  - Footer mobile layout improved (flex-col sm:flex-row with better gap spacing)
  - Color grid in ContainerFormPage now uses responsive grid (5 columns on mobile, 10 on desktop)
  - Horizontal scroll indicator added to DataTable (gradient hint on mobile)
  - Search placeholder in ContainersListPage changed from "Search items..." to "Search containers..."

- **Button Visibility Logic**:
  - Header buttons on ContainersListPage and HomePage now hidden when containers list is empty
  - Prevents duplicate "Create Container" buttons
  - Dropdown menu always visible on ContainersListPage (contains import option)

- **Accessibility**:
  - Added aria-labels to all icon-only buttons:
    - ContainerCardActions dropdown trigger
    - ContainerHeader actions (SparklesIcon, MoreVertical)
    - ContainersListPage actions (Sparkles)
    - ContainersListPageDropdown trigger
  - Added translations for "more actions" (PL/EN)

### Fixed
- **Critical Mobile UX Issues**:
  - Fixed color grid layout on mobile (ContainerFormPage) - now displays 5 columns instead of 10 in single row
  - Fixed footer mobile layout - better spacing and responsive columns
  - Fixed duplicate "Create Container" buttons on ContainersListPage and HomePage
  - Fixed placeholder text inconsistency ("Search items..." → "Search containers...")

- **Component Issues**:
  - Fixed TableEmptyDecorated component - proper icon component handling with computed
  - Fixed empty states across application - consistent styling and layout
  - Fixed horizontal scroll indicator positioning in DataTable

---

## [0.20.0] - 2025-01-20

### Added
- **maxWeight Feature** (Container Weight Limits):
  - Added `maxWeight` and `maxWeightUnit` fields to containers
  - Weight limit input in container form (Extended Fields section)
  - Automatic weight calculation including container's own weight
  - Visual indicators in ContainerHeader:
    - Warning badge when weight exceeds 90% of limit (orange)
    - Exceeded badge when weight exceeds 100% (red)
    - Color-coded weight display (green/yellow/orange/red)
    - Progress bar showing weight usage percentage
  - Stats card displays "currentWeight / maxWeight" with visual progress bar
  - Weight limit calculations: `calculateWeightLimitPercentage()` and `isWeightLimitExceeded()`
  - Translations for maxWeight feature (PL/EN)

- **hideWhenNested Feature** (Smart Container Filtering):
  - Added `hideWhenNested` boolean field to containers
  - Checkbox in container form: "Hide on list when nested"
  - Automatic filtering in ContainersListPage - containers with `hideWhenNested=true` and `parentContainerId` are hidden from main list
  - Filter respects "Show only root containers" toggle
  - Helps organize nested containers without cluttering main list

- **Parameter Recognition in ContainerForm**:
  - Added "Recognize Parameters" button to container form
  - Recognizes brand from container name using fuzzy matching
  - Same functionality as ItemForm parameter recognition
  - Toast notifications for recognition results

- **UI/UX Improvements**:
  - Container name is now a clickable link in ItemFormPage (navigates to container details)
  - Added `flex-1` to form buttons for better mobile layout:
    - ItemFormFields: Cancel and Save buttons have equal width
    - ContainerHeader: Add Item button expands on mobile (`flex-1 sm:flex-none`)
  - Build script now includes deployment to `/var/www/gear-stack`

### Fixed
- Fixed brand and color displaying as lowercase in UI
  - Changed `getBrandOptions()` to use original case instead of `toLowerCase()`
  - Changed `getColorOptions()` to use original case instead of `toLowerCase()`
  - Brand badge now displays with normal-case (e.g., "Maxpedition" instead of "maxpedition")
- Fixed missing Checkbox import in ContainerFormFields
- Fixed weight calculation to include container's own weight in total

### Changed
- Updated ROADMAP with new features:
  - Added maxWeight feature documentation with use cases
  - Added container/item management features (cloning, existing items catalog)

---

## [0.19.0] - 2025-01-22

### Added
- **Parameter Recognition Feature**:
  - Added automatic recognition of brand and color from item names
  - New utility: `parameterRecognition.ts` with fuzzy matching against `SUGGESTED_BRANDS` and `SUGGESTED_COLORS`
  - "Recognize Parameters" action in item row actions menu
  - "Recognize Parameters" button in item form (fills brand/color fields)
  - Bulk action "Recognize Parameters for All Items" in container header dropdown menu
  - Recognition only fills empty fields (doesn't overwrite existing values)
  - Integration with existing suggested values dictionaries

### Changed
- **UI Improvements**:
  - Added visual separator in item form between fields and actions
  - Improved parameter recognition UX with proper toast notifications
  - Badge component now properly imported from registry in `PageListHeader.vue`

### Fixed
- Fixed TypeScript error in parameter recognition (handling undefined first word)
- Improved nested container display - nested containers now have bold font and clickable links to container detail page

---

## [0.18.0] - 2025-01-21

### Added
- **Modular Settings Architecture**:
  - Separated core settings (locale, dark mode, preferred weight unit) from gear-specific settings (custom categories, container types)
  - Created dedicated services: `CoreSettingsService` and `GearSettingsService`
  - Created separate Pinia stores: `useSettingsStore` and `useGearSettingsStore`
  - Created separate composables: `useSettings()` and `useGearSettings()`
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

