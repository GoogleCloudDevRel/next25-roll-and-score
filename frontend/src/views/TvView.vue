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

import { shallowRef, watch, onMounted, computed, onUnmounted, ref } from 'vue'
import { useRouteManager } from '@/router/useRouteManager'
import { subscribeGameStarted, subscribeTotalScore, useScoreStore } from '@/store'

import WelcomeScreen from '../routes/WelcomeScreen.vue'
import StartScreen from '../routes/StartScreen.vue'
import ScoreScreen from '../routes/ScoreScreen.vue'
import ProgressScreen from '../routes/ProgressScreen.vue'
import ReplayScreen from '../routes/ReplayScreen.vue'
import ReportScreen from '../routes/ReportScreen.vue'
import FinalScreen from '../routes/FinalScreen.vue'

const scoreStore = useScoreStore()
const { navigateTo, currentRoute, registerRoutes } = useRouteManager()

const gameStarted = computed(() => scoreStore.gameStarted)
const totalScore = computed(() => scoreStore.totalScore)
const gameId = computed(() => scoreStore.gameId)
const tries = computed(() => scoreStore.tries)
const maxTries = computed(() => scoreStore.maxTries)

const activeRoutes = shallowRef([])
const activeRoutesRef = shallowRef([])
const routeComponents = {
  intro: RollAndScoreIntro,
  welcome: WelcomeScreen,
  start: StartScreen,
  score: ScoreScreen,
  progress: ProgressScreen,
  replay: ReplayScreen,
  report: ReportScreen,
  final: FinalScreen,
}

// --- Route registration ---
registerRoutes(routeComponents, activeRoutes, activeRoutesRef)

// --- Helper function to navigate ---
const navigateToScreen = async (screen) => {
  if (currentRoute.value?.id !== screen) {
    navigateTo(screen)
  }
}

// --- Timers for sequences ---
const introWelcomeLoopTimer = ref(null)
const scoreReplyReportTimer = ref(null)

// --- Helper function to clear all timers ---
const clearAllTimers = () => {
  if (introWelcomeLoopTimer.value) {
    clearTimeout(introWelcomeLoopTimer.value)
    introWelcomeLoopTimer.value = null
  }
  if (scoreReplyReportTimer.value) {
    clearTimeout(scoreReplyReportTimer.value)
    scoreReplyReportTimer.value = null
  }
}

// --- Intro/Welcome Loop ---
const startIntroWelcomeLoop = () => {
  clearAllTimers() // Ensure other timers are stopped

  const loop = async () => {
    if (!gameStarted.value) {
      // Only loop if game is not started
      const currentScreen = currentRoute.value?.id
      if (currentScreen === 'intro') {
        await navigateToScreen('welcome')
      } else {
        // Default to intro if not on welcome (or if initial state)
        await navigateToScreen('intro')
      }
      // Schedule next loop iteration
      if (!gameStarted.value) {
        // Double check game hasn't started during navigation
        introWelcomeLoopTimer.value = setTimeout(loop, 10000) // 10 seconds interval
      }
    } else {
      introWelcomeLoopTimer.value = null // Stop timer if game started
    }
  }
  loop() // Start the loop immediately
}

// --- Intro/Welcome Loop and Score Page Navigation Watcher ---
watch(
  () => [gameStarted.value, totalScore.value],
  ([isGameRunning], [newTotalScoreVal, oldTotalScoreVal]) => {
    if (isGameRunning === false) {
      console.log('Watcher: Game is not running. Looping Intro and Welcome')
      startIntroWelcomeLoop()
    } else {
      console.log('Watcher: Game is running. Clearing all timers')
      clearAllTimers()

      if (newTotalScoreVal > oldTotalScoreVal) {
        console.log('Watcher: A throw was made. Go to Score')
        navigateToScreen('score')
      } else {
        console.log('Watcher: Game is running. Go to Start')
        navigateToScreen('start')
      }
    }
  },
)

// --- Subscriptions Watcher ---
watch(
  () => gameStarted.value,
  async (isGameRunning) => {
    if (isGameRunning === true) {
      console.log('Subscribe to totalScore')
      unsubFunctionContainer['totalScore'] = await subscribeTotalScore(gameId.value)
    }
  },
)

// --- Firestore Subscription Management ---
const unsubFunctionContainer = {}

const clearAllSubscriptions = async () => {
  for (const key in unsubFunctionContainer) {
    if (Object.hasOwn(unsubFunctionContainer, key)) {
      const unsubscribeFunction = unsubFunctionContainer[key]
      if (typeof unsubscribeFunction === 'function') {
        await unsubscribeFunction()
      }
    }
  }
}

// --- Initial Load Logic ---
onMounted(async () => {
  await scoreStore.getStationInfo()

  if (!gameStarted.value && currentRoute.value?.id !== 'intro') {
    console.log('Game is not running. Looping Intro and Welcome')
    navigateTo('intro') // Default until state is known
  }

  console.log('Subscribe to gameStarted')
  unsubFunctionContainer['gameStarted'] = await subscribeGameStarted()
})

onUnmounted(() => {
  clearAllTimers() // Clean up timers
  clearAllSubscriptions() // Clean up subscriptions
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
