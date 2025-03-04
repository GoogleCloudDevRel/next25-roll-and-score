import { readonly, nextTick, triggerRef } from 'vue'
import { RouteManager } from './RouteManager'

// Create a singleton instance at module level
const instance = new RouteManager()

// Refs for managing route components at module level
instance._activeRoutes = null
instance._activeRoutesRef = null
instance._nextIndex = 0
instance._prevIndex = null

export function useRouteManager() {
  // Enhanced navigation with automatic state updates and error handling
  const navigateTo = async (routeId, data) => {
    console.log(instance.currentRoute.value, instance.isTransitioning.value);
    if(instance.isTransitioning.value) return;
    if(instance.currentRoute.value?.id === routeId) return;

    if (!routeId) throw new Error('Route ID is required')
    try {

      instance._nextIndex = instance._activeRoutes.value.length
      instance._prevIndex = instance._nextIndex - 1
      instance._prevIndex = instance._prevIndex < 0 ? null : instance._prevIndex

      await instance.navigateTo(routeId, data)
    } catch (error) {
      console.error('Navigation failed:', error)
      throw error
    }
  }

  // Register route with lifecycle management
  const registerRoute = (id, config) => {
    if (!id) throw new Error('Route ID is required')
    if (!config) throw new Error('Route config is required')
    instance.registerRoute(id, config)
  }

  const registerRoutes = (routes, activeRoutes, activeRoutesRef) => {
    if (!routes || typeof routes !== 'object' || !activeRoutesRef) {
      throw new Error('Routes must be a valid object')
    }

    // Store refs at module level
    instance._activeRoutes = activeRoutes
    instance._activeRoutesRef = activeRoutesRef

    Object.keys(routes).forEach(
      (routeId) => registerRoute(routeId, {
        beforeAll: async (to, from) => {
          const nextRef = instance._activeRoutesRef.value[instance._nextIndex]
          if (nextRef) {
            return await nextRef.beforeAll?.(to, from)
          }
        },
        onEnter: async (to, from) => {
          // Set next component
          instance._activeRoutes.value.push(routes[routeId])
          triggerRef(instance._activeRoutes)

          // Wait for component to mount and get ref
          await nextTick()

          const nextRef = instance._activeRoutesRef.value[instance._nextIndex]

          if (nextRef) {
            // Set initial state
            await nextRef.animateSet?.(to, from)
            // Run enter animation
            await nextRef.animateIn?.(to, from)
            // Start static animation
            nextRef.animateIdle?.(to, from)
          }
        },
        onExit: async (to, from) => {
          const prevRef = instance._activeRoutesRef.value[instance._prevIndex];
          if (prevRef) {
            await nextTick()
            // Run exit animation
            await prevRef.animateOut?.(to, from)
          }
        },
        afterAll: async () => {
          // Update state and clear previous route refs after transition
          const prevRef = instance._activeRoutes.value[instance._prevIndex]

          if(prevRef) {
            instance._activeRoutes.value.shift()
            instance._activeRoutesRef.value.shift()
            triggerRef(instance._activeRoutes)
            triggerRef(instance._activeRoutesRef)
          }
        }
      }))
  }

  const onRouteChange = (handler) => {
    if (typeof handler !== 'function') {
      throw new Error('Route change handler must be a function')
    }
    instance.customRouteChange = handler
  }

  return {
    currentRoute: readonly(instance.currentRoute),
    previousRoute: readonly(instance.previousRoute),
    isTransitioning: readonly(instance.isTransitioning),
    isLanding: readonly(instance.isLanding),
    registerRoutes,
    navigateTo,
    onRouteChange
  }
}
