# Plan Implementacji: Ocenianie (gwiazdki) kontenerów

## 📋 Przegląd

Plan implementacji systemu oceniania kontenerów (rating system) zgodnie z wymaganiami z ROADMAP_ONLINE.md. System umożliwia:
- **Owner rating**: Właściciel kontenera może ocenić swój kontener (1-5 gwiazdek)
- **User rating**: Inni użytkownicy mogą ocenić publiczne kontenery (1-5 gwiazdek)

## 🎯 Cele

1. **Backend**: Tabela `container_ratings` z rozróżnieniem typu oceny (`rating_type: 'owner' | 'user'`)
2. **Backend**: Endpointy API do dodawania/aktualizacji/usuwania oceny
3. **Backend**: Obliczanie średniej oceny per kontener
4. **Frontend**: Komponent gwiazdek do oceniania (w szczegółach kontenera)
5. **Frontend**: Wyświetlanie średniej oceny w galerii i szczegółach kontenera
6. **Frontend**: Rozróżnienie między owner rating a user rating w UI
7. **Frontend**: Możliwość zmiany własnej oceny

## 🔍 Analiza Obecnego Stanu

### Backend

**Istniejące modele:**
- `GearContainerDB` w `backend/app/modules/gear/db_models.py`
- Brak tabeli `container_ratings`
- Brak pola `author_rating` w `GearContainerDB` (w przeciwieństwie do FEATURE-023, tutaj używamy tylko ratingów w osobnej tabeli)

**Istniejące endpointy:**
- `GET /gear/containers/{id}` - pobieranie kontenera
- `GET /gear/public/containers` - pobieranie publicznych kontenerów
- `GET /gear/public/containers/{id}` - pobieranie publicznego kontenera

**Brakujące:**
- Tabela `container_ratings`
- Endpointy do zarządzania ocenami
- Logika obliczania średniej oceny

### Frontend

**Istniejące komponenty:**
- `PublicContainerDetailPage.vue` - strona szczegółów publicznego kontenera
- `ContainerDetailPage.vue` - strona szczegółów własnego kontenera
- `PublicContainersBrowserPage.vue` - przeglądarka publicznych kontenerów
- `PublicContainerCard.vue` - karta kontenera w galerii

**Brakujące:**
- Komponent gwiazdek do oceniania (`RatingStars.vue` lub `ContainerRating.vue`)
- Wyświetlanie średniej oceny w kartach i szczegółach
- UI do oceniania przez właściciela i użytkowników

## 📝 Plan Implementacji

### Faza 1: Backend - Model Danych i Migracja

#### Step 1.1: Utworzenie modelu `ContainerRatingDB`

**File:** `backend/app/modules/gear/db_models.py`

Dodaj nowy model:

```python
class ContainerRatingDB(Base):
    """SQLAlchemy model for container ratings.
    
    Supports two types of ratings:
    - 'owner': Rating given by container owner
    - 'user': Rating given by other users (for public containers)
    
    Attributes:
        id: Unique identifier (ULID format, 36 chars)
        container_id: Rated container ID
        user_id: User who gave the rating
        rating: Rating value (1-5)
        rating_type: Type of rating ('owner' or 'user')
        created_at: Rating timestamp
        updated_at: Last update timestamp
    """
    
    __tablename__ = "container_ratings"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    container_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("gear_containers.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5
    rating_type: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="user"
    )  # 'owner' or 'user'
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False
    )
    
    # Relationships
    container: Mapped["GearContainerDB"] = relationship(
        "GearContainerDB",
        back_populates="ratings"
    )
    user: Mapped["UserDB"] = relationship("UserDB", foreign_keys=[user_id])
    
    # Unique constraint: one rating per user per container per type
    __table_args__ = (
        UniqueConstraint(
            'container_id',
            'user_id',
            'rating_type',
            name='uq_container_rating_user_type'
        ),
    )
```

Dodaj relację do `GearContainerDB`:

```python
# W GearContainerDB
ratings: Mapped[list["ContainerRatingDB"]] = relationship(
    "ContainerRatingDB",
    back_populates="container",
    cascade="all, delete-orphan"
)
```

