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
import { getQueryParam } from '@/utils/get-query-param'
import { storeToRefs } from 'pinia'

import { onMounted, shallowRef } from 'vue'

const mobileScoreCard = shallowRef(null)

const mobileScoreStore = useMobileScoreStore()

const { leaderboard, finalScore, data, description, videoSrc } = storeToRefs(mobileScoreStore)

async function fetchAPIwithID() {
  const id = getQueryParam('id')

  // TODO: fetch data from API
  try {
    const response = await fetch(`https://api.example.com/data/${id}`)
    const data = await response.json()
    console.log('data', data)
    mobileScoreStore.setData({
      leaderboard: 10,
      finalScore: 1050,
      data: 100,
      description:
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.',
      videoSrc: 'https://storage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
    })
  } catch (error) {
    console.error('error', error)
    mobileScoreStore.setData({
      leaderboard: 10,
      finalScore: 1050,
      data: 100,
      description:
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.',
      videoSrc: 'https://storage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
    })
  }
}

onMounted(async () => {
  await fetchAPIwithID()
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
