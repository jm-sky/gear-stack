# gear-stack
A lightweight front-end application for managing survival gear and bug-out bag equipment.

<img width="1527" height="547" alt="obraz" src="https://github.com/user-attachments/assets/9e71110e-0941-418b-b853-2cd9fe43aa91" />

## Product Requirements (Draft)

### Overview
A lightweight front-end application for managing survival gear and bug-out bag equipment. The app runs fully client-side using `localStorage` for persistence. Users can organize items, track completeness of their kits, and monitor consumables such as food or medical supplies.

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

### Data Persistence
- All data saved in `localStorage`.
- Import / export of full dataset as JSON.

---

### Technical Stack
- Vue 3.5+ with TypeScript
- Pinia for state management
- Vue Router for multi-view navigation
- TailwindCSS + Shadcn-Vue for UI

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
- **All Items List Page** - Dedicated page showing all items from all containers with filtering and sorting
- **Inline Editing** - Quick edit items directly in the list without opening forms
- **Item Ordering** - Manual drag & drop reordering of items within containers

#### Medium Priority
- **Preferred Weight Unit** - User setting to display all weights in grams or kilograms consistently
- **Extended Fields** - Additional fields for items (price, URL, quality tier, brand, color)
- **Extended Container Fields** - Brand and price fields for containers

#### Low Priority
- **Brand Color Selection** - Choose primary brand color (coyote, olive, or other survival/outdoor themes)
- **Footer & Legal Pages** - Cookie information, RODO compliance, privacy policy

### 🔮 Future Considerations
- Cloud synchronization between devices
- Data versioning (change history)
- Statistics and reports
- Container templates (predefined sets)
- Container sharing between users
- Progressive Web App (PWA) for mobile

> 📋 **See also:** [ROADMAP](./docs/ROADMAP.md) for detailed feature implementation plans
