<template>
  <RollAndScoreFinal ref="rollAndScoreFinal" />
</template>

<script setup>
import RollAndScoreFinal from '@/components/RollAndScoreFinal.vue'
import { onMounted, shallowRef } from 'vue'

const rollAndScoreFinal = shallowRef(null)
onMounted(async () => {
  await rollAndScoreFinal.value.animateSet()
  rollAndScoreFinal.value.animateIn()
})
</script>
