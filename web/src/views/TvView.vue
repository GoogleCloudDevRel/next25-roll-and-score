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
import RollAndScoreIntro from '@/components/RollAndScoreIntro.vue'
import { useRouteManager } from '@/router/useRouteManager'

import { nextTick, onMounted, onUnmounted, shallowRef } from 'vue'

import WelcomeScreen from '../routes/WelcomeScreen.vue'
import StartScreen from '../routes/StartScreen.vue'
import ScoreScreen from '../routes/ScoreScreen.vue'
import ReplayScreen from '../routes/ReplayScreen.vue'
import ReportScreen from '../routes/ReportScreen.vue'
import FinalScreen from '../routes/FinalScreen.vue'

const activeRoutes = shallowRef([])
const activeRoutesRef = shallowRef([])

const routes = {
  intro: RollAndScoreIntro,
  welcome: WelcomeScreen,
  start: StartScreen,
  score: ScoreScreen,
  replay: ReplayScreen,
  report: ReportScreen,
  final: FinalScreen,
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
const navigationExample = ['intro', 'welcome', 'start', 'score', 'replay', 'report', 'score', 'final']
function handleClick(e) {
  e.preventDefault()
  if (isTransitioning.value) return
  navigateTo(navigationExample[++index])
}

// Register routes with their animations
onMounted(async () => {
  registerRoutes(routes, activeRoutes, activeRoutesRef)

  await nextTick()

  navigateTo('intro')

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
