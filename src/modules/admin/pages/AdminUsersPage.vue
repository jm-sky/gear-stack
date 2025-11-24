<script setup lang="ts">
import { MoreHorizontal, Shield, ShieldOff, Trash2, Users } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import DataTable from '@/components/data-table/DataTable.vue'
import Badge from '@/components/ui/badge/Badge.vue'
import Button from '@/components/ui/button/Button.vue'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import TableEmptyDecorated from '@/components/ui/table/TableEmptyDecorated.vue'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import type { IAdminUser } from '../types/admin.types'
import { adminApiService } from '../services/adminApiService'
import type { ColumnDef } from '@tanstack/vue-table'

const { t } = useI18n()
const users = ref<IAdminUser[]>([])
const loading = ref(false)

// Load users
async function loadUsers() {
  loading.value = true
  try {
    users.value = await adminApiService.getUsers(0, 1000)
  } catch (error) {
    console.error('Failed to load users:', error)
    toast.error(t('admin.users.loadError', 'Failed to load users'))
  } finally {
    loading.value = false
  }
}

// Toggle admin status
async function toggleAdmin(user: IAdminUser) {
  const newRole = user.isAdmin ? 'user' : 'admin'
  const action = user.isAdmin
    ? t('admin.users.toggleAdmin.demote', 'remove admin privileges')
    : t('admin.users.toggleAdmin.promote', 'grant admin privileges')

  if (!confirm(t('admin.users.toggleAdmin.confirm', 'Are you sure you want to {action}?', { action }))) {
    return
  }

  try {
    await adminApiService.updateUser(user.id, { role: newRole })
    toast.success(
      user.isAdmin
        ? t('admin.users.toggleAdmin.demoteSuccess', 'User demoted from administrator')
        : t('admin.users.toggleAdmin.promoteSuccess', 'User promoted to administrator'),
    )
    await loadUsers()
  } catch (error) {
    console.error('Failed to toggle admin status:', error)
    toast.error(t('admin.users.toggleAdmin.error', 'Failed to update user admin status'))
  }
}

// Delete user
async function deleteUser(userId: string) {
  if (!confirm(t('admin.users.deleteConfirm', 'Are you sure you want to delete this user?'))) {
    return
  }

  try {
    await adminApiService.deleteUser(userId)
    toast.success(t('admin.users.deleteSuccess', 'User deleted successfully'))
    await loadUsers()
  } catch (error) {
    console.error('Failed to delete user:', error)
    toast.error(t('admin.users.deleteError', 'Failed to delete user'))
  }
}

// Columns
const columns = computed<ColumnDef<IAdminUser>[]>(() => [
  {
    id: 'name',
    accessorKey: 'name',
    header: () => t('admin.users.columns.name', 'Name'),
    enableSorting: true,
  },
  {
    id: 'email',
    accessorKey: 'email',
    header: () => t('admin.users.columns.email', 'Email'),
    enableSorting: true,
  },
  {
    id: 'isAdmin',
    accessorKey: 'isAdmin',
    header: () => t('admin.users.columns.isAdmin', 'Admin'),
    enableSorting: true,
  },
  {
    id: 'isActive',
    accessorKey: 'isActive',
    header: () => t('admin.users.columns.isActive', 'Active'),
    enableSorting: true,
  },
  {
    id: 'isEmailVerified',
    accessorKey: 'isEmailVerified',
    header: () => t('admin.users.columns.isEmailVerified', 'Verified'),
    enableSorting: true,
  },
  {
    id: 'createdAt',
    accessorKey: 'createdAt',
    header: () => t('admin.users.columns.createdAt', 'Created'),
    enableSorting: true,
  },
  {
    id: 'actions',
    header: () => t('admin.users.columns.actions', 'Actions'),
    enableSorting: false,
  },
])

