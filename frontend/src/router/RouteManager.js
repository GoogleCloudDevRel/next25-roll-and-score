/**
 * @typedef {Object} RouteConfig
 * @property {Function} onEnter - Entry animation handler
 * @property {Function} onExit - Exit animation handler
 * @property {Function} afterAll - Static state animation handler
 */

import { ref } from "vue"

/**
 * @typedef {Object} RouteState
 * @property {string} id - Unique route identifier
 * @property {any} data - Route-specific data
 * @property {RouteConfig} config - Route animation configuration
 */

export class RouteManager {
  constructor() {
    /** @type {Map<string, RouteConfig>} */
    this.routes = new Map()
    /** @type {{ value: RouteState|null}} */
    this.currentRoute = ref(null)
    /** @type {{value: RouteState|null}} */
    this.previousRoute = ref(null)
    /** @type {{value: boolean}} */
    this.isTransitioning = ref(false)
    /** @type {{value: boolean}} */
    this.isLanding = ref(true)
    /** @type {(to: RouteState, from: RouteState, data: RouteState.data) => Promise<void>} */
    this.customRouteChange = null
  }

  /**
   * Register a new route with its animation configuration
   * @param {string} id - Unique route identifier
   * @param {RouteConfig} config - Route animation configuration
   */
  registerRoute(id, config) {
    // Ensure all handlers are functions, use no-op if not provided
    this.routes.set(id, {
      beforeAll: config.beforeAll || (() => Promise.resolve()),
      onEnter: config.onEnter || (() => Promise.resolve()),
      onExit: config.onExit || (() => Promise.resolve()),
      afterAll: config.afterAll || (() => { })
    })
  }

  async onRouteChange(to, from) {
    // Execute beforeAll hook if we have a current route (useful for FLIP animations)
    const beforeAllRes = await from?.config.beforeAll(to, from)
    to.data = { ...to.data, ...(beforeAllRes || {}) }

    // Execute exit and enter animations in parallel
    await Promise.all([
      // Exit animation (if we have a current route)
      from ? from.config.onExit(to, from) : Promise.resolve(),
      // Enter animation
      to.config.onEnter(to, from)
    ])

    // Execute static animation if defined
    if (to.config.afterAll) {
      to.config.afterAll(to, from)
    }
  }

  /**
   * Navigate to a new route
   * @param {string} id - Target route identifier
   * @param {any} data - Route-specific data to pass
   * @returns {Promise<void>}
   */
  async navigateTo(id, data = {}) {
    // Validate navigation request
    if (this.isTransitioning.value || !this.routes.has(id)) {
      return
    }

    // Start transition
    this.isTransitioning.value = true
    const fromRoute = this.currentRoute.value
    this.previousRoute.value = fromRoute
    const toConfig = this.routes.get(id)
    const toRoute = { id, data, config: toConfig }
    // Update current route immediately so both components can be mounted
    this.currentRoute.value = toRoute

    try {
      await this.customRouteChange?.(toRoute, fromRoute)
      await this.onRouteChange(toRoute, fromRoute)
    } catch (error) {
      console.error('Route transition failed:', error)
      throw error
    } finally {
      this.isTransitioning.value = false
      this.isLanding.value = false
    }
  }

  /**
   * Get previous route state
   * @returns {RouteState|null}
   */
  getPreviousRoute() {
    return this.previousRoute
  }

  /**
   * Get current route state
   * @returns {RouteState|null}
   */
  getCurrentRoute() {
    return this.currentRoute
  }

  /**
   * Check if currently transitioning between routes
   * @returns {boolean}
   */
  getIsTransitioning() {
    return this.isTransitioning
  }

  /**
   * Clear all animations and reset state
   */
  destroy() {
    this.routes.clear()
    this.currentRoute.value = null
    this.isTransitioning.value = false
  }
}