#### Step 1.2: Utworzenie migracji

**File:** `backend/migrations/versions/XXX_add_container_ratings.py`

```python
"""Add container_ratings table

Revision ID: XXX
Revises: YYY
Create Date: 2025-XX-XX XX:XX:XX.XXXXXX
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'XXX'
down_revision = 'YYY'
branch_labels = None
depends_on = None

def upgrade():
    # Create container_ratings table
    op.create_table(
        'container_ratings',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('container_id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('rating_type', sa.String(10), nullable=False, server_default='user'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ['container_id'],
            ['gear_containers.id'],
            ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['users.id'],
            ondelete='CASCADE'
        ),
        sa.UniqueConstraint(
            'container_id',
            'user_id',
            'rating_type',
            name='uq_container_rating_user_type'
        )
    )
    op.create_index(
        op.f('ix_container_ratings_container_id'),
        'container_ratings',
        ['container_id']
    )
    op.create_index(
        op.f('ix_container_ratings_user_id'),
        'container_ratings',
        ['user_id']
    )
    op.create_index(
        'ix_container_ratings_rating_type',
        'container_ratings',
        ['rating_type']
    )

def downgrade():
    op.drop_table('container_ratings')
```

---

### Faza 2: Backend - Schemas i Walidacja

#### Step 2.1: Dodanie schemas dla ratingów

**File:** `backend/app/modules/gear/schemas.py`

Dodaj nowe schemas:

```python
# Rating type enum
RatingType = Literal["owner", "user"]

class ContainerRatingCreate(BaseModel):
    """Schema for creating/updating container rating."""
    
    rating: int = Field(..., ge=1, le=5, description="Rating value from 1 to 5")
    rating_type: RatingType = Field(
        default="user",
        description="Type of rating: 'owner' for owner rating, 'user' for user rating"
    )
    
    model_config = {"populate_by_name": True}


class ContainerRatingResponse(BaseModel):
    """Schema for container rating response."""
    
    id: str
    container_id: str = Field(alias="containerId")
    user_id: str = Field(alias="userId")
    rating: int
    rating_type: RatingType = Field(alias="ratingType")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    
    model_config = {"from_attributes": True, "populate_by_name": True}
```

#### Step 2.2: Aktualizacja `ContainerResponse`

**File:** `backend/app/modules/gear/schemas.py`

Dodaj pola ratingów do `ContainerResponse`:

```python
class ContainerResponse(BaseModel):
    """Schema for gear container response."""
    
    # ... istniejące pola ...
    
    # Rating fields
    owner_rating: int | None = Field(None, alias="ownerRating")  # Owner's rating (1-5)
    user_rating: int | None = Field(None, alias="userRating")  # Current user's rating (if logged in)
    average_user_rating: float | None = Field(None, alias="averageUserRating")  # Average of all user ratings
    user_rating_count: int = Field(default=0, alias="userRatingCount")  # Number of user ratings
    
    model_config = {"from_attributes": True, "populate_by_name": True}
```

---

### Faza 3: Backend - Repository i Service

#### Step 3.1: Dodanie metod do repository

**File:** `backend/app/modules/gear/repository.py`

Dodaj metody do `GearRepository`:

