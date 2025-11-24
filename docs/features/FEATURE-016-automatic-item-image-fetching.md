# FEATURE-016: Automatic Item Image Fetching

**Status:** 🔄 Planned
**Priority:** Medium
**Complexity:** Large
**Category:** 📷 Media & Resources
**Related Features:** FEATURE-013 (Item Descriptions), FEATURE-012 (Add Existing Items)
**Requires:** Backend/DB, Admin Access (isAdmin)

---

## 📋 Overview

Add automatic image fetching functionality for items. Users can search for item images from configured web sources (stores, APIs) when creating or editing items. This feature is **admin-only** and includes configurable image search engines with support for both HTML scraping and API-based sources.

---

## 🎯 Goals

1. **Image Search on Item Creation** - Option to search for images when creating new items
2. **On-Demand Image Search** - Action to search for images for existing items
3. **User Settings** - Default option to auto-search images for new items
4. **Admin-Only Access** - Feature available only for users with `isAdmin` flag
5. **Configurable Search Engines** - Support for multiple image sources (stores, APIs)
6. **Search Engine Configuration** - Server-side storage of search engine configs with relationship to items
7. **Image Selection** - UI to browse and select images from search results
8. **Caching** - Cache search results to reduce API calls

---

## 📐 Design

### Current State

- Items have no image field (or placeholder)
- No image search functionality
- No image source configuration
- No admin-only feature restrictions

### Proposed Changes

#### 1. Database Schema

**New Tables:**

```python
# Image Search Engine Configuration
class ImageSearchEngine(Base):
    __tablename__ = "image_search_engines"
    
    id: UUID
    name: str  # e.g., "Militaria.pl", "Allegro", "Google Images API"
    type: str  # "html_scraper" | "api"
    base_url: str  # e.g., "https://militaria.pl"
    search_template: str  # e.g., "/search?q={query}"
    image_selectors: JSON  # CSS selectors for HTML scraping
    api_endpoint: Optional[str]  # API endpoint if type is "api"
    api_key: Optional[str]  # API key if required
    is_active: bool
    priority: int  # Order of search engines
    created_at: datetime
    updated_at: datetime

# Item Images (relationship)
class ItemImage(Base):
    __tablename__ = "item_images"
    
    id: UUID
    item_id: UUID  # FK to items
    search_engine_id: UUID  # FK to image_search_engines
    image_url: str
    thumbnail_url: Optional[str]
    source_url: str  # Original product page URL
    is_primary: bool  # Primary image for item
    cached_at: datetime
    created_at: datetime

# Add to existing Item model
class Item(Base):
    # ... existing fields ...
    primary_image_id: Optional[UUID]  # FK to item_images
```

#### 2. User Settings

**Add to User Settings:**

```typescript
interface UserSettings {
  // ... existing settings ...
  autoSearchImagesForNewItems: boolean  // Default: false
}
```

#### 3. Frontend UI Components

**Item Form Page (`ItemFormPage.vue`):**

- Checkbox/toggle: "Wyszukaj obrazki w web" (only visible for admins)
- Button: "Wyszukaj obrazki" (triggers search)
- Image search results modal/dialog:
  - Grid of image thumbnails
  - Source indicator (which search engine found it)
  - Click to select image
  - Preview larger image on hover/click
  - "Use this image" button

**Item Actions (Existing Items):**

- Dropdown action: "Wyszukaj obrazki" (only visible for admins)
- Same image selection modal as above

**Settings Page:**

- Section: "Automatyczne wyszukiwanie obrazków" (only visible for admins)
- Checkbox: "Domyślnie wyszukaj obrazków dla nowych przedmiotów"
- Info text: "Funkcjonalność dostępna tylko dla administratorów"

**Admin Panel (Future):**

- Page: "Konfiguracja wyszukiwarek obrazków"
- List of configured search engines
- Add/Edit/Delete search engines
- Test search engine functionality

#### 4. Search Engine Configuration

**Configuration Structure:**

