<template>
  <div class="center">
    <GeminiCoach
      ref="geminiCoach"
      :show-badge="false"
      :text="copy.startText"
      :bg-color="colors.brandYellow"
      :immediate="false"
    />
  </div>
</template>

<script setup>
import GeminiCoach from '@/components/GeminiCoach.vue'
import { useRouteManager } from '@/router/useRouteManager'
import colors from '@/utils/colors'
import { getQueryParam } from '@/utils/get-query-param'
import { ref } from 'vue'
import { useScoreStore } from '@/store'
import { storeToRefs } from 'pinia'
import copy from '@/copy.json'
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
    await new Promise((resolve) => setTimeout(resolve, 2000))
    if (gameStarted.value) {
      navigateTo('score')
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
