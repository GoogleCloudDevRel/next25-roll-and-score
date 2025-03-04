<template>
  <div class="center">
    <GeminiCoach
      ref="geminiCoach"
      :show-badge="false"
      text="Roll the ball to start!"
      :bg-color="colors.brandYellow"
      :immediate="false"
    />
  </div>
</template>

<script setup>
import GeminiCoach from '@/components/GeminiCoach.vue'
import { useRouteManager } from '@/router/useRouteManager'
import colors from '@/utils/colors'
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
  },
  animateOut: () => {
    geminiCoach.value.animateOut()
  },
  animateIdle: async () => {
    await new Promise((resolve) => setTimeout(resolve, 2000))
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
