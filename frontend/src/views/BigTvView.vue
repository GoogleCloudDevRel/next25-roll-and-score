<template>
  <BackgroundBase
    :dpr="1"
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
  <QRCode :value="'https://www.google.com'" />
</template>

<script setup>
import BackgroundBase from '@/components/background/BackgroundBase.vue'
import BackgroundRings from '@/components/background/BackgroundRings.vue'
import RollAndScoreHighlights from '@/components/RollAndScoreHighlights.vue'
import RollAndScoreIntro from '@/components/RollAndScoreIntro.vue'
import { useRouteManager } from '@/router/useRouteManager'
import { nextTick, onMounted, onUnmounted, shallowRef } from 'vue'
import { getQueryParam } from '@/utils/get-query-param'
import QRCode from '@/components/QRCode.vue'
import { subscribeToHighlightsChanges } from '@/store'
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

let timer = null
let duration = 10000 // 10 seconds
const currentScreen = shallowRef('intro')

const startLoopTimer = () => {
  clearTimeout(timer)

  if (currentScreen.value === 'intro') {
    duration = 10000 // 10 seconds for intro
  } else if (currentScreen.value === 'highlights') {
    duration = 30000 // 30 seconds for highlights
  }

  timer = setTimeout(() => {
    if (currentScreen.value === 'intro') {
      currentScreen.value = 'highlights'
      navigateTo(currentScreen.value)
    } else if (currentScreen.value === 'highlights') {
      currentScreen.value = 'intro'
      navigateTo(currentScreen.value)
    }

    startLoopTimer() // Continue the cycle
  }, duration)
}

let unsubscribeHighlightsChanges = null
// Register routes with their animations
onMounted(async () => {
  registerRoutes(routes, activeRoutes, activeRoutesRef)

  await nextTick()

  const initialView = Object.keys(routes).find((key) => getQueryParam('view', false) === key)
  index = Object.keys(routes).indexOf(initialView)
  index = index === -1 ? 0 : index
  navigateTo(initialView ?? 'intro')

  if (getQueryParam('manual')) {
    document.body.addEventListener('click', handleClick)
  } else {
    startLoopTimer()
  }

  unsubscribeHighlightsChanges = subscribeToHighlightsChanges()
})

onUnmounted(() => {
  if (getQueryParam('manual')) {
    document.body.removeEventListener('click', handleClick)
  }
  unsubscribeHighlightsChanges()
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
