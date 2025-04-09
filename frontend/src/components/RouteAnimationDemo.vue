<template>
  <nav class="controls">
    <button
      v-for="(_, routeId) in routes"
      :key="routeId"
      @click="navigateTo(routeId)"
      :disabled="isTransitioning"
      :class="{ active: currentRoute?.id === routeId }"
    >
      {{ routeId.charAt(0).toUpperCase() + routeId.slice(1) }}
    </button>
  </nav>

  <div class="routes">
    <component
      v-for="route in activeRoutes"
      :is="route"
      ref="activeRoutesRef"
      :key="route.__name"
    />
  </div>
</template>

<script setup>
import { shallowRef, onMounted } from 'vue'
import { useRouteManager } from '../router/useRouteManager'
import HomeRoute from '../routes/HomeRoute.vue'
import HomeDetailRoute from '../routes/HomeDetailRoute.vue'
import AboutRoute from '../routes/AboutRoute.vue'
import ContactRoute from '../routes/ContactRoute.vue'

const activeRoutes = shallowRef([])
const activeRoutesRef = shallowRef([])

const routes = {
  home: HomeRoute,
  about: AboutRoute,
  contact: ContactRoute,
  homedetail: HomeDetailRoute,
}

const {
  currentRoute,
  isTransitioning,
  registerRoutes,
  navigateTo,
  // Optional: Use this to customize how routes change behave
  // onRouteChange,
} = useRouteManager()

// Register routes with their animations
onMounted(() => {
  registerRoutes(routes, activeRoutes, activeRoutesRef)

  // Initialize with home route
  navigateTo('home')
})
</script>

<style lang="scss" scoped>
.controls {
  position: absolute;
  display: flex;
  gap: 1rem;
  justify-content: center;
  top: 1rem;
  z-index: 999;

  button {
    padding: 0.8rem 1.5rem;
    border: 2px solid #42b883;
    border-radius: 4px;
    background: transparent;
    color: #42b883;
    font-weight: bold;
    cursor: pointer;
    transition: all 0.3s;

    &.active {
      background: #42b883;
      color: white;
    }

    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    &:hover:not(:disabled) {
      background: #42b883;
      color: white;
    }
  }
}

.routes {
  position: relative;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}
</style>