```python
async def get_container_rating(
    self,
    container_id: str,
    user_id: str,
    rating_type: str = "user"
) -> ContainerRatingDB | None:
    """Get user's rating for a container by type."""
    result = await self.db.execute(
        select(ContainerRatingDB)
        .where(ContainerRatingDB.container_id == container_id)
        .where(ContainerRatingDB.user_id == user_id)
        .where(ContainerRatingDB.rating_type == rating_type)
    )
    return result.scalar_one_or_none()

async def upsert_container_rating(
    self,
    container_id: str,
    user_id: str,
    rating: int,
    rating_type: str = "user"
) -> ContainerRatingDB:
    """Create or update user's rating for a container."""
    existing = await self.get_container_rating(container_id, user_id, rating_type)
    
    if existing:
        existing.rating = rating
        existing.updated_at = datetime.now(UTC)
        await self.db.flush()
        return existing
    
    new_rating = ContainerRatingDB(
        id=generate_id(),
        container_id=container_id,
        user_id=user_id,
        rating=rating,
        rating_type=rating_type,
    )
    self.db.add(new_rating)
    await self.db.flush()
    return new_rating

async def delete_container_rating(
    self,
    container_id: str,
    user_id: str,
    rating_type: str = "user"
) -> bool:
    """Delete user's rating for a container."""
    rating = await self.get_container_rating(container_id, user_id, rating_type)
    if rating:
        await self.db.delete(rating)
        await self.db.flush()
        return True
    return False

async def get_container_average_user_rating(
    self,
    container_id: str
) -> float | None:
    """Calculate average user rating for a container (excluding owner ratings)."""
    result = await self.db.execute(
        select(func.avg(ContainerRatingDB.rating))
        .where(ContainerRatingDB.container_id == container_id)
        .where(ContainerRatingDB.rating_type == "user")
    )
    avg = result.scalar()
    return float(avg) if avg is not None else None

async def get_container_user_rating_count(
    self,
    container_id: str
) -> int:
    """Get number of user ratings for a container (excluding owner ratings)."""
    result = await self.db.execute(
        select(func.count(ContainerRatingDB.id))
        .where(ContainerRatingDB.container_id == container_id)
        .where(ContainerRatingDB.rating_type == "user")
    )
    return result.scalar() or 0

async def get_container_owner_rating(
    self,
    container_id: str
) -> int | None:
    """Get owner's rating for a container."""
    result = await self.db.execute(
        select(ContainerRatingDB.rating)
        .where(ContainerRatingDB.container_id == container_id)
        .where(ContainerRatingDB.rating_type == "owner")
        .limit(1)
    )
    rating = result.scalar_one_or_none()
    return rating if rating else None
```

#### Step 3.2: Aktualizacja metody `get_container` i `get_public_container`

**File:** `backend/app/modules/gear/repository.py`

Zaktualizuj metody, aby uwzględniały ratingi:

```python
async def get_container(
    self,
    container_id: str,
    user_id: str
) -> GearContainerDB | None:
    """Get container with ratings if user_id provided."""
    container = await self.db.get(GearContainerDB, container_id)
    if not container:
        return None
    
    # Load owner rating
    owner_rating = await self.get_container_owner_rating(container_id)
    
    # Load user rating (if current user is not owner)
    user_rating = None
    if container.user_id != user_id:
        user_rating_obj = await self.get_container_rating(
            container_id,
            user_id,
            rating_type="user"
        )
        user_rating = user_rating_obj.rating if user_rating_obj else None
    
    # Calculate average user rating
    avg_user_rating = await self.get_container_average_user_rating(container_id)
    user_rating_count = await self.get_container_user_rating_count(container_id)
    
    # Attach as attributes (will be serialized in response)
    container._owner_rating = owner_rating
    container._user_rating = user_rating
    container._average_user_rating = avg_user_rating
    container._user_rating_count = user_rating_count
    
    return container

async def get_public_container(
    self,
    container_id: str
) -> GearContainerDB | None:
    """Get public container with ratings."""
    container = await self.get_public_container_base(container_id)  # Existing method
    if not container:
        return None
    
    # Load owner rating
    owner_rating = await self.get_container_owner_rating(container_id)
    
    # Calculate average user rating
    avg_user_rating = await self.get_container_average_user_rating(container_id)
    user_rating_count = await self.get_container_user_rating_count(container_id)
    
    # Attach as attributes
    container._owner_rating = owner_rating
    container._average_user_rating = avg_user_rating
    container._user_rating_count = user_rating_count
    
    return container
```

#### Step 3.3: Aktualizacja service

**File:** `backend/app/modules/gear/service.py`

Zaktualizuj metodę `_map_container_to_response`:

```python
async def _map_container_to_response(
    self,
    container: GearContainerDB
) -> ContainerResponse:
    """Map container DB model to response schema."""
    # ... istniejące mapowanie ...
    
    # Map rating fields
    owner_rating = getattr(container, '_owner_rating', None)
    user_rating = getattr(container, '_user_rating', None)
    average_user_rating = getattr(container, '_average_user_rating', None)
    user_rating_count = getattr(container, '_user_rating_count', 0)
    
    return ContainerResponse(
        # ... istniejące pola ...
        ownerRating=owner_rating,
        userRating=user_rating,
        averageUserRating=float(average_user_rating) if average_user_rating else None,
        userRatingCount=user_rating_count,
    )
```

