<template>
  <div class="center">
    <GeminiCoach
      ref="geminiCoach"
      text="Welcome! Are you ready to experience Gemini 2.0’s real-time guidance, and see how AI can elevate your game?"
      :immediate="false"
    />
  </div>
</template>

<script setup>
import GeminiCoach from '@/components/GeminiCoach.vue'
import { useRouteManager } from '@/router/useRouteManager'
import { ref } from 'vue'

const geminiCoach = ref(null)

const { navigateTo } = useRouteManager()

defineExpose({
  animateSet: async () => {
    await geminiCoach.value.animateSet()
  },
  animateIn: async () => {
    await new Promise((resolve) => setTimeout(resolve, 2000))
    await geminiCoach.value.animateIn()
    await new Promise((resolve) => setTimeout(resolve, 2000))
    navigateTo('start')
  },
  animateOut: () => {
    geminiCoach.value.animateOut()
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