// Global filter function
const globalFilterFn = (row: IAdminUser, filterValue: string) => {
  const query = filterValue.toLowerCase()
  return (
    row.name.toLowerCase().includes(query) ||
    row.email.toLowerCase().includes(query)
  )
}

onMounted(() => {
  loadUsers()
})
</script>

<template>
  <AuthenticatedLayout>
    <div class="space-y-6 w-full max-w-full overflow-hidden">
      <!-- Header -->
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold tracking-tight flex items-center gap-3">
            <Users class="size-8 text-primary" />
            {{ t('admin.users.title', 'Users Management') }}
          </h1>
          <p class="text-muted-foreground mt-2">
            {{ t('admin.users.subtitle', 'Manage user accounts and permissions') }}
          </p>
        </div>
      </div>

      <!-- Table -->
      <DataTable
        :columns="columns"
        :data="users"
        :search-placeholder="t('admin.users.search', 'Search users...')"
        :global-filter-fn="globalFilterFn"
        :enable-sorting="true"
        :enable-filtering="true"
        :enable-pagination="true"
        :initial-page-size="20"
      >
        <template #name="{ row }">
          <div class="flex items-center gap-2">
            <div
              v-if="row.original.avatarUrl"
              class="size-8 rounded-full bg-cover bg-center"
              :style="{ backgroundImage: `url(${row.original.avatarUrl})` }"
            />
            <div
              v-else
              class="size-8 rounded-full bg-primary/10 flex items-center justify-center text-primary font-semibold text-sm"
            >
              {{ row.original.name.charAt(0).toUpperCase() }}
            </div>
            <span class="font-medium">{{ row.original.name }}</span>
          </div>
        </template>

        <template #email="{ row }">
          <span class="text-muted-foreground">{{ row.original.email }}</span>
        </template>

        <template #isAdmin="{ row }">
          <Badge v-if="row.original.isAdmin" variant="default">
            {{ t('admin.users.admin', 'Admin') }}
          </Badge>
          <span v-else class="text-muted-foreground">-</span>
        </template>

        <template #isActive="{ row }">
          <Badge v-if="row.original.isActive" variant="default">
            {{ t('admin.users.active', 'Active') }}
          </Badge>
          <Badge v-else variant="secondary">
            {{ t('admin.users.inactive', 'Inactive') }}
          </Badge>
        </template>

        <template #isEmailVerified="{ row }">
          <Badge v-if="row.original.isEmailVerified" variant="default">
            {{ t('admin.users.verified', 'Verified') }}
          </Badge>
          <Badge v-else variant="destructive">
            {{ t('admin.users.unverified', 'Unverified') }}
          </Badge>
        </template>

        <template #createdAt="{ row }">
          <span class="text-sm text-muted-foreground">
            {{ new Date(row.original.createdAt).toLocaleDateString() }}
          </span>
        </template>

        <template #actions="{ row }">
          <DropdownMenu>
            <DropdownMenuTrigger as-child>
              <Button variant="ghost" size="sm">
                <MoreHorizontal class="size-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem @click="toggleAdmin(row.original)">
                <Shield v-if="!row.original.isAdmin" class="size-4" />
                <ShieldOff v-else class="size-4" />
                <span>
                  {{
                    row.original.isAdmin
                      ? t('admin.users.toggleAdmin.demote', 'Remove Admin')
                      : t('admin.users.toggleAdmin.promote', 'Make Admin')
                  }}
                </span>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                class="text-destructive focus:text-destructive"
                @click="deleteUser(row.original.id)"
              >
                <Trash2 class="size-4" />
                <span>{{ t('admin.users.delete', 'Delete') }}</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </template>

        <template #empty>
          <TableEmptyDecorated
            :colspan="columns.length"
            :title="t('admin.users.empty', 'No users found')"
            :description="t('admin.users.emptyDescription', 'No users match your search criteria.')"
          />
        </template>
      </DataTable>
    </div>
  </AuthenticatedLayout>
</template>
