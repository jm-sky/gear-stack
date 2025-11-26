<script setup lang="ts">
import { ImageIcon, Trash2 } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { type RouteLocationRaw, RouterLink } from 'vue-router'
import { toast } from 'vue-sonner'
import DropdownMenu from '@/components/ui/dropdown-menu/DropdownMenu.vue'
import DropdownMenuContent from '@/components/ui/dropdown-menu/DropdownMenuContent.vue'
import DropdownMenuItem from '@/components/ui/dropdown-menu/DropdownMenuItem.vue'
import DropdownMenuTrigger from '@/components/ui/dropdown-menu/DropdownMenuTrigger.vue'
import { useAuth } from '@/modules/auth/composables/useAuth'
import { GearRoutePath } from '@/modules/gear/routes'
import { itemImageApiService } from '@/modules/gear/services/itemImageApiService'
import { useGearStore } from '@/modules/gear/store/useGearStore'
import { useHandleError } from '@/shared/composables/useHandleError'
import type { IItemImage } from '@/modules/gear/types/itemImage.types'

const props = defineProps<{
  itemId: string
  containerId?: string
  publicMode?: boolean
}>()

const { t } = useI18n()
const { handleError } = useHandleError()
const { user, isAuthenticated } = useAuth()
const store = useGearStore()

const image = ref<IItemImage | null>(null)
const isLoading = ref(false)
const hasError = ref(false)
const isUploading = ref(false)
const fileInput = ref<HTMLInputElement>()
const contextMenuOpen = ref(false)

// Get container to check ownership
const container = computed(() => {
  if (!props.containerId) return undefined
  return store.getContainerById(props.containerId)
})

// Check if user is admin
const isAdmin = computed(() => {
  return user.value?.isAdmin ?? false
})

// Check if user is owner of the container
const isOwner = computed(() => {
  if (!isAuthenticated.value || !user.value || !container.value) {
    return false
  }
  // For public containers, check authorId
  if (container.value.authorId) {
    return container.value.authorId === user.value.id
  }
  // For private containers (no authorId), if we can access the container,
  // it means we own it (backend handles authorization)
  // For localStorage, all containers are considered owned by current user
  return true
})

// Check if user can manage images (admin AND owner)
const canManageImages = computed(() => {
  return isAdmin.value && isOwner.value
})

async function loadPrimaryImage() {
  if (isLoading.value || (image.value && !hasError.value)) return

  try {
    isLoading.value = true
    hasError.value = false
    const images = await itemImageApiService.getImages(props.itemId)
    if (!images.length) {
      image.value = null
      return
    }

    const primary = images.find(img => img.isPrimary) ?? images[0]
    image.value = primary ?? null
  } catch (error: unknown) {
    console.error('Failed to load item image', error)
    hasError.value = true
    handleError(error)
  } finally {
    isLoading.value = false
  }
}

async function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  // Reset input
  if (fileInput.value) {
    fileInput.value.value = ''
  }

  await uploadImage(file)
}

async function uploadImage(file: File) {
  if (!canManageImages.value || isUploading.value) return

  try {
    isUploading.value = true
    const newImage = await itemImageApiService.uploadImage(props.itemId, file, true)
    image.value = newImage
    toast.success(t('gear.itemsTable.imageCell.uploadSuccess'))
  } catch (error: unknown) {
    console.error('Failed to upload image', error)
    handleError(error)
  } finally {
    isUploading.value = false
  }
}

function handleImageClick() {
  if (!canManageImages.value || image.value) return
  fileInput.value?.click()
}

async function handleDeleteImage() {
  if (!image.value || !canManageImages.value) return

  if (!confirm(t('gear.itemsTable.imageCell.confirmDelete'))) {
    return
  }

  try {
    await itemImageApiService.deleteImage(image.value.id)
    image.value = null
    toast.success(t('gear.itemsTable.imageCell.deleteSuccess'))
  } catch (error: unknown) {
    console.error('Failed to delete image', error)
    handleError(error)
  }
}

function handleContextMenu(event: MouseEvent) {
  if (!canManageImages.value || !image.value) return
  event.preventDefault()
  contextMenuOpen.value = true
}

const routeTo = computed<RouteLocationRaw | undefined>(() => {
  if (!image.value || !props.containerId) return undefined

  if (props.publicMode) {
    return GearRoutePath.PublicItemDetailById(props.containerId, props.itemId)
  }
  return {
      path: GearRoutePath.ItemDetailById(props.containerId, props.itemId),
      query: { from: 'container' },
    }
})

onMounted(() => {
  void loadPrimaryImage()
})
</script>

<template>
  <div class="flex items-center justify-center">
    <!-- Hidden file input -->
    <input
      v-if="canManageImages"
      ref="fileInput"
      type="file"
      accept="image/*"
      class="hidden"
      @change="handleFileSelect"
    />

    <!-- Loading skeleton -->
    <div
      v-if="isLoading"
      class="size-10 rounded-md bg-muted animate-pulse"
    />

    <!-- Image thumbnail with context menu -->
    <DropdownMenu v-else-if="image && !hasError" v-model:open="contextMenuOpen">
      <div
        class="-my-1 group block rounded-md overflow-hidden"
        @contextmenu="handleContextMenu"
      >
        <DropdownMenuTrigger as-child>
          <component
            :is="routeTo ? RouterLink : 'button'"
            :to="routeTo"
            class="block focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            <img
              :src="image.url"
              :alt="image.fileName"
              loading="lazy"
              class="size-12 rounded-md object-cover border border-border group-hover:border-primary/50 transition-colors"
            />
          </component>
        </DropdownMenuTrigger>
      </div>
      <DropdownMenuContent v-if="canManageImages">
        <DropdownMenuItem
          variant="destructive"
          @select="handleDeleteImage"
        >
          <Trash2 class="size-4" />
          {{ t('gear.itemsTable.imageCell.deleteImage') }}
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>

    <!-- No image - clickable if can manage -->
    <button
      v-else-if="canManageImages"
      type="button"
      class="flex items-center justify-center size-10 text-muted-foreground hover:text-foreground transition-colors cursor-pointer"
      @click="handleImageClick"
    >
      <ImageIcon class="size-4" />
    </button>

    <!-- No image - not clickable -->
    <span v-else class="flex items-center justify-center size-10 text-muted-foreground">
      <ImageIcon class="size-4" />
    </span>
  </div>
</template>


