<template>
  <div class="final-screen">
    <div class="half-top">
      <ScoreBoard
        ref="scoreBoard"
        textVariant="tv-bold-420"
        :value="score"
        :immediate="false"
      />
    </div>
    <GeminiCoachDrawer
      ref="drawer"
      text="Great job! Now approach the staff to collect to your comprehensive analysis!"
    />
  </div>
</template>

<script setup>
import GeminiCoachDrawer from '@/components/GeminiCoachDrawer.vue'
import ScoreBoard from '@/components/ScoreBoard.vue'
import { ref } from 'vue'
import { useScoreStore } from '@/store'
import { storeToRefs } from 'pinia'

const drawer = ref(null)
const scoreBoard = ref(null)
const scoreStore = useScoreStore()
const { score } = storeToRefs(scoreStore)

defineExpose({
  animateSet: async () => {
    await drawer.value.animateSet()
    await scoreBoard.value.animateSet()
  },
  animateIn: async () => {
    await new Promise((resolve) => setTimeout(resolve, 2000))
    scoreBoard.value.animateIn()
    await drawer.value.animateIn()
  },
  animateOut: async () => {
    await drawer.value.animateOut()
    await scoreBoard.value.animateOut()
  },
})
</script>

<style lang="scss" scoped>
.final-screen {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.half-top {
  position: absolute;
  top: 0;
  left: 0;
  height: 50vh;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