---

### Faza 4: Backend - API Endpoints

#### Step 4.1: Dodanie endpointów dla ratingów

**File:** `backend/app/modules/gear/router.py`

Dodaj nowe endpointy:

```python
@router.post(
    "/containers/{container_id}/rating",
    response_model=dict,
    summary="Rate a container"
)
async def rate_container(
    container_id: str,
    rating_data: ContainerRatingCreate,
    current_user: CurrentUser,
    service: GearServiceDep,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Rate a container (create or update rating).
    
    Supports two rating types:
    - 'owner': Rating by container owner (only if current_user is owner)
    - 'user': Rating by other users (only for public containers)
    """
    repository = GearRepository(db)
    
    # Verify container exists
    container = await repository.get_container(container_id, current_user.id)
    if not container:
        # Try public container
        container = await repository.get_public_container(container_id)
        if not container:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Container not found"
            )
    
    # Validate rating type
    is_owner = container.user_id == current_user.id
    
    if rating_data.rating_type == "owner" and not is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only container owner can set owner rating"
        )
    
    if rating_data.rating_type == "user" and is_owner:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Container owner should use 'owner' rating type"
        )
    
    if rating_data.rating_type == "user" and not container.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ratings are only allowed for public containers"
        )
    
    # Upsert rating
    rating = await repository.upsert_container_rating(
        container_id=container_id,
        user_id=current_user.id,
        rating=rating_data.rating,
        rating_type=rating_data.rating_type
    )
    await db.commit()
    
    # Get updated stats
    if rating_data.rating_type == "owner":
        owner_rating = rating.rating
        avg_user_rating = await repository.get_container_average_user_rating(container_id)
        user_rating_count = await repository.get_container_user_rating_count(container_id)
    else:
        owner_rating = await repository.get_container_owner_rating(container_id)
        avg_user_rating = await repository.get_container_average_user_rating(container_id)
        user_rating_count = await repository.get_container_user_rating_count(container_id)
    
    return {
        "rating": rating.rating,
        "ratingType": rating.rating_type,
        "ownerRating": owner_rating,
        "averageUserRating": float(avg_user_rating) if avg_user_rating else None,
        "userRatingCount": user_rating_count
    }


@router.delete(
    "/containers/{container_id}/rating",
    summary="Delete container rating"
)
async def delete_container_rating(
    container_id: str,
    rating_type: str = Query(
        default="user",
        description="Type of rating to delete: 'owner' or 'user'"
    ),
    current_user: CurrentUser = Depends(get_current_user),
    service: GearServiceDep = Depends(get_gear_service),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Delete user's rating for a container."""
    repository = GearRepository(db)
    
    # Verify container exists
    container = await repository.get_container(container_id, current_user.id)
    if not container:
        container = await repository.get_public_container(container_id)
        if not container:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Container not found"
            )
    
    # Validate rating type
    is_owner = container.user_id == current_user.id
    
    if rating_type == "owner" and not is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only container owner can delete owner rating"
        )
    
    # Delete rating
    deleted = await repository.delete_container_rating(
        container_id,
        current_user.id,
        rating_type
    )
    await db.commit()
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rating not found"
        )
    
    # Get updated stats
    owner_rating = await repository.get_container_owner_rating(container_id)
    avg_user_rating = await repository.get_container_average_user_rating(container_id)
    user_rating_count = await repository.get_container_user_rating_count(container_id)
    
    return {
        "message": "Rating deleted",
        "ownerRating": owner_rating,
        "averageUserRating": float(avg_user_rating) if avg_user_rating else None,
        "userRatingCount": user_rating_count
    }
```

---

### Faza 5: Frontend - Typy i Interfejsy

#### Step 5.1: Aktualizacja typów

**File:** `src/modules/gear/types/gear.types.ts`

Dodaj typy i zaktualizuj interfejsy:

