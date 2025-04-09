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

import { shallowRef, ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { storeToRefs } from 'pinia'

import { useRouteManager } from '@/router/useRouteManager'
import {
  subscribeGameStarted,
  subscribeTotalScore,
  subscribeToHighlightsChanges,
  useScoreStore,
} from '@/store'

import WelcomeScreen from '../routes/WelcomeScreen.vue'
import StartScreen from '../routes/StartScreen.vue'
import ScoreScreen from '../routes/ScoreScreen.vue'
import ProgressScreen from '../routes/ProgressScreen.vue'
import ReplayScreen from '../routes/ReplayScreen.vue'
import ReportScreen from '../routes/ReportScreen.vue'
import FinalScreen from '../routes/FinalScreen.vue'

const { navigateTo, currentRoute, registerRoutes, isTransitioning } = useRouteManager()
const scoreStore = useScoreStore()
const {
  device,
  gameId,
  gameStarted,
  totalScore,
  tries,
  triesPerStep,
  maxTries,
  replayVideo,
  geminiAnalysis,
} = storeToRefs(scoreStore)
const stationId = computed(() => device.value.padStart(2, '0'))

const unsubFunctionContainer = {}
const hasShownProgess = ref(false)
const hasShownReport = ref(false)
const hasShownReplay = ref(false)

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
const currentScreen = computed(() => currentRoute.value?.id)

// --- Route registration ---
registerRoutes(routeComponents, activeRoutes, activeRoutesRef)

// --- Helper function to navigate ---
const navigateToScreen = async (screen) => {
  if (currentRoute.value?.id !== screen) {
    console.log(`Navigation: From ${currentRoute.value?.id} to ${screen}`)
    await navigateTo(screen)
  }
}

// --- Helper function to wait ---
const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

// --- Timers for sequences ---
const introWelcomeLoopTimer = ref(null)

// --- Helper function to clear all timers ---
const clearAllTimers = () => {
  if (introWelcomeLoopTimer.value) {
    clearTimeout(introWelcomeLoopTimer.value)
    introWelcomeLoopTimer.value = null
  }
}

// --- Intro/Welcome Loop ---
const startIntroWelcomeLoop = () => {
  clearAllTimers() // Ensure other timers are stopped

  const loop = async () => {
    if (!gameStarted.value) {
      // Only loop if game is not started
      if (currentScreen.value === 'intro') {
        navigateToScreen('welcome')
      } else {
        // Default to intro if not on welcome (or if initial state)
        navigateToScreen('intro')
      }
      // Schedule next loop iteration
      if (!gameStarted.value) {
        // Double check game hasn't started during navigation
        introWelcomeLoopTimer.value = setTimeout(loop, 7000) // 7 seconds interval
      }
    } else {
      introWelcomeLoopTimer.value = null // Stop timer if game started
    }
  }
  loop() // Start the loop immediately
}

// --- Watchers ---
watch(
  () => gameStarted.value && !isTransitioning.value,
  async (isReadyToShowGameScreen) => {
    if (isReadyToShowGameScreen) {
      if (currentScreen.value === 'intro' || currentScreen.value === 'welcome') {
        console.log('gameStarted Watcher: Game is running. Clearing all timers')
        clearAllTimers()

        if (!Object.hasOwn(unsubFunctionContainer, 'totalScore')) {
          console.log('gameStarted Watcher: Subscribe to totalScore')
          addSubscription('totalScore', await subscribeTotalScore())
        }

        if (!Object.hasOwn(unsubFunctionContainer, 'highScores')) {
          console.log('gameStarted Watcher: Subscribe to totalScore')
          addSubscription('highScores', await subscribeToHighlightsChanges())
        }

        if (totalScore.value > 0) {
          console.log('gameStarted Watcher: Scores exist. Showing Score')
          navigateToScreen('score')
        } else {
          console.log('gameStarted Watcher: Game started. Showing Start')
          navigateToScreen('start')
        }
      }
    } else {
      if (!gameStarted.value) {
        console.log('gameStarted Watcher: Game is not running. Loop Intro/ Welcome')
        scoreStore.reset()
        startIntroWelcomeLoop()
      }
    }
  },
)

watch(
  () =>
    currentScreen.value === 'start' &&
    totalScore.value > 0 &&
    gameStarted.value &&
    !isTransitioning.value,
  (isStartScreen) => {
    if (isStartScreen) {
      console.log('Start Page Watcher: Scores exist. Showing Score')
      navigateToScreen('score')
    }
  },
)

watch(
  () =>
    currentScreen.value === 'score' &&
    totalScore.value > 0 &&
    tries.value % triesPerStep.value === 0 &&
    gameStarted.value &&
    !isTransitioning.value,
  async (value) => {
    if (value) {
      if (!hasShownProgess.value) {
        console.log('Score Page Watcher: Round Ends.')
        clearAllTimers()
        await delay(1000)
        navigateToScreen('progress')
        hasShownProgess.value = true
      }
    }
  },
)

watch(
  () =>
    replayVideo.value &&
    currentScreen.value === 'progress' &&
    !hasShownReplay.value &&
    gameStarted.value &&
    !isTransitioning.value,
  async (isGeminiAnalysisOut) => {
    if (isGeminiAnalysisOut) {
      console.log('Watcher: Replay video is out. Showing Replay')
      navigateToScreen('replay')
      await delay(10000)
      hasShownReplay.value = true

      if (geminiAnalysis.value) {
        console.log('Watcher: Gemini analysis is not out. Showing Report')
        navigateToScreen('report')
        await delay(10000)
        hasShownReport.value = true

        resumeOrFinishGame()
      } else {
        console.log('Watcher: Waiting for Gemini analysis. Showing Progress')
        navigateToScreen('progress')
      }
    }
  },
)

watch(
  () =>
    geminiAnalysis.value &&
    currentScreen.value === 'progress' &&
    hasShownReplay.value &&
    !hasShownReport.value &&
    gameStarted.value &&
    !isTransitioning.value,
  async (isGeminiAnalysisOut) => {
    if (isGeminiAnalysisOut) {
      console.log('Watcher: Gemini analysis is out. Showing Report')
      navigateTo('report')
      await delay(10000)
      hasShownReport.value = true

      resumeOrFinishGame()
    }
  },
)

watch(
  () => tries.value === 4 && gameStarted.value && !isTransitioning.value,
  async (is4Tries) => {
    if (is4Tries) {
      console.log('Watcher: 4 tries. Reset hasShown variables')
      hasShownProgess.value = false
      hasShownReport.value = false
      hasShownReplay.value = false
    }
  },
)

const resumeGame = async () => {
  console.log(`Resuming game ${gameId.value} for Station ${stationId.value}`)
  try {
    const response = await fetch('/api/resume_game', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        stationId: stationId.value,
        gameId: gameId.value,
      }),
    })
    const data = await response.json()
    console.log(`Game ${gameId.value} resumed successfully:`, data)
  } catch (error) {
    console.error(`Error resuming game: ${gameId.value} for Station ${stationId.value}`, error)
  }
}

