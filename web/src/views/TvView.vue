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

import { nextTick, onMounted, onUnmounted, shallowRef, watch } from 'vue'

import WelcomeScreen from '../routes/WelcomeScreen.vue'
import StartScreen from '../routes/StartScreen.vue'
import ScoreScreen from '../routes/ScoreScreen.vue'
import ReplayScreen from '../routes/ReplayScreen.vue'
import ReportScreen from '../routes/ReportScreen.vue'
import FinalScreen from '../routes/FinalScreen.vue'
import { getQueryParam } from '@/utils/get-query-param'
import { subscribeGameStarted, subscribeToScoreChanges, useScoreStore } from '@/store'
import { storeToRefs } from 'pinia'
import { signIn } from '@/config/firebaseConfig'


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

const { registerRoutes, navigateTo, isTransitioning } = useRouteManager()
const { gameStarted } = storeToRefs(useScoreStore())

watch(
  () => !gameStarted.value && !isTransitioning.value,
  (v) => {
    if (v) {
      navigateTo('intro')
    }
  },
)

let index = 0
const navigationFlow = [
  'intro',
  'welcome',
  'start',
  'score',
  'replay',
  'report',
  'score',
  'replay',
  'report',
  'score',
  'final',
]

function handleClick(e) {
  e.preventDefault()
  if (isTransitioning.value) return
  navigateTo(navigationFlow[++index])
}

let unsubscribeGameStarted = null
let unsubscribeScoreChanges = null

// Register routes with their animations
onMounted(async () => {
  const initialView = navigationFlow.find((key) => getQueryParam('view', false) === key)
  index = navigationFlow.indexOf(initialView)
  index = index === -1 ? 0 : index

  registerRoutes(routes, activeRoutes, activeRoutesRef)

  await nextTick()

  navigateTo(initialView ?? navigationFlow[0])

  document.body.addEventListener('click', handleClick)

  await signIn()

  unsubscribeGameStarted = subscribeGameStarted()
  unsubscribeScoreChanges = subscribeToScoreChanges()
})

onUnmounted(() => {
  unsubscribeGameStarted()
  unsubscribeScoreChanges()
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
