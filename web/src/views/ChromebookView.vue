<template>
  <RollAndScoreFinal
    ref="rollAndScoreFinal"
    :score="score"
  />
</template>

<script setup>
import RollAndScoreFinal from '@/components/RollAndScoreFinal.vue'
import { onMounted, shallowRef } from 'vue'
import { useScoreStore } from '@/store'
import { storeToRefs } from 'pinia'
const rollAndScoreFinal = shallowRef(null)

// fetch score
const scoreStore = useScoreStore()

scoreStore.setScore(1234)

const { score } = storeToRefs(scoreStore)

onMounted(async () => {
  await rollAndScoreFinal.value.animateSet()
  rollAndScoreFinal.value.animateIn()
})
</script>
