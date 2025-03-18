<template>
  <MobileScoreCard
    ref="mobileScoreCard"
    :video-src="videoSrc"
    :leaderboard="leaderboard"
    :final-score="finalScore"
    :data="data"
    :description="description"
  />
</template>

<script setup>
import MobileScoreCard from '@/components/mobile-score-card/MobileScoreCard.vue'
import { useMobileScoreStore } from '@/store'
import { storeToRefs } from 'pinia'

import { onMounted, shallowRef } from 'vue'

const mobileScoreCard = shallowRef(null)

const mobileScoreStore = useMobileScoreStore()

const { leaderboard, finalScore, data, description, videoSrc } = storeToRefs(mobileScoreStore)

const promise = mobileScoreStore.setData()

onMounted(async () => {
  await promise
  await mobileScoreCard.value.animateSet()

  mobileScoreCard.value.animateIn()
})
</script>

<style lang="scss" scoped>
.routes {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
}
</style>
