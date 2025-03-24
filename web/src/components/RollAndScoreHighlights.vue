<template>
  <div :class="['wrapper', { 'wrapper--device-1': scoreStore.device === '1' }]">
    <div
      class="highlights"
      ref="highlights"
    >
      <div class="sidebar">
        <LeaderBoard
          ref="leaderboard"
          :score1="score1"
          :score2="score2"
          :score3="score3"
          :score4="score4"
          :score5="score5"
        />
      </div>
      <div
        class="video-block"
        ref="videoBlock"
      >
        <video
          :src="videoUrl"
          autoplay
          muted
          class="video"
          ref="video"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { shallowRef } from 'vue'
import LeaderBoard from './leaderboard/LeaderBoard.vue'
import { useHightlightsStore } from '@/store'
import { storeToRefs } from 'pinia'
import { gsap } from '@/utils/gsap'
import { useScoreStore } from '@/store'

const store = useHightlightsStore()
const scoreStore = useScoreStore()

const { score1, score2, score3, score4, score5, video: videoUrl } = storeToRefs(store)

const leaderboard = shallowRef(null)
const videoBlock = shallowRef(null)

async function animateSet() {
  await leaderboard.value.animateSet()
  gsap.set(videoBlock.value, { scale: 0 })
}
async function animateIn() {
  await new Promise((resolve) => setTimeout(resolve, 2000))
  await Promise.all([
    gsap.to(videoBlock.value, { scale: 1, duration: 1, ease: 'power2.out' }),
    leaderboard.value.animateIn(),
  ])
}
async function animateOut() {
  await leaderboard.value.animateOn()
}

defineExpose({
  animateSet,
  animateIn,
  animateOut,
})
</script>

<style lang="scss" scoped>
.wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: px-to-vw(48, 4k);

  &--device-1 {
    .sidebar {
      grid-column-start: 2;
      grid-column-end: 3;
      grid-row-start: 1;
      grid-row-end: 2;
    }
  }
}

.highlights {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: px-to-vw(48, 4k);
  width: 100%;
  flex: 1;
}

.sidebar {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.video-block {
  text-align: center;
  background: #bebebe;
  box-shadow:
    0 0 0 px-to-vw(3, 4k) #000,
    px-to-vw(10, 4k) px-to-vw(10, 4k) 0 0 #000;
  border-radius: px-to-vw(50, 4k);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  overflow: hidden;

  .video {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
}
</style>
