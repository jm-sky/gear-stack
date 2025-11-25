# Gear Stack

A comprehensive web application for managing survival gear, bug-out bags, and outdoor equipment with multi-user support, cloud synchronization, and advanced organization features.

<img width="1527" height="547" alt="obraz" src="https://github.com/user-attachments/assets/9e71110e-0941-418b-b853-2cd9fe43aa91" />

## Overview

Gear Stack is a full-stack application designed for outdoor enthusiasts, preppers, and survival gear collectors. It combines an intuitive front-end interface with a robust backend to provide secure multi-user gear management with cloud synchronization across devices.

**Key Capabilities:**
- **Multi-User Platform** - Secure user accounts with authentication and authorization
- **Hybrid Architecture** - Works offline with localStorage, syncs with cloud when online
- **Advanced Organization** - Hierarchical container system with nested items and weight tracking
- **Rich Metadata** - Track weight, expiration dates, priorities, brands, and custom categories
- **Data Portability** - Import/export functionality with AI-ready markdown format

> 📋 **[Zobacz pełną listę funkcjonalności w języku polskim →](./FEATURES.md)**

---

### Core Features
- Manage multiple gear lists (e.g., Bug-Out Bag, EDC, Get Home Bag, custom).
- Add, edit, and remove items.
- Item fields: name, category, quantity, weight, notes, expiration date (optional), priority.
- Mark items as *owned*, *missing*, or *to buy*.
- Automatic calculation of total pack weight.
- Kit readiness/completeness indicator.

---

### User Experience
- List view and detailed item view.
- Search, filter, and sort by category, weight, priority, or status.
- Highlight expired or soon-to-expire items.
- Quick actions: mark as used, missing, expired.

---

### Data Architecture
- **Hybrid Persistence**:
  - Client-side: `localStorage` for offline-first functionality
  - Server-side: PostgreSQL database for multi-device sync
- **Automatic Synchronization** - Changes sync to cloud when online
- **Conflict Resolution** - Smart merging of offline changes
- **Data Portability** - Import/export in JSON format

---

### Technical Stack

**Frontend:**
- Vue 3.5+ with TypeScript & Composition API
- Pinia for state management
- Vue Router for navigation
- TailwindCSS v4 + shadcn-vue components
- VeeValidate + Zod for form validation
- TanStack Query for server state management
- vue-i18n for internationalization

**Backend:**
- FastAPI (Python) with async/await
- PostgreSQL database
- SQLAlchemy ORM with async support
- JWT authentication with refresh tokens
- Rate limiting and reCAPTCHA protection
- Modular architecture (auth, two-factor, email)

**Infrastructure:**
- Docker containerization
- Nginx reverse proxy
- Development and production configurations

---

## Business Features

### 🔐 User Management & Security
- **User Registration & Login** - Email/password authentication with secure password hashing
- **OAuth Social Login** - Sign in with Google (GitHub support planned)
- **Email Verification** - Confirm email addresses for account security
- **Two-Factor Authentication (2FA)** - TOTP (authenticator apps) and WebAuthn (passkeys/security keys)
- **Password Management** - Reset forgotten passwords, change password for authenticated users
- **reCAPTCHA v3 Protection** - Invisible bot protection on login, registration, and password reset
- **Session Management** - JWT tokens with automatic refresh, secure logout
- **Account Deletion** - GDPR-compliant soft delete with confirmation

### 👤 User Profile
- **Profile Management** - Update name, email, and preferences
- **Avatar Support** - OAuth providers automatically provide profile pictures
- **Preferred Settings** - Weight units, language, theme preferences
- **Security Settings** - Manage 2FA methods, view security status

### 🌐 Multi-Language Support
- English and Polish fully supported
- Automatic locale detection from browser
- Manual language switching in settings
- All UI text, validation messages, and emails localized

### 🎨 Theming
- **Dark Mode** - Full dark theme support with system preference detection
- **Theme Persistence** - Settings saved per user account

---

## Gear Management Features

### 📦 Container System
- **Multiple Container Types** - Bug-out bags, EDC kits, get-home bags, medical kits, camping gear, and custom types
- **Hierarchical Organization** - Containers can contain other containers (nested packs, pouches in bags)
- **Visual Distinction** - Assign colors to containers for quick identification (10+ colors)
- **Container Metadata** - Type, description, base weight, color coding
- **Cycle Detection** - Prevents circular references in nested containers

### 🎒 Item Management
- **Rich Item Data**:
  - Basic: Name, quantity, weight (with unit selection: g, kg, oz, lb)
  - Organization: Category, priority, status (owned/missing/to buy)
  - Metadata: Brand, notes, expiration date
  - Advanced: Consumable flag, worn flag, custom categories
- **Smart Categorization** - Automatic category recognition based on item name (water, fire, food, shelter, first aid, tools, navigation, communication, clothing, hygiene, light, other)
- **Status Tracking** - Mark items as owned, missing, or to buy
- **Priority Levels** - Low, medium, high, critical
- **Expiration Tracking** - Monitor consumables and replace before they expire