```typescript
interface ImageSearchEngineConfig {
  id: string
  name: string
  type: 'html_scraper' | 'api'
  baseUrl: string
  
  // For HTML Scrapers
  searchTemplate?: string  // e.g., "/search?q={query}"
  imageSelectors?: {
    container: string  // CSS selector for image container
    image: string  // CSS selector for img tag or data attribute
    thumbnail?: string  // Optional thumbnail selector
    link?: string  // Link to product page
  }
  
  // For API
  apiEndpoint?: string
  apiKey?: string
  requestHeaders?: Record<string, string>
  responseMapping?: {
    images: string  // JSON path to images array
    imageUrl: string  // JSON path to image URL
    thumbnailUrl?: string  // JSON path to thumbnail URL
    sourceUrl?: string  // JSON path to source URL
  }
  
  isActive: boolean
  priority: number
}
```

**Example Configurations:**

**1. HTML Scraper (Militaria.pl):**
```json
{
  "name": "Militaria.pl",
  "type": "html_scraper",
  "baseUrl": "https://militaria.pl",
  "searchTemplate": "/szukaj?fraza={query}",
  "imageSelectors": {
    "container": ".product-item",
    "image": "img.product-image",
    "link": "a.product-link"
  }
}
```

**2. HTML Scraper (Allegro):**
```json
{
  "name": "Allegro",
  "type": "html_scraper",
  "baseUrl": "https://allegro.pl",
  "searchTemplate": "/listing?string={query}",
  "imageSelectors": {
    "container": "article[data-role='offer']",
    "image": "img[data-src]",
    "thumbnail": "img[data-src]",
    "link": "a[data-role='offer-link']"
  }
}
```

**3. API (Google Images API):**
```json
{
  "name": "Google Images API",
  "type": "api",
  "baseUrl": "https://www.googleapis.com",
  "apiEndpoint": "/customsearch/v1",
  "apiKey": "${GOOGLE_API_KEY}",
  "responseMapping": {
    "images": "items",
    "imageUrl": "link",
    "thumbnailUrl": "image.thumbnailLink",
    "sourceUrl": "image.contextLink"
  }
}
```

#### 5. Search Query Building

**Query Construction:**

```typescript
interface SearchQuery {
  itemName: string
  brand?: string
  category?: string
  color?: string
}

function buildSearchQuery(item: IGearItem): string {
  const parts: string[] = []
  
  if (item.brand) {
    parts.push(item.brand)
  }
  
  parts.push(item.name)
  
  if (item.color) {
    parts.push(item.color)
  }
  
  return parts.join(' ')
}
```

---

## 🛠️ Implementation Plan

### Phase 1: Backend Infrastructure

**Files:**
- `backend/app/modules/gear/models/image_search.py` - Database models
- `backend/app/modules/gear/schemas/image_search.py` - Pydantic schemas
- `backend/app/modules/gear/repositories/image_search_repository.py` - Repository layer
- `backend/app/modules/gear/services/image_search_service.py` - Business logic
- `backend/app/modules/gear/routers/image_search.py` - API endpoints
- `backend/alembic/versions/XXXX_add_image_search_tables.py` - Database migration

**Changes:**
1. Create database models for `ImageSearchEngine` and `ItemImage`
2. Add `primary_image_id` field to `Item` model
3. Create Pydantic schemas for API requests/responses
4. Implement repository methods for CRUD operations
5. Create image search service with:
   - HTML scraping logic (using BeautifulSoup or similar)
   - API client logic
   - Query building
   - Image URL extraction
   - Caching mechanism
6. Create API endpoints:
   - `GET /api/image-search/engines` - List all search engines (admin only)
   - `POST /api/image-search/engines` - Create search engine (admin only)
   - `PUT /api/image-search/engines/{id}` - Update search engine (admin only)
   - `DELETE /api/image-search/engines/{id}` - Delete search engine (admin only)
   - `POST /api/image-search/search` - Search for images (admin only)
   - `POST /api/items/{item_id}/images` - Attach image to item (admin only)
   - `PUT /api/items/{item_id}/primary-image` - Set primary image (admin only)

### Phase 2: Frontend API Integration

**Files:**
- `src/modules/gear/services/imageSearchApiService.ts` - API service
- `src/modules/gear/composables/useImageSearch.ts` - Composable

**Changes:**
1. Create API service for image search endpoints
2. Create composable with:
   - `searchImages(query: string, engines?: string[])` - Search for images
   - `attachImageToItem(itemId: string, imageUrl: string, sourceUrl: string)` - Attach image
   - `setPrimaryImage(itemId: string, imageId: string)` - Set primary image
   - `getItemImages(itemId: string)` - Get item images