const finishGame = async () => {
  console.log(`Finishing game ${gameId.value} for Station ${stationId.value}`)
  try {
    const response = await fetch('/api/reset_station', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        stationId: stationId.value,
      }),
    })
    const data = await response.json()
    console.log(`Game ${gameId.value} finished successfully:`, data)
  } catch (error) {
    console.error(`Error finishing game: ${gameId.value} for Station ${stationId.value}`, error)
  }
}

const resumeOrFinishGame = async () => {
  if (tries.value === 3) {
    console.log('Watcher: Resuming game. Showing Score')
    navigateTo('score')
    resumeGame()
  } else if (tries.value === maxTries.value) {
    console.log('Watcher: Finishing game. Showing Score')
    navigateTo('final')
    await delay(10000)
    finishGame()
  }
}

// --- Firestore Subscription Management ---
const addSubscription = async (key, func) => {
  if (Object.hasOwn(unsubFunctionContainer, key)) {
    clearSubscription(unsubFunctionContainer[key])
  }
  unsubFunctionContainer[key] = func
}

const clearAllSubscriptions = async () => {
  for (const key in unsubFunctionContainer) {
    if (Object.hasOwn(unsubFunctionContainer, key)) {
      clearSubscription(unsubFunctionContainer[key])
    }
  }
}

const clearSubscription = async (func) => {
  if (typeof func === 'function') {
    await func()
  }
}

// --- Initial Load Logic ---
onMounted(async () => {
  navigateToScreen('intro')

  console.log('TV - onMounted: Retriving Station Info from Firestore')
  await scoreStore.getStationInfo()

  console.log('TV - onMounted: Subscribe to gameStarted')
  addSubscription('gameStarted', await subscribeGameStarted())

  if (gameStarted.value) {
    console.log('TV - onMounted: Retriving Game Info from Firestore')
    await scoreStore.getGameInfo()

    console.log('TV - onMounted: Subscribe to totalScore')
    addSubscription('totalScore', await subscribeTotalScore())
  }
})

onUnmounted(() => {
  console.log('onOumnted!')
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