```typescript
// Rating type (1-5)
export type TRatingValue = 1 | 2 | 3 | 4 | 5

// Rating type enum
export type TRatingType = 'owner' | 'user'

// Zaktualizuj IGearContainer
export interface IGearContainer {
  // ... istniejące pola ...
  
  // Rating fields
  ownerRating?: TRatingValue | null  // Owner's rating (1-5)
  userRating?: TRatingValue | null  // Current user's rating (if logged in)
  averageUserRating?: number | null  // Average of all user ratings
  userRatingCount?: number  // Number of user ratings
}
```

---

### Faza 6: Frontend - Komponenty UI

#### Step 6.1: Utworzenie komponentu `RatingStars.vue`

**File:** `src/modules/gear/components/RatingStars.vue`

Komponent do wyświetlania i oceniania (gwiazdki):

```vue
<script setup lang="ts">
import { computed } from 'vue'
import { Star } from 'lucide-vue-next'
import type { TRatingValue } from '../types/gear.types'

interface Props {
  rating?: TRatingValue | number | null
  maxRating?: number
  size?: 'sm' | 'md' | 'lg'
  interactive?: boolean
  showNumber?: boolean
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  maxRating: 5,
  size: 'md',
  interactive: false,
  showNumber: false,
  disabled: false
})

const emit = defineEmits<{
  'update:rating': [value: TRatingValue | null]
  'change': [value: TRatingValue | null]
}>()

const hoveredRating = ref<number | null>(null)

const displayRating = computed(() => {
  if (hoveredRating.value !== null) {
    return hoveredRating.value
  }
  if (props.rating == null) return null
  return Math.round(props.rating)
})

const starSize = computed(() => {
  switch (props.size) {
    case 'sm': return 'size-4'
    case 'md': return 'size-5'
    case 'lg': return 'size-6'
    default: return 'size-5'
  }
})

function handleStarClick(rating: number) {
  if (props.disabled || !props.interactive) return
  
  const newRating = rating === props.rating ? null : (rating as TRatingValue)
  emit('update:rating', newRating)
  emit('change', newRating)
}

function handleStarHover(rating: number) {
  if (props.disabled || !props.interactive) return
  hoveredRating.value = rating
}

function handleStarLeave() {
  if (props.disabled || !props.interactive) return
  hoveredRating.value = null
}
</script>

<template>
  <div class="flex items-center gap-1">
    <div class="flex gap-0.5">
      <button
        v-for="star in maxRating"
        :key="star"
        type="button"
        :class="[
          'transition-colors',
          starSize,
          interactive && !disabled ? 'cursor-pointer hover:scale-110' : 'cursor-default',
          disabled ? 'opacity-50' : ''
        ]"
        :disabled="disabled || !interactive"
        @click="handleStarClick(star)"
        @mouseenter="handleStarHover(star)"
        @mouseleave="handleStarLeave"
      >
        <Star
          :class="[
            'transition-colors',
            star <= (displayRating ?? 0)
              ? 'fill-yellow-400 text-yellow-400'
              : 'fill-gray-200 text-gray-300'
          ]"
        />
      </button>
    </div>
    <span
      v-if="showNumber && rating != null"
      class="text-sm font-medium text-gray-700 dark:text-gray-300 ml-1"
    >
      {{ rating.toFixed(1) }}
    </span>
  </div>
</template>
```

#### Step 6.2: Utworzenie komponentu `ContainerRatingCard.vue`

**File:** `src/modules/gear/components/ContainerRatingCard.vue`

Komponent do wyświetlania i zarządzania ocenami kontenera:

