import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { GearRoutePath } from '../routes'
import { createNavigationQuery, getFrom, getReturnTo } from '../utils/navigationParams'

export function useNavigationReturn(containerId: string, itemId?: string) {
  const route = useRoute()
  const router = useRouter()

  const returnTo = computed(() => getReturnTo(route))
  const from = computed(() => getFrom(route))

  function navigateBack() {
    const returnToValue = returnTo.value
    const fromValue = from.value

    if (returnToValue === 'detail' && itemId) {
      router.push({
        path: GearRoutePath.ItemDetailById(containerId, itemId),
        query: createNavigationQuery(undefined, fromValue),
      })
    } else if (returnToValue === 'shopping') {
      router.push(GearRoutePath.ShoppingPlanning)
    } else {
      router.push(GearRoutePath.ContainerDetailById(containerId))
    }
  }

  function navigateBackAndClean() {
    navigateBack()
    // Clean query params from URL after navigation
    router.replace({ query: {} })
  }

  return {
    returnTo,
    from,
    navigateBack,
    navigateBackAndClean,
  }
}

