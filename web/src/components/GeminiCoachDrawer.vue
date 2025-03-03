<template>
  <div class="geminicoachdrawer">
    <div
      class="bg"
      ref="bg"
    ></div>
    <div class="badgeTop">
      <VBadge ref="badge">
        <IconBase variant="gemini" />
        <VText
          text="GEMINI COACH"
          variant="tv-bold-72"
        />
      </VBadge>
    </div>
    <VText
      ref="textContent"
      :text="text"
      variant="tv-bold-160"
      animateBy="lines"
    />
  </div>
</template>

<script setup>
import { shallowRef } from 'vue'
import IconBase from './IconBase.vue'
import VBadge from './VBadge.vue'
import VText from './VText.vue'
import { gsap } from '@/utils/gsap'

const badge = shallowRef(null)
const textContent = shallowRef(null)
const bg = shallowRef(null)

defineProps({
  text: {
    type: String,
    default: 'Great job! Now approach the staff to collect to your comprehensive analysis!',
  },
})

defineExpose({
  animateSet: async () => {
    await textContent.value.prepare()
    badge.value?.animateSet()
    gsap.set(bg.value, {
      scaleY: 0,
      transformOrigin: 'bottom',
    })
  },
  animateIn: () => {
    textContent.value.animateIn(0.35)
    badge.value?.animateIn()
    gsap.to(bg.value, {
      scaleY: 1,
      duration: 1,
      ease: 'power2.inOut',
    })
  },
  animateOut: () => {
    textContent.value.animateOut(0)
    badge.value.animateOut()
    gsap.to(bg.value, {
      scaleY: 0,
      duration: 1,
      ease: 'power2.inOut',
      delay: textContent.value.splitText?.lines.length * 0.1 || 0,
    })
  },
})
</script>

<style lang="scss" scoped>
.geminicoachdrawer {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 50vh;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: px-to-vw(200, 4k) px-to-vw(600, 4k);
}

.bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: $brandBlue;
  box-shadow: 0 0 0 px-to-vw(6, 4k) #000;
}

.badgeTop {
  position: absolute;
  z-index: 1;
  bottom: 100%;
  transform: translateY(50%);
}
</style>
