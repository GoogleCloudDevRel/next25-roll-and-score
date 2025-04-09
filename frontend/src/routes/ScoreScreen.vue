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
      :value="totalScore"
      :immediate="false"
    />
    <VProgress ref="progress" />
  </div>
</template>

<script setup>
import ScoreBoard from '@/components/ScoreBoard.vue'
import VProgress from '@/components/VProgress.vue'
import { useScoreStore } from '@/store'

import { ref } from 'vue'
import { storeToRefs } from 'pinia'
import { getQueryParam } from '@/utils/get-query-param'
import VText from '@/components/VText.vue'

const scoreBoard = ref(null)
const progress = ref(null)
const heading = ref(null)

const store = useScoreStore()

const { totalScore, maxTries, tries } = storeToRefs(store)

defineExpose({
  animateSet: async () => {
    await heading.value.prepare()
    await scoreBoard.value.animateSet()
    await progress.value.animateSet()
  },
  animateIn: async () => {
    await new Promise((resolve) => setTimeout(resolve, 2000))
    await scoreBoard.value.animateIn()
    heading.value.animateIn()
    await progress.value.animateIn()
  },
  animateOut: () => {
    scoreBoard.value.animateOut()
    heading.value.animateOut()
    if (tries.value === maxTries.value) {
      progress.value.animateOut()
    }
  },
  animateIdle: async () => {
    if (!getQueryParam('manual')) return
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
