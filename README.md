# gear-stack
A lightweight front-end application for managing survival gear and bug-out bag equipment.

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