```vue
<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { RatingStars } from './RatingStars'
import { Button } from '@/components/ui/button'
import type { IGearContainer, TRatingValue, TRatingType } from '../types/gear.types'

interface Props {
  container: IGearContainer
  isOwner?: boolean
  isPublic?: boolean
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isOwner: false,
  isPublic: false,
  loading: false
})

const emit = defineEmits<{
  'rate': [rating: TRatingValue, type: TRatingType]
  'delete-rating': [type: TRatingType]
}>()

const { t } = useI18n()

const ownerRating = computed(() => props.container.ownerRating)
const userRating = computed(() => props.container.userRating)
const averageUserRating = computed(() => props.container.averageUserRating)
const userRatingCount = computed(() => props.container.userRatingCount ?? 0)

function handleOwnerRatingChange(rating: TRatingValue | null) {
  if (rating === null) {
    emit('delete-rating', 'owner')
  } else {
    emit('rate', rating, 'owner')
  }
}

function handleUserRatingChange(rating: TRatingValue | null) {
  if (rating === null) {
    emit('delete-rating', 'user')
  } else {
    emit('rate', rating, 'user')
  }
}
</script>

<template>
  <div class="space-y-4">
    <!-- Owner Rating Section -->
    <div v-if="isOwner" class="space-y-2">
      <div class="flex items-center justify-between">
        <label class="text-sm font-medium">
          {{ t('gear.container.ownerRating') }}
        </label>
      </div>
      <RatingStars
        :rating="ownerRating"
        :interactive="true"
        :disabled="loading"
        @update:rating="handleOwnerRatingChange"
      />
      <p class="text-xs text-gray-500">
        {{ t('gear.container.ownerRatingDescription') }}
      </p>
    </div>

    <!-- User Rating Section -->
    <div v-if="isPublic && !isOwner" class="space-y-2">
      <div class="flex items-center justify-between">
        <label class="text-sm font-medium">
          {{ t('gear.container.yourRating') }}
        </label>
      </div>
      <RatingStars
        :rating="userRating"
        :interactive="true"
        :disabled="loading"
        @update:rating="handleUserRatingChange"
      />
    </div>

    <!-- Average User Rating Display -->
    <div v-if="isPublic && userRatingCount > 0" class="space-y-2">
      <div class="flex items-center justify-between">
        <label class="text-sm font-medium">
          {{ t('gear.container.averageUserRating') }}
        </label>
        <span class="text-sm text-gray-500">
          ({{ userRatingCount }} {{ t('gear.container.ratings') }})
        </span>
      </div>
      <RatingStars
        :rating="averageUserRating"
        :show-number="true"
        :interactive="false"
      />
    </div>
  </div>
</template>
```

#### Step 6.3: Aktualizacja `ContainerDetailPage.vue`

**File:** `src/modules/gear/pages/ContainerDetailPage.vue`

Dodaj sekcję z ocenami:

```vue
<script setup lang="ts">
// ... istniejący kod ...

import { ContainerRatingCard } from '../components/ContainerRatingCard'
import { useGearStore } from '../store'
import { useAuthStore } from '@/modules/auth/store'

const gearStore = useGearStore()
const authStore = useAuthStore()

const isOwner = computed(() => {
  return container.value?.userId === authStore.user?.id
})

const isPublic = computed(() => {
  return container.value?.isPublic ?? false
})

async function handleRate(rating: TRatingValue, type: TRatingType) {
  if (!container.value) return
  
  try {
    await gearContainerApiService.rateContainer(
      container.value.id,
      rating,
      type
    )
    // Refresh container data
    await loadContainer()
  } catch (error) {
    // Handle error
  }
}

async function handleDeleteRating(type: TRatingType) {
  if (!container.value) return
  
  try {
    await gearContainerApiService.deleteContainerRating(
      container.value.id,
      type
    )
    // Refresh container data
    await loadContainer()
  } catch (error) {
    // Handle error
  }
}
</script>

<template>
  <div>
    <!-- ... istniejący kod ... -->
    
    <!-- Rating Section -->
    <Card v-if="container" class="mt-6">
      <CardHeader>
        <CardTitle>{{ t('gear.container.ratings') }}</CardTitle>
      </CardHeader>
      <CardContent>
        <ContainerRatingCard
          :container="container"
          :is-owner="isOwner"
          :is-public="isPublic"
          @rate="handleRate"
          @delete-rating="handleDeleteRating"
        />
      </CardContent>
    </Card>
  </div>
</template>
```

#### Step 6.4: Aktualizacja `PublicContainerDetailPage.vue`

**File:** `src/modules/gear/pages/PublicContainerDetailPage.vue`

Podobne zmiany jak w `ContainerDetailPage.vue`, ale z uwzględnieniem, że użytkownik może ocenić tylko jako "user" (nie jako owner).

