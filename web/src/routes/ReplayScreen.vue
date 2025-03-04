<template>
  <div class="center">
    <div class="badge-top">
      <VBadge ref="badge">
        <IconBase variant="gemini" />
        <VText
          text="GEMINI COACH"
          variant="tv-bold-72"
        />
      </VBadge>
    </div>
    <div
      class="video-replay"
      ref="wrapper"
    >
      <!-- 10sec version -->
      <video
        src="https://storage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
        muted
        class="video"
        ref="video"
      />
    </div>
  </div>
</template>

<script setup>
import { gsap } from '@/utils/gsap'
import { ref } from 'vue'
import { useRouteManager } from '@/router/useRouteManager'
import { getQueryParam } from '@/utils/get-query-param'
import VBadge from '@/components/VBadge.vue'
import IconBase from '@/components/IconBase.vue'
import VText from '@/components/VText.vue'

const video = ref(null)
const wrapper = ref(null)
const badge = ref(null)

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
  padding: px-to-vw(48, 4k);

  .badge-top {
    position: absolute;
    top: px-to-vw(20, 4k);
    z-index: 100;

    :deep(svg) {
      width: px-to-vw(62, 4k);
      height: px-to-vw(62, 4k);
    }
  }

  .video-replay {
    width: 100%;
    height: 100%;
    border-radius: px-to-vw(50, 4k);
    overflow: hidden;

    .video {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  }
}
</style>
