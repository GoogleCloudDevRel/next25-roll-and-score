<template>
  <div class="progress">
    <div
      class="dot"
      v-for="i in maxTries"
      :key="i"
      ref="dots"
      :class="{ active: i <= progress }"
    />
  </div>
</template>

<script setup>
import { shallowRef } from 'vue'
import { useScoreStore } from '@/store'
import { storeToRefs } from 'pinia'
import { gsap } from '@/utils/gsap'
import { pxToVw } from '@/utils/px'

const store = useScoreStore()
const { progress, maxTries } = storeToRefs(store)

const dots = shallowRef([])

defineExpose({
  animateSet: async () => {
    gsap.set(dots.value, {
      clipPath: `inset(${dots.value[0].clientHeight / 2}px round 50%)`,
    })
  },
  animateIn: async () => {
    gsap.to(dots.value, {
      clipPath: `inset(${pxToVw(-20)} round 50%)`,
      duration: 0.65,
      ease: 'power2.in',
      stagger: 0.1,
    })
  },
  animateOut: async () => {
    gsap.fromTo(
      dots.value,
      {
        clipPath: `inset(${pxToVw(-20)}px round 50%)`,
      },
      {
        clipPath: `inset(${dots.value[0].clientHeight / 2}px round 50%)`,
        duration: 0.65,
        ease: 'power2.in',
        stagger: 0.1,
      },
    )
  },
})
</script>

<style lang="scss" scoped>
.progress {
  position: fixed;
  bottom: px-to-vw(120, 4k);
  display: flex;
  gap: px-to-vw(48, 4k);
}

.dot {
  width: px-to-vw(200, 4k);
  height: px-to-vw(200, 4k);
  background-color: #666666;
  border-radius: 50%;
  box-shadow:
    0 0 0 px-to-vw(5, 4k) rgb(0, 0, 0),
    px-to-vw(15, 4k) px-to-vw(20, 4k) rgb(0, 0, 0);

  &:global(.active) {
    background-color: #fff !important;
  }
}
</style>