#### Step 6.5: Aktualizacja `PublicContainerCard.vue`

**File:** `src/modules/gear/components/PublicContainerCard.vue`

Dodaj wyświetlanie średniej oceny w karcie:

```vue
<template>
  <Card>
    <!-- ... istniejący kod ... -->
    
    <!-- Rating Display -->
    <div v-if="container.averageUserRating != null" class="flex items-center gap-2 mt-2">
      <RatingStars
        :rating="container.averageUserRating"
        :show-number="true"
        size="sm"
        :interactive="false"
      />
      <span class="text-xs text-gray-500">
        ({{ container.userRatingCount }})
      </span>
    </div>
  </Card>
</template>
```

---

### Faza 7: Frontend - Services i API

#### Step 7.1: Dodanie metod API

**File:** `src/modules/gear/services/gearContainerApiService.ts`

Dodaj metody:

```typescript
async rateContainer(
  containerId: string,
  rating: TRatingValue,
  ratingType: TRatingType = 'user'
): Promise<{
  rating: TRatingValue
  ratingType: TRatingType
  ownerRating: TRatingValue | null
  averageUserRating: number | null
  userRatingCount: number
}> {
  const response = await apiClient.post(
    `/gear/containers/${containerId}/rating`,
    {
      rating,
      ratingType
    }
  )
  return response.data
}

async deleteContainerRating(
  containerId: string,
  ratingType: TRatingType = 'user'
): Promise<{
  message: string
  ownerRating: TRatingValue | null
  averageUserRating: number | null
  userRatingCount: number
}> {
  const response = await apiClient.delete(
    `/gear/containers/${containerId}/rating`,
    {
      params: { rating_type: ratingType }
    }
  )
  return response.data
}
```

---

### Faza 8: Frontend - i18n

#### Step 8.1: Dodanie tłumaczeń

**File:** `src/modules/gear/i18n/index.ts`

Dodaj tłumaczenia:

```typescript
// PL
container: {
  // ... istniejące ...
  ratings: 'Oceny',
  ownerRating: 'Twoja ocena (jako właściciel)',
  ownerRatingDescription: 'Oceń swój kontener od 1 do 5 gwiazdek',
  yourRating: 'Twoja ocena',
  averageUserRating: 'Średnia ocena użytkowników',
  ratings: 'ocen',
  rateContainer: 'Oceń kontener',
  deleteRating: 'Usuń ocenę',
}

// EN
container: {
  // ... existing ...
  ratings: 'Ratings',
  ownerRating: 'Your Rating (as owner)',
  ownerRatingDescription: 'Rate your container from 1 to 5 stars',
  yourRating: 'Your Rating',
  averageUserRating: 'Average User Rating',
  ratings: 'ratings',
  rateContainer: 'Rate Container',
  deleteRating: 'Delete Rating',
}
```

---

## 📁 Pliki do Modyfikacji

### Backend

- `backend/app/modules/gear/db_models.py` - Model `ContainerRatingDB`, relacja w `GearContainerDB`
- `backend/app/modules/gear/schemas.py` - Schemas dla ratingów, aktualizacja `ContainerResponse`
- `backend/app/modules/gear/repository.py` - Metody dla ratingów, aktualizacja `get_container` i `get_public_container`
- `backend/app/modules/gear/service.py` - Aktualizacja `_map_container_to_response`
- `backend/app/modules/gear/router.py` - Endpointy POST/DELETE dla ratingów
- `backend/migrations/versions/XXX_add_container_ratings.py` - Migracja bazy danych

### Frontend

- `src/modules/gear/types/gear.types.ts` - Typy `TRatingValue`, `TRatingType`, aktualizacja `IGearContainer`
- `src/modules/gear/components/RatingStars.vue` - **NOWY** - Komponent gwiazdek
- `src/modules/gear/components/ContainerRatingCard.vue` - **NOWY** - Komponent zarządzania ocenami
- `src/modules/gear/pages/ContainerDetailPage.vue` - Dodanie sekcji z ocenami
- `src/modules/gear/pages/PublicContainerDetailPage.vue` - Dodanie sekcji z ocenami
- `src/modules/gear/components/PublicContainerCard.vue` - Wyświetlanie średniej oceny
- `src/modules/gear/services/gearContainerApiService.ts` - Metody API dla ratingów
- `src/modules/gear/i18n/index.ts` - Tłumaczenia

