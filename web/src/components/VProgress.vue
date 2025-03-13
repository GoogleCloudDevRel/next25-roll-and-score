<template>
  <div
    class="progress"
    ref="progress"
  >
    <div
      class="group"
      v-for="i in maxSteps"
      :key="i"
    >
      <div
        class="dot"
        v-for="j in triesPerStep"
        :key="j + (i - 1) * triesPerStep"
        :data-index="j + (i - 1) * triesPerStep"
        ref="dots"
        :class="{ active: j + (i - 1) * triesPerStep <= tries }"
      />
      <IconGemini
        :class="['gemini', { active: 3 + (i - 1) * triesPerStep <= tries }]"
        v-if="i !== maxSteps"
      />
    </div>
  </div>
</template>

<script setup>
import { shallowRef } from 'vue'
import { useScoreStore } from '@/store'
import { storeToRefs } from 'pinia'
import { gsap } from '@/utils/gsap'
import IconGemini from './icons/IconGemini.vue'

const store = useScoreStore()
const { tries, triesPerStep, maxSteps } = storeToRefs(store)

const dots = shallowRef([])
const progress = shallowRef(null)
defineExpose({
  animateSet: async () => {
    gsap.set(progress.value, {
      y: progress.value.clientHeight + (160 / 3840) * window.innerWidth,
    })
  },
  animateIn: async () => {
    gsap.to(progress.value, {
      y: 0,
      duration: 0.6,
      delay: 0.6,
      ease: 'power2.out',
    })
  },
  animateOut: async () => {
    gsap.fromTo(
      progress.value,
      {
        y: 0,
      },
      {
        y: progress.value.clientHeight + (160 / 3840) * window.innerWidth,
        duration: 0.6,
        delay: 0,
        ease: 'power2.out',
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
  background-color: #2a2a2a;
  padding: px-to-vw(48, 4k);
  box-shadow:
    0 0 0 px-to-vw(5, 4k) rgb(0, 0, 0),
    px-to-vw(15, 4k) px-to-vw(20, 4k) rgb(0, 0, 0);
  border-radius: px-to-vw(24, 4k);
}

.group {
  display: flex;
  gap: px-to-vw(48, 4k);
  align-items: center;
}

.gemini {
  width: px-to-vw(100, 4k);
  height: auto;
  fill: $brandBlue;
  stroke: #000;
  stroke-width: px-to-vw(5, 4k);
  // filter: drop-shadow(px-to-vw(8, 4k) px-to-vw(10, 4k) rgb(0, 0, 0));
  paint-order: fill stroke;
  transition: transform 0.6s ease-in-out;

  &.active {
    transform: scale(1.1) rotate(360deg);
  }
}

.dot {
  width: px-to-vw(120, 4k);
  height: px-to-vw(120, 4k);
  background-color: #666666;
  border-radius: 50%;
  box-shadow:
    0 0 0 px-to-vw(5, 4k) rgb(0, 0, 0),
    px-to-vw(15, 4k) px-to-vw(20, 4k) rgb(0, 0, 0);

  &.active {
    background-color: #fff !important;
  }
}
</style>