3. Add admin check utility (`useIsAdmin()` composable)

### Phase 3: Frontend UI - Item Form

**Files:**
- `src/modules/gear/pages/ItemFormPage.vue`
- `src/modules/gear/components/ImageSearchDialog.vue` - New component
- `src/modules/gear/components/ImageSearchResults.vue` - New component

**Changes:**
1. Add "Wyszukaj obrazki" button to item form (admin only)
2. Create `ImageSearchDialog` component:
   - Search input (pre-filled with item name + brand)
   - Loading state during search
   - `ImageSearchResults` component for displaying results
   - Image selection handler
3. Create `ImageSearchResults` component:
   - Grid layout for image thumbnails
   - Image preview on hover/click
   - Source indicator badge
   - "Select" button for each image
4. Handle image selection:
   - Call API to attach image to item
   - Update form state
   - Show success toast

### Phase 4: Frontend UI - Existing Items

**Files:**
- `src/modules/gear/components/ItemsTableRowActions.vue`
- `src/modules/gear/pages/ContainerDetailPage.vue`

**Changes:**
1. Add "Wyszukaj obrazki" action to item row actions dropdown (admin only)
2. Open same `ImageSearchDialog` with pre-filled query
3. Handle image selection and update item

### Phase 5: User Settings

**Files:**
- `src/modules/settings/pages/SettingsPage.vue`
- `src/modules/settings/store/useSettingsStore.ts`
- `src/modules/settings/types/settings.types.ts`

**Changes:**
1. Add `autoSearchImagesForNewItems` to settings type
2. Add settings section "Automatyczne wyszukiwanie obrazków" (admin only)
3. Add checkbox for default auto-search
4. Update item form to check this setting and auto-trigger search if enabled

### Phase 6: Image Display

**Files:**
- `src/modules/gear/components/ItemImage.vue` - New component
- `src/modules/gear/components/ItemsTable.vue`
- `src/modules/gear/components/ContainerCard.vue`

**Changes:**
1. Create `ItemImage` component for displaying item images
2. Add image column/display to items table
3. Add image display to container cards
4. Handle image loading errors (fallback to category icon)

### Phase 7: Admin Panel (Future)

**Files:**
- `src/modules/admin/pages/ImageSearchEnginesPage.vue` - New page
- `src/modules/admin/components/ImageSearchEngineForm.vue` - New component

**Changes:**
1. Create admin page for managing search engines
2. Create form for adding/editing search engines
3. List existing search engines with edit/delete actions
4. Test search engine functionality

---

## 📊 Data Flow

### Image Search Flow

```
User clicks "Wyszukaj obrazki" (admin only)
  ↓
Frontend builds search query (item name + brand + color)
  ↓
API call: POST /api/image-search/search
  {
    query: "Petzl Headlamp Black",
    engines: ["engine-1", "engine-2"] // Optional, or use all active
  }
  ↓
Backend service:
  - Iterates through active search engines (by priority)
  - For HTML scrapers: fetches HTML, parses with selectors
  - For API: makes API call with query
  - Extracts image URLs, thumbnails, source URLs
  - Caches results
  ↓
Returns array of image results:
  [
    {
      imageUrl: "https://...",
      thumbnailUrl: "https://...",
      sourceUrl: "https://...",
      searchEngine: "Militaria.pl"
    },
    ...
  ]
  ↓
Frontend displays results in ImageSearchDialog
  ↓
User selects image
  ↓
API call: POST /api/items/{itemId}/images
  {
    imageUrl: "...",
    sourceUrl: "...",
    searchEngineId: "..."
  }
  ↓
Backend creates ItemImage record
  ↓
Frontend updates UI to show selected image
```

### Auto-Search Flow (Settings Enabled)

```
User creates new item (admin only)
  ↓
Check user settings: autoSearchImagesForNewItems === true
  ↓
Auto-trigger image search after item name/brand entered
  ↓
Show ImageSearchDialog with results
  ↓
User can select image or dismiss
```

---

## 🔍 Technical Details

### HTML Scraping Implementation

**Backend Service:**

