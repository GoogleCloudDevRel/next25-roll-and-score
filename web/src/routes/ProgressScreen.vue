<template>
  <div class="center">
    <VText
      ref="progressTextRef"
      variant="tv-bold-240"
      text="Loading analysis"
    />
    <div
      class="gemini-icon-spin"
      ref="geminiIconSpinRef"
    >
      <IconGemini class="gemini-icon" />
    </div>
    <VProgress />
    <VConfetti
      ref="confetti"
      use-blue
    />
  </div>
</template>

<script setup>
import { useRouteManager } from '@/router/useRouteManager'
import { useScoreStore } from '@/store'
import { storeToRefs } from 'pinia'
import VText from '@/components/VText.vue'
import { ref, watch } from 'vue'
import copy from '@/copy.json'
import IconGemini from '@/components/icons/IconGemini.vue'
import { gsap } from '@/utils/gsap'
import VProgress from '@/components/VProgress.vue'
import VConfetti from '@/components/VConfetti.vue'
const { navigateTo, isTransitioning, previousRoute } = useRouteManager()

const { gameStarted, geminiReport, replayVideo } = storeToRefs(useScoreStore())

const progressTextRef = ref(null)
const geminiIconSpinRef = ref(null)
const confetti = ref(null)

watch(
  () => geminiReport.value && replayVideo.value && gameStarted.value && !isTransitioning.value,
  (v) => {
    if (v) {
      navigateTo(previousRoute.value.id === 'replay' ? 'report' : 'replay')
    }
  },
  { immediate: true },
)

const animatedOut = ref(false)

defineExpose({
  animateSet: async () => {
    gsap.set(geminiIconSpinRef.value, {
      scale: 0,
    })
    await progressTextRef.value.prepare()
    confetti.value.animateSet()
  },
  animateIn: async () => {
    animatedOut.value = false
    await Promise.all([
      confetti.value.animateIn(2),
      progressTextRef.value.animateIn(2),
      gsap.to(geminiIconSpinRef.value, {
        scale: 1,
        rotate: '+=180',
        duration: 2,
        delay: 1.4,
        ease: 'expo.inOut',
      }),
    ])
  },
  animateOut: async () => {
    animatedOut.value = true
    await Promise.all([
      progressTextRef.value.animateOut(),
      gsap.to(geminiIconSpinRef.value, {
        rotate: '+=180',
        scale: 0,
        duration: 1.2,
        ease: 'power2.inOut',
      }),
    ])
  },
  animateIdle: async () => {
    let i = 0
    while (true) {
      if (animatedOut.value) break
      await new Promise((resolve) => setTimeout(resolve, 1200))
      if (animatedOut.value) break
      gsap.to(geminiIconSpinRef.value, {
        rotate: '+=180',
        duration: 1.2,
        ease: 'power2.inOut',
      })
      await progressTextRef.value.animateOut(0, { duration: 0.4, ease: 'power2.inOut' })
      if (animatedOut.value) break
      await progressTextRef.value.setText(copy.progressText[i])
      if (animatedOut.value) break
      await progressTextRef.value.animateIn(0, { duration: 0.8, ease: 'power2.out' })
      if (animatedOut.value) break
      i = (i + 1) % copy.progressText.length
    }
  },
})
</script>

<style lang="scss" scoped>
.center {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  height: 100%;
  color: $brandBlue;
  padding: px-to-vw(160, 4k);

  .VText {
    position: absolute;
    padding-bottom: px-to-vw(1500, 4k);
  }
}

.gemini-icon {
  width: px-to-vw(950, 4k);
  height: px-to-vw(950, 4k);
  stroke: #000;
  stroke-width: px-to-vw(10, 4k);
  paint-order: fill stroke;
}
</style>
