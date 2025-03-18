<template>
  <GameMaster
    ref="gameMaster"
  />
</template>

<script setup>
import GameMaster from '@/components/GameMaster.vue'
import { onMounted, shallowRef } from 'vue'
import { useScoreStore } from '@/store'
import { storeToRefs } from 'pinia'

const gameMaster = shallowRef(null)

onMounted(async () => {
  await gameMaster.value.animateSet()
  gameMaster.value.animateIn()
})
</script>
