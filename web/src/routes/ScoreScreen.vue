<template>
  <div class="center">
    <div class="heading">
      <VText
        ref="heading"
        variant="tv-bold-240"
        text="Your Score"
      />
    </div>
    <ScoreBoard
      ref="scoreBoard"
      text-variant="tv-bold-575"
      :value="score"
      :immediate="false"
    />
    <VProgress ref="progress" />
  </div>
</template>

<script setup>
import ScoreBoard from '@/components/ScoreBoard.vue'
import VProgress from '@/components/VProgress.vue'
import { useRouteManager } from '@/router/useRouteManager'
import { useScoreStore } from '@/store'

import { ref } from 'vue'
import { storeToRefs } from 'pinia'
import { getQueryParam } from '@/utils/get-query-param'
import VText from '@/components/VText.vue'

const scoreBoard = ref(null)
const progress = ref(null)
const heading = ref(null)

const { navigateTo } = useRouteManager()

const store = useScoreStore()

const { score } = storeToRefs(store)

defineExpose({
  animateSet: async () => {
    await heading.value.prepare()
    await scoreBoard.value.animateSet()
    if (score.value === 0) {
      await progress.value.animateSet()
    }
  },
  animateIn: async () => {
    await new Promise((resolve) => setTimeout(resolve, 2000))
    await scoreBoard.value.animateIn()
    heading.value.animateIn()
    if (score.value === 0) {
      await progress.value.animateIn()
    }
  },
  animateOut: () => {
    scoreBoard.value.animateOut()
    heading.value.animateOut()
    if (store.maxTries === store.progress) {
      progress.value.animateOut()
    }
  },
  animateIdle: async () => {
    const isAfterCoachReport = score.value > 0
    await new Promise((resolve) => setTimeout(resolve, 2500))
    store.setScore(isAfterCoachReport ? 3000 : 1234)
    await new Promise((resolve) => setTimeout(resolve, 2500))
    store.setScore(isAfterCoachReport ? 4000 : 2000)
    await new Promise((resolve) => setTimeout(resolve, 2500))
    if (!isAfterCoachReport) {
      store.setScore(2456)
      await new Promise((resolve) => setTimeout(resolve, 2500))
    }
    if (getQueryParam('manual')) return
    navigateTo(isAfterCoachReport ? 'final' : 'replay')
  },
})
</script>

<style lang="scss" scoped>
.heading {
  position: absolute;
  top: px-to-vw(60, 4k);
}
.center {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}
</style>