```python
async def scrape_html_images(
    engine: ImageSearchEngine,
    query: str
) -> List[ImageSearchResult]:
    """Scrape images from HTML source."""
    import httpx
    from bs4 import BeautifulSoup
    
    # Build search URL
    search_url = f"{engine.base_url}{engine.search_template.format(query=query)}"
    
    # Fetch HTML
    async with httpx.AsyncClient() as client:
        response = await client.get(search_url, timeout=10.0)
        response.raise_for_status()
        html = response.text
    
    # Parse HTML
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find image containers
    containers = soup.select(engine.image_selectors['container'])
    
    results = []
    for container in containers[:20]:  # Limit to 20 results
        img_tag = container.select_one(engine.image_selectors['image'])
        if not img_tag:
            continue
        
        image_url = img_tag.get('src') or img_tag.get('data-src')
        if not image_url:
            continue
        
        # Make absolute URL
        if image_url.startswith('/'):
            image_url = f"{engine.base_url}{image_url}"
        
        # Get source URL
        link_tag = container.select_one(engine.image_selectors.get('link', 'a'))
        source_url = link_tag.get('href') if link_tag else None
        
        results.append(ImageSearchResult(
            image_url=image_url,
            thumbnail_url=image_url,  # Use same URL if no thumbnail selector
            source_url=source_url or search_url,
            search_engine_id=engine.id
        ))
    
    return results
```

### API-Based Search Implementation

**Backend Service:**

```python
async def search_api_images(
    engine: ImageSearchEngine,
    query: str
) -> List[ImageSearchResult]:
    """Search images via API."""
    import httpx
    
    # Build API request
    url = f"{engine.base_url}{engine.api_endpoint}"
    params = {
        'q': query,
        'key': engine.api_key,
        # ... other API-specific params
    }
    
    headers = engine.request_headers or {}
    
    # Make API call
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, headers=headers, timeout=10.0)
        response.raise_for_status()
        data = response.json()
    
    # Extract images using response mapping
    images = get_nested_value(data, engine.response_mapping['images'])
    
    results = []
    for img_data in images[:20]:  # Limit to 20 results
        image_url = get_nested_value(img_data, engine.response_mapping['imageUrl'])
        thumbnail_url = get_nested_value(
            img_data, 
            engine.response_mapping.get('thumbnailUrl', 'imageUrl')
        )
        source_url = get_nested_value(
            img_data,
            engine.response_mapping.get('sourceUrl', 'link')
        )
        
        results.append(ImageSearchResult(
            image_url=image_url,
            thumbnail_url=thumbnail_url,
            source_url=source_url,
            search_engine_id=engine.id
        ))
    
    return results
```

### Caching Strategy

**Cache Key:**
```
image_search:{engine_id}:{query_hash}
```

**Cache Duration:**
- 24 hours for successful searches
- 1 hour for failed searches (to avoid repeated failures)

**Cache Storage:**
- Redis (if available) or in-memory cache
- Store: `List[ImageSearchResult]`

### Admin Check

**Backend Middleware/Decorator:**

```python
from functools import wraps
from fastapi import HTTPException, status

def admin_required(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        current_user = kwargs.get('current_user')
        if not current_user or not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This feature is available only for administrators"
            )
        return await func(*args, **kwargs)
    return wrapper
```

**Frontend Composable:**

```typescript
export function useIsAdmin() {
  const userStore = useUserStore()
  
  const isAdmin = computed(() => {
    return userStore.user?.isAdmin === true
  })
  
  return { isAdmin }
}
```

---

## 🧪 Testing

### Manual Test Cases

1. **Admin Access Check**
   - ✅ Non-admin users don't see "Wyszukaj obrazki" button
   - ✅ Non-admin users get 403 error if they try to call API directly
   - ✅ Admin users see button and can use feature

2. **Image Search on Item Creation**
   - ✅ Admin creates new item
   - ✅ Clicks "Wyszukaj obrazki" button
   - ✅ Dialog opens with search results
   - ✅ Can select image
   - ✅ Image is attached to item

3. **Image Search for Existing Item**
   - ✅ Admin opens existing item
   - ✅ Clicks "Wyszukaj obrazki" from actions menu
   - ✅ Dialog opens with search results
   - ✅ Can select image
   - ✅ Image is attached to item

