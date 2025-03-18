<template>
  <div class="center">
    <GeminiCoach
      ref="geminiCoach"
      :text="text"
      :immediate="false"
    />
  </div>
</template>

<script setup>
import GeminiCoach from '@/components/GeminiCoach.vue'
import { useRouteManager } from '@/router/useRouteManager'
import { getQueryParam } from '@/utils/get-query-param'
import { ref } from 'vue'
import { useScoreStore } from '@/store'
import { storeToRefs } from 'pinia'

const props = defineProps({
  text: {
    type: String,
    default:
      'Welcome! Are you ready to experience Gemini 2.0’s real-time guidance, and see how AI can elevate your game?',
  },
})

const geminiCoach = ref(null)

const { navigateTo } = useRouteManager()

const { gameStarted } = storeToRefs(useScoreStore())

defineExpose({
  animateSet: async () => {
    await geminiCoach.value.animateSet()
  },
  animateIn: async () => {
    await new Promise((resolve) => setTimeout(resolve, 2000))
    await geminiCoach.value.animateIn()
  },
  animateOut: async () => {
    await geminiCoach.value.animateOut()
  },
  animateIdle: async () => {
    if (getQueryParam('manual')) return
    await new Promise((resolve) => setTimeout(resolve, props.text.length * 50))
    if (gameStarted.value) {
      navigateTo('start')
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
