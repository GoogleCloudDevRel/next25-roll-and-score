<template>
  <div class="center">
    <GeminiCoach
      ref="geminiCoach"
      :text="geminiReport"
      :immediate="false"
    />
  </div>
</template>

<script setup>
import GeminiCoach from '@/components/GeminiCoach.vue'
import { useRouteManager } from '@/router/useRouteManager'
import { ref } from 'vue'
import { useGeminiReportStore } from '@/store'
import { storeToRefs } from 'pinia'

const geminiCoach = ref(null)
const geminiReportStore = useGeminiReportStore()
const { text: geminiReport } = storeToRefs(geminiReportStore)

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
}
</style>
