<template>
  <RollAndScoreFinal
    ref="rollAndScoreFinal"
    :score="finalScore"
    :gameId="gameId"
    :videoSrc="videoSrc"
  />
</template>

<script setup>
import RollAndScoreFinal from '@/components/RollAndScoreFinal.vue'
import { onMounted, shallowRef } from 'vue'
import { useChromebookStore } from '@/store'
import { storeToRefs } from 'pinia'
const rollAndScoreFinal = shallowRef(null)

const chromebookStore = useChromebookStore()

const { finalScore, gameId, videoSrc } = storeToRefs(chromebookStore)

const promise = chromebookStore.setData()

onMounted(async () => {
  await promise
  await rollAndScoreFinal.value.animateSet()
  rollAndScoreFinal.value.animateIn()
})
</script>
