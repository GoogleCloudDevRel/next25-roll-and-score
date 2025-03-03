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
    await new Promise((resolve) => setTimeout(resolve, 2000))
    navigateTo('videoReplay')
  },
  animateOut: () => {
    scoreBoard.value.animateOut()
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
