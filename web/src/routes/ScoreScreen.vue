<template>
  <div class="center">
    <ScoreBoard
      ref="scoreBoard"
      text-variant="tv-bold-420"
      :value="score"
      :immediate="false"
    />
  </div>
</template>

<script setup>
import ScoreBoard from '@/components/ScoreBoard.vue'

import { useRouteManager } from '@/router/useRouteManager'
import { useScoreStore } from '@/store'

import { ref } from 'vue'
import { storeToRefs } from 'pinia'
import { getQueryParam } from '@/utils/get-query-param'

const scoreBoard = ref(null)

const { navigateTo } = useRouteManager()

const store = useScoreStore()

const { score } = storeToRefs(store)

defineExpose({
  animateSet: async () => {
    await scoreBoard.value.animateSet()
  },
  animateIn: async () => {
    await new Promise((resolve) => setTimeout(resolve, 2000))
    await scoreBoard.value.animateIn()
  },
  animateOut: () => {
    scoreBoard.value.animateOut()
  },
  animateIdle: async () => {
    if (getQueryParam('demo')) {
      const isAfterCoachReport = score.value > 0
      await new Promise((resolve) => setTimeout(resolve, 3000))
      store.setScore(isAfterCoachReport ? 3000 : 1234)
      await new Promise((resolve) => setTimeout(resolve, 3000))
      store.setScore(isAfterCoachReport ? 4000 : 2000)
      await new Promise((resolve) => setTimeout(resolve, 3000))
      store.setScore(isAfterCoachReport ? 5000 : 2456)
      await new Promise((resolve) => setTimeout(resolve, 3000))
      if (getQueryParam('manual')) return
      navigateTo(isAfterCoachReport ? 'final' : 'replay')
    }
  },
})
</script>

<style lang="scss" scoped>
.center {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}
</style>
