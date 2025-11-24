<script setup lang="ts">
import { Users, Package, PackageCheck } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { apiClient } from '@/shared/services/apiClient'
import { config } from '@/shared/config/config'
import { useGearStore } from '@/modules/gear/store/useGearStore'
import { useAuthStore } from '@/modules/auth/store/useAuthStore'

const { t } = useI18n()
const gearStore = useGearStore()
const authStore = useAuthStore()

// Stats state
const totalUsers = ref(0)
const newUsersThisMonth = ref(0)
const loading = ref(true)

// Calculate current month start date
const getCurrentMonthStart = (): Date => {
  const now = new Date()
  return new Date(now.getFullYear(), now.getMonth(), 1)
}

// Check if date is within current month
const isThisMonth = (dateString: string): boolean => {
  const date = new Date(dateString)
  const monthStart = getCurrentMonthStart()
  return date >= monthStart
}

// Calculate containers stats
const containersStats = computed(() => {
  const containers = gearStore.getAllContainers
  const total = containers.length
  const newThisMonth = containers.filter(c => isThisMonth(c.createdAt)).length
  return { total, newThisMonth }
})

// Calculate items stats
const itemsStats = computed(() => {
  const containers = gearStore.getAllContainers
  const allItems = containers.flatMap(c => c.items)
  const total = allItems.length
  const newThisMonth = allItems.filter(item => isThisMonth(item.createdAt)).length
  return { total, newThisMonth }
})

// Fetch user stats from API if backend is enabled
const fetchUserStats = async () => {
  if (!config.backend.enabled) {
    loading.value = false
    return
  }

  try {
    // Try to fetch stats from API (if endpoint exists)
    // For now, we'll set to 0 if endpoint doesn't exist
    const response = await apiClient.get<{
      total: number
      newThisMonth: number
    }>('/stats/users').catch(() => null)

    if (response?.data) {
      totalUsers.value = response.data.total
      newUsersThisMonth.value = response.data.newThisMonth
    }
  } catch (error) {
    // Endpoint might not exist, that's okay
    console.debug('Stats endpoint not available:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  // Load containers from storage if not authenticated
  if (!authStore.isAuthenticated) {
    gearStore.loadFromStorage()
  }
  fetchUserStats()
})
</script>

<template>
  <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
    <!-- Total Users -->
    <div class="bg-card/50 backdrop-blur-sm rounded-lg border p-6 text-center">
      <div class="flex justify-center mb-3">
        <div class="rounded-full bg-primary/10 p-3">
          <Users class="size-6 text-primary" />
        </div>
      </div>
      <div class="text-3xl font-bold text-primary mb-1">
        {{ loading ? '...' : totalUsers.toLocaleString() }}
      </div>
      <div class="text-sm text-muted-foreground mb-2">
        {{ t('landing.stats.totalUsers', 'Total Users') }}
      </div>
      <div v-if="!loading && newUsersThisMonth > 0" class="text-xs text-muted-foreground">
        +{{ newUsersThisMonth }} {{ t('landing.stats.newThisMonth', 'this month') }}
      </div>
    </div>

    <!-- Total Containers -->
    <div class="bg-card/50 backdrop-blur-sm rounded-lg border p-6 text-center">
      <div class="flex justify-center mb-3">
        <div class="rounded-full bg-primary/10 p-3">
          <Package class="size-6 text-primary" />
        </div>
      </div>
      <div class="text-3xl font-bold text-primary mb-1">
        {{ containersStats.total.toLocaleString() }}
      </div>
      <div class="text-sm text-muted-foreground mb-2">
        {{ t('landing.stats.totalContainers', 'Total Containers') }}
      </div>
      <div v-if="containersStats.newThisMonth > 0" class="text-xs text-muted-foreground">
        +{{ containersStats.newThisMonth }} {{ t('landing.stats.newThisMonth', 'this month') }}
      </div>
    </div>

    <!-- Total Items -->
    <div class="bg-card/50 backdrop-blur-sm rounded-lg border p-6 text-center">
      <div class="flex justify-center mb-3">
        <div class="rounded-full bg-primary/10 p-3">
          <PackageCheck class="size-6 text-primary" />
        </div>
      </div>
      <div class="text-3xl font-bold text-primary mb-1">
        {{ itemsStats.total.toLocaleString() }}
      </div>
      <div class="text-sm text-muted-foreground mb-2">
        {{ t('landing.stats.totalItems', 'Total Items') }}
      </div>
      <div v-if="itemsStats.newThisMonth > 0" class="text-xs text-muted-foreground">
        +{{ itemsStats.newThisMonth }} {{ t('landing.stats.newThisMonth', 'this month') }}
      </div>
    </div>
  </div>
</template>
