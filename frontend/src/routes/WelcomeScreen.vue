<template>
  <div class="center">
    <GeminiCoach
      ref="geminiCoach"
      :title="copy.introTitle"
      :message="copy.welcomeText"
      :immediate="false"
    />
  </div>
</template>

<script setup>
import GeminiCoach from '@/components/GeminiCoach.vue'
import { getQueryParam } from '@/utils/get-query-param'
import { ref } from 'vue'
import copy from '@/copy.json'

const geminiCoach = ref(null)

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
    await new Promise((resolve) => setTimeout(resolve, copy.welcomeText.length * 50))
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
