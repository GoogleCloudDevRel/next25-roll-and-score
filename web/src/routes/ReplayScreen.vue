<template>
  <div class="center">
    <div class="video-replay">
      <div class="badge-top">
        <VBadge
          ref="badge"
          variant="green"
          classes="badge"
        >
          <VText
            text="REPLAY"
            variant="tv-bold-72"
          />
        </VBadge>
      </div>
      <div
        class="clip"
        ref="wrapper"
      >
        <video
          :src="replayVideo"
          muted
          class="video"
          ref="video"
        />
      </div>
    </div>
    <VProgress />
  </div>
</template>

<script setup>
import { gsap } from '@/utils/gsap'
import { ref } from 'vue'
import { useRouteManager } from '@/router/useRouteManager'
import { getQueryParam } from '@/utils/get-query-param'
import VBadge from '@/components/VBadge.vue'
import VText from '@/components/VText.vue'
import VProgress from '@/components/VProgress.vue'
import { useScoreStore } from '@/store'
import { storeToRefs } from 'pinia'

const video = ref(null)
const wrapper = ref(null)
const badge = ref(null)

const { replayVideo } = storeToRefs(useScoreStore())

const { navigateTo } = useRouteManager()

const animateSet = () => {
  gsap.set(wrapper.value, {
    scale: 0,
  })
  gsap.set(video.value, {
    scale: 1.5,
  })
  badge.value.animateSet()
}

const animateIn = async () => {
  await new Promise((resolve) => setTimeout(resolve, 2000))

  video.value.play()

  badge.value.animateIn()

  gsap.to(wrapper.value, {
    scale: 1,
    duration: 1,
    ease: 'power2.inOut',
  })
  gsap.to(video.value, {
    scale: 1,
    duration: 1,
    ease: 'power2.inOut',
  })
}

const animateOut = () => {
  badge.value.animateOut()

  gsap.to(wrapper.value, {
    scale: 0,
    duration: 1,
    ease: 'power2.inOut',
  })
  gsap.to(video.value, {
    scale: 1.5,
    duration: 1,
    ease: 'power2.inOut',
  })
}

defineExpose({
  animateSet,
  animateIn,
  animateOut,
  animateIdle: async () => {
    if (getQueryParam('manual')) return
    await Promise.race([
      new Promise((resolve) => (video.value.onended = () => resolve())),
      new Promise((resolve) => setTimeout(resolve, 5000)),
    ])
    navigateTo('report')
  },
})
</script>

<style lang="scss" scoped>
.center {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  padding: px-to-vw(220, 4k) px-to-vw(360, 4k);

  .badge-top {
    position: absolute;
    transform: translateY(calc(-50% - px-to-vw(10, 4k)));
    z-index: 100;

    :deep(svg) {
      width: px-to-vw(62, 4k);
      height: px-to-vw(62, 4k);
    }
  }

  .video-replay {
    position: relative;
    display: flex;
    justify-content: center;
    height: 100%;
    aspect-ratio: 16 / 9;

    .clip {
      border-radius: px-to-vw(50, 4k);
      overflow: hidden;
      box-shadow:
        0 0 0 px-to-vw(6, 4k) #000,
        px-to-vw(12, 4k) px-to-vw(16, 4k) #000;
    }

    .video {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  }

  .badge {
    min-width: px-to-vw(618, 4k);
    text-align: center;
    justify-content: center;
  }
}
</style>
