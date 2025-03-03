<template>
  <MobileScoreCard
    ref="mobileScoreCard"
    video-src="/images/video.mp4"
    leaderboard="100"
    final-score="100"
    data="100"
    description="Lorem ipsum dolor sit amet, consec tetur adipiscing elit. Suspendisse nec ipsum eu tortor mattis facilisis. Nam consequat arcu ut lorem pretium, id porttitor sem porttitor. Nunc facilisis lacus eu velit fermentum, "
  />
</template>

<script setup>
import MobileScoreCard from '@/components/mobile-score-card/MobileScoreCard.vue'

import { onMounted, shallowRef } from 'vue'

const mobileScoreCard = shallowRef(null)

onMounted(async () => {
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