### 📊 Analytics & Insights
- **Weight Calculations**:
  - Total pack weight with recursive calculation for nested containers
  - Category-based weight distribution
  - Base weight vs. consumables tracking
- **Readiness Indicators** - Kit completeness percentage based on owned vs. missing items
- **Donut Charts** - Visual breakdown of weight or quantity by category
- **Item Statistics** - Count items by status, category, or priority

### 🔍 Search & Filtering
- **Smart Search** - Find items by name, brand, or notes across all containers
- **Multi-Criteria Filtering** - Filter by category, status, priority, or container
- **Sorting Options** - Sort by name, weight, expiration date, or priority
- **Highlight Expired Items** - Visual warnings for expired or soon-to-expire items

### 🚀 Import/Export
- **JSON Export/Import** - Full data backup and restore
- **AI-Ready Markdown Export** - Export containers to markdown format for AI processing
  - Structured format with metadata (weight, brand, color, status)
  - Nested container support with calculated weights
  - Legend explaining data structure
  - One-click copy to clipboard
- **Cross-Device Transfer** - Export from one device, import on another

### ⚡ Productivity Features
- **Quick Item Entry** - Smart defaults and keyboard shortcuts
- **Inline Editing** - Edit items directly in lists (planned)
- **Drag & Drop Reordering** - Manual item ordering (planned)
- **Bulk Actions** - Mark multiple items as owned/missing (planned)
- **Templates** - Save and reuse common gear configurations (planned)

---

## Features

### ✅ Implemented Features

#### 🌐 Internationalization
- **Locale Detection** - Automatic language detection from browser settings with fallback to Polish
- Manual language switching in settings (English/Polish)
- HTML lang attribute automatically set based on detected language

#### 🎨 UI/UX
- **Category Icons** - Dedicated icons for each item category (water, fire, food, shelter, first aid, tools, navigation, communication, clothing, hygiene, light, other)
- **Container Colors** - Assign colors to containers for visual distinction (10 colors available)
- **Donut Chart Analytics** - Pie chart showing category distribution by weight or quantity in containers

#### 🔗 Container Nesting
- **Parent-Children Relationship** - Containers can contain other containers as items
- Hide nested containers from main container list
- Expandable rows in item tables to view nested container contents
- Recursive weight calculation (container + contents)
- Cycle detection to prevent infinite loops
- Separate "Add Item" and "Add Container" actions

#### ⚡ Quick Item Entry
- **Default Values** - New items have sensible defaults (0.1 kg weight, quantity 1, status "owned", priority "medium")
- **Category Recognition** - Automatic category detection based on item name keywords (supports English and Polish)
- Recognition triggered on blur event for immediate feedback

#### 🚀 Export Features
- **Export to AI Prompt** - Export container with all contents as markdown for AI processing
- Compact format with metadata (weight, brand, color, status, expiration)
- Support for nested containers with calculated weights
- Legend explaining data structure for AI
- One-click copy to clipboard

### 🔄 Planned Features

#### High Priority
- ✅ **All Items List Page** - Dedicated page showing all items from all containers with filtering and sorting
- ✅ **Shopping Planning Page** - Page for managing items to buy and expiring soon, with shopping list functionality
- ✅ **Container Cloning** - Duplicate containers with all items and nested containers
- ✅ **Add Existing Items** - Add items from other containers using catalog selector
- 🔄 **Inline Editing** - Quick edit items directly in the list without opening forms
- 🔄 **Item Ordering** - Manual drag & drop reordering of items within containers

#### Medium Priority
- ✅ **Preferred Weight Unit** - User setting to display all weights in grams or kilograms consistently
- ✅ **Extended Fields** - Additional fields for items (price, URL, quality tier, brand, color)
- ✅ **Extended Container Fields** - Brand and price fields for containers
- ✅ **Max Weight Limit** - Set maximum weight for containers with visual warnings
- ✅ **Parameter Recognition** - Automatic recognition of brand and color from item names
- ✅ **404 Page** - User-friendly not found page with navigation suggestions

#### Low Priority
- ⏸️ **Brand Color Selection** - Choose primary brand color (on hold - current color is satisfactory)
- ✅ **Footer & Legal Pages** - Cookie information, RODO compliance, privacy policy

### 🔮 Future Roadmap

**Frontend Features (see [ROADMAP.md](./docs/ROADMAP.md)):**
- Inline editing of items directly in lists
- Drag & drop item ordering
- Custom brand management
- Currency support
- Markdown support in notes
- Integrated weight input with unit picker

**Backend Features (see [ROADMAP_ONLINE.md](./docs/ROADMAP_ONLINE.md)):**
- ✅ User authentication (OAuth, 2FA, reCAPTCHA) - Completed
- Multi-device synchronization
- Container sharing between users
- Public container gallery
- Global item catalog
- Progressive Web App (PWA)
- AI-powered features
- Item photo uploads (requires S3 storage)

