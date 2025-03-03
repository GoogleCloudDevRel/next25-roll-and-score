<template>
  <div class="intro">
    <VText
      ref="pre"
      class="pre"
      variant="tv-bold-96"
      text="AI POWERED"
    />
    <div class="sign">
      <svg
        ref="svg"
        viewBox="0 0 2520 671"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M2420 80.2236C2420 52.8855 2397.84 30.7236 2370.5 30.7236H169.5C142.162 30.7236 120 52.8855 120 80.2236C120 107.562 97.5894 129.724 70.2513 129.724C42.637 129.724 20 152.109 20 179.724V519.724C20 547.338 42.3858 569.724 70 569.724C97.6142 569.724 120 592.358 120 619.972C120 647.863 142.61 670.724 170.5 670.724H2369.5C2397.39 670.724 2420 647.863 2420 619.972C2420 592.358 2442.39 569.724 2470 569.724C2497.61 569.724 2520 547.338 2520 519.724V179.724C2520 152.109 2497.36 129.724 2469.75 129.724C2442.41 129.724 2420 107.562 2420 80.2236Z"
          fill="black"
        />
        <path
          d="M149.5 3.72363H2350.5C2376.18 3.72363 2397 24.5424 2397 50.2236C2397 79.2381 2420.77 102.724 2449.75 102.724C2475.73 102.724 2497 123.786 2497 149.724V489.724C2497 515.681 2475.96 536.724 2450 536.724C2420.71 536.724 2397 560.721 2397 589.972C2397 616.225 2375.71 637.724 2349.5 637.724H150.5C124.286 637.724 103 616.225 103 589.972C103 560.721 79.2904 536.724 50 536.724C24.0426 536.724 3 515.681 3 489.724V149.724C3 123.786 24.2743 102.724 50.2513 102.724C79.2266 102.724 103 79.2381 103 50.2236C103 24.5424 123.819 3.72363 149.5 3.72363Z"
          fill="#4285F4"
          stroke="black"
          stroke-width="6"
        />
      </svg>
      <div class="inner">
        <VText
          ref="text"
          variant="tv-bold-420"
          text="Roll & Score"
          split-type="chars"
          animate-by="chars"
        />
      </div>
    </div>
    <VText
      ref="sub"
      class="sub"
      variant="tv-bold-96"
      text="Elevate Your Gameplay with Gemini 2.0"
    />
  </div>
</template>

<script setup>
import { shallowRef } from 'vue'
import VText from './VText.vue'
import { gsap } from '@/utils/gsap'

const svg = shallowRef(null)
const pre = shallowRef(null)
const text = shallowRef(null)
const sub = shallowRef(null)

console.log('rerender')

defineExpose({
  animateSet: async () => {
    await Promise.all([
      pre.value.prepare(),
      text.value.prepare(true, { yPercent: 130 }),
      sub.value.prepare(),
    ])
    gsap.set(svg.value, {
      scale: 0,
    })
  },
  animateIn: async () => {
    pre.value.animateIn()
    text.value.animateIn(0.8, {
      ease: 'elastic.out(1,0.5)',
      duration: 1.2,
      stagger: 0.075,
      yPercent: 130,
    })
    sub.value.animateIn(1.5)
    await gsap.to(svg.value, {
      scale: 1,
      duration: 2.5,
      ease: 'elastic.out(1,0.5)',
      delay: 0.6,
    })
  },
  animateOut: async () => {
    pre.value.animateOut(),
      text.value.animateOut(0, { yPercent: -130 }),
      sub.value.animateOut(),
      await gsap.to(svg.value, {
        scale: 0,
        duration: 1.5,
        ease: 'power2.in',
      })
  },
})
</script>

<style lang="scss" scoped>
.intro {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
}

.sign {
  color: $brandYellow;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;

  .inner {
    padding: px-to-vw(115, 4k);
    overflow: hidden;
  }

  svg {
    width: 100%;
    height: auto;
    position: absolute;
    stroke-width: px-to-vw(6, 4k);
    stroke: #000;
  }

  & :global(.pre) {
    margin-bottom: px-to-vw(80, 4k);
  }
  & :global(.sub) {
    margin-top: px-to-vw(115, 4k);
  }
}
</style>
