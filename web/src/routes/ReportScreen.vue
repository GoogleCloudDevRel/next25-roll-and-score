<template>
  <div class="center">
    <GeminiCoach
      ref="geminiCoach"
      :text="geminiReport"
      :immediate="false"
    />
    <VProgress />
  </div>
</template>

<script setup>
import GeminiCoach from '@/components/GeminiCoach.vue'
import VProgress from '@/components/VProgress.vue'
import { useRouteManager } from '@/router/useRouteManager'
import { getQueryParam } from '@/utils/get-query-param'
import { ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useScoreStore } from '@/store'

const geminiCoach = ref(null)
const scoreStore = useScoreStore()
const { geminiReport } = storeToRefs(scoreStore)

const { navigateTo } = useRouteManager()

defineExpose({
  animateSet: async () => {
    await geminiCoach.value.animateSet()
  },
  animateIn: async () => {
    await new Promise((resolve) => setTimeout(resolve, 2000))
    await geminiCoach.value.animateIn()
    // wait for the text to be read
  },
  animateOut: () => {
    geminiCoach.value.animateOut()
  },
  animateIdle: async () => {
    if (getQueryParam('manual')) return
    await new Promise((resolve) => setTimeout(resolve, geminiReport.value.length * 50))
    navigateTo('score')
  },
})
</script>

<style lang="scss" scoped>
.center {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  padding-bottom: px-to-vw(260, 4k);
}
</style>
