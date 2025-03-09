<template>
  <BackgroundBase
    :dpr="1.5"
    v-slot="{ oglState }"
  >
    <BackgroundRings :oglState="oglState" />
  </BackgroundBase>
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
import BackgroundBase from '@/components/background/BackgroundBase.vue'
import BackgroundRings from '@/components/background/BackgroundRings.vue'
import RollAndScoreHighlights from '@/components/RollAndScoreHighlights.vue'
import RollAndScoreIntro from '@/components/RollAndScoreIntro.vue'
import { useRouteManager } from '@/router/useRouteManager'
import { nextTick, onMounted, onUnmounted, shallowRef } from 'vue'
import { getQueryParam } from '@/utils/get-query-param'

const activeRoutes = shallowRef([])
const activeRoutesRef = shallowRef([])

const routes = {
  intro: RollAndScoreIntro,
  highlights: RollAndScoreHighlights,
}

const {
  registerRoutes,
  navigateTo,
  isTransitioning,
  // Optional: Use this to customize how routes change behave
  // onRouteChange,
} = useRouteManager()

window.navigateTo = navigateTo

let index = 0
function handleClick(e) {
  e.preventDefault()
  if (isTransitioning.value) return
  navigateTo(Object.keys(routes)[++index])
}

// Register routes with their animations
onMounted(async () => {
  registerRoutes(routes, activeRoutes, activeRoutesRef)

  await nextTick()

  const initialView = Object.keys(routes).find((key) => getQueryParam('view', false) === key)
  index = Object.keys(routes).indexOf(initialView)
  index = index === -1 ? 0 : index

  navigateTo(initialView ?? 'intro')

  document.body.addEventListener('click', handleClick)
})

onUnmounted(() => {
  document.body.removeEventListener('click', handleClick)
})
</script>

<style lang="scss" scoped>
.routes > * {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
}
</style>