> 📋 **See also:**
> - [ROADMAP.md](./docs/ROADMAP.md) - 📍 Roadmap index (start here)
> - [ROADMAP_OFFLINE.md](./docs/ROADMAP_OFFLINE.md) - Offline features (localStorage)
> - [ROADMAP_ONLINE.md](./docs/ROADMAP_ONLINE.md) - Online features (backend/DB/auth)
> - [Features Documentation](./docs/features/) - Detailed implementation plans

---

## Development

### Prerequisites
- Node.js ^20.19.0 or >=22.12.0
- pnpm 10.18.3+
- Python 3.12+
- PostgreSQL 15+
- Docker & Docker Compose (for containerized development)

### Quick Start

**Frontend Development:**
```bash
pnpm install
pnpm dev              # Start dev server (http://localhost:5176)
pnpm build            # Build for production
pnpm type-check       # Run TypeScript checks
pnpm lint             # Run ESLint with auto-fix
```

**Backend Development:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
python cli.py db migrate  # Run database migrations
uvicorn app.main:app --reload
```

**Docker (Full Stack):**
```bash
docker-compose up -d
```

### Environment Variables

**Frontend (.env):**
```env
VITE_API_PROXY_URL=http://localhost:8000
VITE_GOOGLE_RECAPTCHA_SITE_KEY=your_recaptcha_site_key
VITE_GOOGLE_OAUTH_CLIENT_ID=your_google_oauth_client_id
```

**Backend (backend/.env):**
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/gearstack
JWT_SECRET_KEY=your-secret-key
RECAPTCHA_ENABLED=true
RECAPTCHA_SECRET_KEY=your_recaptcha_secret
GOOGLE_OAUTH_CLIENT_ID=your_oauth_client_id
GOOGLE_OAUTH_CLIENT_SECRET=your_oauth_client_secret
```

See `.env.example` and `backend/.env.example` for complete configuration options.

---

## Project Structure

```
gear-stack/
├── src/                      # Frontend source code
│   ├── modules/              # Feature modules
│   │   ├── auth/             # Authentication module
│   │   ├── gear/             # Gear management module
│   │   ├── settings/         # Settings module
│   │   └── user/             # User profile module
│   ├── components/           # Shared components
│   │   └── ui/               # shadcn-vue components
│   ├── layouts/              # Layout wrappers
│   ├── router/               # Vue Router config
│   ├── shared/               # Shared utilities
│   └── i18n/                 # Internationalization
├── backend/                  # Backend source code
│   ├── app/
│   │   ├── core/             # Core functionality (config, DB, email)
│   │   ├── modules/          # Feature modules
│   │   │   ├── auth/         # Auth module
│   │   │   └── two_factor/   # 2FA module
│   │   └── main.py           # FastAPI app entry
│   └── migrations/           # Database migrations
├── docs/                     # Documentation
│   ├── features/             # Feature implementation plans
│   ├── ROADMAP.md            # Roadmap index (entry point)
│   ├── ROADMAP_OFFLINE.md    # Offline features (localStorage)
│   └── ROADMAP_ONLINE.md     # Online features (backend/DB/auth)
└── docker-compose.yml        # Docker configuration
```

---

## Architecture

### Module-Based Frontend

Each feature is self-contained in `src/modules/`:
- `pages/` - Vue page components
- `components/` - Module-specific components
- `store/` - Pinia stores for state
- `services/` - Business logic layer
- `composables/` - Reusable composition functions
- `types/` - TypeScript definitions
- `routes.ts` - Module routes
- `i18n/` - Module translations

### Backend Modules

Backend follows FastAPI modular pattern:
- `router.py` - API endpoints with rate limiting
- `service.py` - Business logic
- `repositories.py` - Database access
- `models.py` - Domain models
- `schemas.py` - Request/response schemas
- `db_models.py` - SQLAlchemy models

### State Management Pattern

**Frontend:**
- Pinia stores handle state persistence
- Service classes contain business logic
- Stores expose simple CRUD + localStorage sync
- Services handle validation, calculations

**Backend:**
- Repository pattern for data access
- Service layer for business rules
- Clean separation of concerns

---

## Security Features

- ✅ **JWT Authentication** - Secure token-based auth with refresh tokens
- ✅ **Password Hashing** - bcrypt with configurable rounds
- ✅ **Rate Limiting** - Protection against brute force attacks
- ✅ **reCAPTCHA v3** - Bot protection (score-based, invisible)
- ✅ **OAuth 2.0** - CSRF protection via state parameter
- ✅ **Two-Factor Authentication** - TOTP and WebAuthn support
- ✅ **Email Verification** - Confirm user email addresses
- ✅ **CORS Configuration** - Secure cross-origin requests
- ✅ **SQL Injection Prevention** - Parameterized queries via SQLAlchemy
- ✅ **XSS Protection** - Input validation and sanitization

---

## Contributing

Contributions are welcome! Please read our contributing guidelines and code of conduct before submitting pull requests.

---

## License

[To be determined]

---

## Support

For issues, questions, or feature requests, please open an issue on GitHub.