---

## ✅ Kryteria Akceptacji

### Backend

- [ ] Tabela `container_ratings` utworzona z odpowiednimi constraintami
- [ ] Unique constraint zapobiega duplikatom ratingów (jeden użytkownik = jedna ocena per typ)
- [ ] Endpoint POST `/gear/containers/{id}/rating` działa poprawnie
- [ ] Endpoint DELETE `/gear/containers/{id}/rating` działa poprawnie
- [ ] Walidacja ratingów (1-5) działa poprawnie
- [ ] Walidacja typu oceny (owner/user) działa poprawnie
- [ ] Endpointy GET kontenerów zwracają `ownerRating`, `userRating`, `averageUserRating`, `userRatingCount`
- [ ] Obliczanie średniej oceny użytkowników działa poprawnie (wyklucza owner ratings)
- [ ] Owner może ocenić tylko jako "owner", inni użytkownicy tylko jako "user"
- [ ] User ratings są dozwolone tylko dla publicznych kontenerów

### Frontend

- [ ] Komponent `RatingStars` wyświetla oceny poprawnie (gwiazdki)
- [ ] Komponent `RatingStars` pozwala na interaktywne ocenianie (hover, click)
- [ ] Komponent `ContainerRatingCard` wyświetla owner rating (dla właściciela)
- [ ] Komponent `ContainerRatingCard` wyświetla user rating (dla innych użytkowników)
- [ ] Komponent `ContainerRatingCard` wyświetla średnią ocenę użytkowników z liczbą ocen
- [ ] Strona szczegółów kontenera (`ContainerDetailPage`) wyświetla sekcję z ocenami
- [ ] Strona szczegółów publicznego kontenera (`PublicContainerDetailPage`) wyświetla sekcję z ocenami
- [ ] Karty kontenerów w galerii (`PublicContainerCard`) wyświetlają średnią ocenę
- [ ] Właściciel może ocenić swój kontener jako "owner"
- [ ] Inni użytkownicy mogą ocenić publiczne kontenery jako "user"
- [ ] Użytkownicy mogą zmienić swoją ocenę
- [ ] Użytkownicy mogą usunąć swoją ocenę
- [ ] Tłumaczenia zaktualizowane (PL/EN)

### Testing

- [ ] Testy jednostkowe dla repository methods (ratingi)
- [ ] Testy integracyjne dla endpointów ratingów
- [ ] Testy E2E dla oceniania kontenerów
- [ ] Testy walidacji (rating 1-5, typ owner/user)
- [ ] Testy uprawnień (owner vs user, public vs private)

---

## 🔗 Powiązane Funkcjonalności

- **Public containers** - Ratingi są szczególnie przydatne dla publicznych kontenerów
- **User profiles** - Możliwość wyświetlania średnich ocen użytkownika w przyszłości
- **FEATURE-023** - Ogólny system ocen (dla przedmiotów i kontenerów) - ten plan skupia się tylko na kontenerach

---

## 📝 Uwagi

- **Rating scale:** 1-5 (gwiazdki)
- **Owner rating:** Tylko właściciel kontenera może ustawić ocenę typu "owner"
- **User ratings:** Każdy użytkownik może ocenić publiczny kontener raz jako "user" (upsert)
- **Public visibility:** User ratings widoczne tylko dla publicznych kontenerów
- **Unique constraint:** Jeden użytkownik może mieć jedną ocenę typu "owner" i jedną typu "user" per kontener
- **Average calculation:** Średnia ocena użytkowników wyklucza owner ratings

---

## 🚀 Przyszłe Rozszerzenia

- Komentarze do ocen (opcjonalne)
- Filtrowanie/sortowanie kontenerów po ocenach w galerii
- Statystyki ocen w profilu użytkownika
- Powiadomienia o nowych ocenach
- Historia zmian ocen
- Weryfikacja ocen (tylko użytkownicy, którzy skopiowali kontener mogą ocenić)

