<template>
  <GameMaster ref="gameMaster" />
</template>

<script setup>
import GameMaster from '@/components/GameMaster.vue'
import { onMounted, shallowRef } from 'vue'

const gameMaster = shallowRef(null)

onMounted(async () => {
  await gameMaster.value.animateSet()
  gameMaster.value.animateIn()
})
</script>
