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
      :badgeIcon="rank > 0 && rankStep === 0 ? false : true"
      :badgeText="rank > 0 && rankStep === 0 ? `TOP 5 SCORE` : 'GEMINI COACH'"
      :badgeVariant="rank > 0 && rankStep === 0 ? 'red' : 'yellow'"
      :text="
        rank > 0 && rankStep === 0
          ? `Congratulations, you ranked <span class='highlight'>#${rank}</span> in today’s Roll & Score`
          : 'Great job! Now approach the staff to collect to your comprehensive analysis!'
      "
    />
    <VConfetti ref="confetti" />
  </div>
</template>

<script setup>
import GeminiCoachDrawer from '@/components/GeminiCoachDrawer.vue'
import ScoreBoard from '@/components/ScoreBoard.vue'
import VConfetti from '@/components/VConfetti.vue'
import { computed, ref } from 'vue'
import { useHightlightsStore, useScoreStore } from '@/store'
import { storeToRefs } from 'pinia'

const drawer = ref(null)
const scoreBoard = ref(null)
const confetti = ref(null)

const scoreStore = useScoreStore()
const highlightsStore = useHightlightsStore()

const { score } = storeToRefs(scoreStore)
const { score1, score2, score3, score4, score5 } = storeToRefs(highlightsStore)

const rank = computed(() => {
  if (score.value >= score1.value) return 1
  if (score.value >= score2.value) return 2
  if (score.value >= score3.value) return 3
  if (score.value >= score4.value) return 4
  if (score.value >= score5.value) return 5
  return 0
})

const rankStep = ref(0)

defineExpose({
  animateSet: async () => {
    await drawer.value.animateSet()
    await scoreBoard.value.animateSet()
    confetti.value.animateSet()
  },
  animateIn: async () => {
    await new Promise((resolve) => setTimeout(resolve, 2000))
    scoreBoard.value.animateIn()
    await drawer.value.animateIn()
    if (rank.value > 0) {
      confetti.value.animateIn()
      await new Promise((resolve) => setTimeout(resolve, 6000))
      await Promise.all([drawer.value.badge().animateOut(), drawer.value.text().animateOut()])
      rankStep.value = 1
      await drawer.value.badge().animateSet()
      await drawer.value.text().animateSet()
      drawer.value.badge().animateIn()
      drawer.value.text().animateIn()
    }
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

  :global(.highlight) {
    color: $brandYellow;
  }
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