4. **Auto-Search Setting**
   - ✅ Admin enables "Domyślnie wyszukaj obrazków dla nowych przedmiotów"
   - ✅ Creates new item
   - ✅ Search dialog auto-opens after entering name/brand
   - ✅ Non-admin setting has no effect

5. **Multiple Search Engines**
   - ✅ Multiple engines configured
   - ✅ Search queries all active engines
   - ✅ Results show source engine
   - ✅ Results are combined and deduplicated

6. **HTML Scraper**
   - ✅ Configure HTML scraper for test site
   - ✅ Search returns images from HTML
   - ✅ Image URLs are absolute
   - ✅ Source URLs are correct

7. **API Scraper**
   - ✅ Configure API scraper (e.g., Google Images)
   - ✅ Search returns images from API
   - ✅ Response mapping works correctly

8. **Image Display**
   - ✅ Selected images display in items table
   - ✅ Images display in container cards
   - ✅ Fallback to category icon if image fails to load

9. **Caching**
   - ✅ Same query returns cached results
   - ✅ Cache expires after 24 hours
   - ✅ Failed searches cached for 1 hour

### Unit Tests

1. **Backend:**
   - `test_image_search_service.py` - Test HTML scraping, API calls, query building
   - `test_image_search_repository.py` - Test CRUD operations
   - `test_image_search_router.py` - Test API endpoints, admin checks

2. **Frontend:**
   - `imageSearchApiService.spec.ts` - Test API service methods
   - `useImageSearch.spec.ts` - Test composable logic
   - `ImageSearchDialog.spec.ts` - Test component rendering and interactions

---

## 📦 Release

**Version:** TBD
**Release Date:** TBD
**Branch:** develop → main

### CHANGELOG Entry

```
### Added
- Automatic image search for items (admin-only feature)
- Image search on item creation and for existing items
- User setting: "Domyślnie wyszukaj obrazków dla nowych przedmiotów" (admin only)
- Configurable image search engines (HTML scrapers and API-based)
- Image selection UI with preview
- Image display in items table and container cards
- Caching for search results (24h for success, 1h for failures)

### Changed
- Item model now supports primary image
- Admin-only access control for image search features

### Database
- New table: `image_search_engines` - Configuration for search engines
- New table: `item_images` - Relationship between items and images
- Added `primary_image_id` field to `items` table
```

---

## 🚀 Future Enhancements

### Image Upload
- Allow users to upload their own images (requires S3 storage)
- Combine uploaded images with searched images

### Image Optimization
- Automatic image resizing and compression
- WebP conversion
- CDN integration

### Advanced Search
- Search by image (reverse image search)
- AI-powered image matching
- Image quality scoring

### Search Engine Management UI
- Admin panel for managing search engines
- Test search engine functionality
- Analytics for search engine performance

### Multi-Image Support
- Support for multiple images per item (gallery)
- Image reordering
- Image deletion

---

## 📝 Notes

- **Admin-Only Feature**: This feature is restricted to administrators only. Non-admin users will not see any UI elements related to image search.
- **Search Engine Configuration**: Initially, search engines will be configured via database migrations or admin API. Future enhancement will add admin UI for managing engines.
- **HTML Scraping Limitations**: HTML scraping may break if websites change their structure. API-based sources are more reliable but require API keys.
- **Rate Limiting**: Consider implementing rate limiting for search requests to avoid overwhelming external APIs.
- **Legal Considerations**: Ensure compliance with website terms of service when scraping HTML. Prefer API-based sources when available.
- **Image Storage**: Initially, images are stored as URLs (external links). Future enhancement may include downloading and storing images locally (requires S3).
- **Caching**: Cache is important to reduce API calls and improve performance. Consider Redis for production.
- **Error Handling**: Gracefully handle failures (network errors, parsing errors, API errors) and show user-friendly messages.

---

## 🔗 Related Documentation

- [ROADMAP_ONLINE.md](../ROADMAP_ONLINE.md) - Online/backend features roadmap
- [FEATURE-012](./FEATURE-012-add-existing-items.md) - Add existing items (similar UI patterns)
- [FEATURE-013](./FEATURE-013-item-descriptions.md) - Item descriptions (form enhancements)
- Backend auth module: `backend/app/modules/auth/`
- Frontend auth module: `src/modules/auth/`
