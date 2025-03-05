<template>
  <div
    class="VBadge badge"
    :class="[variant, classes]"
    ref="badge"
  >
    <div
      class="inner"
      ref="inner"
    >
      <slot />
    </div>
  </div>
</template>

<script setup>
import { gsap } from '@/utils/gsap'
import { pxToVw } from '@/utils/px'
import { shallowRef } from 'vue'

const badge = shallowRef(null)
const inner = shallowRef(null)

defineProps({
  variant: {
    type: String,
    default: '',
  },
  classes: {
    type: String,
    default: '',
  },
})

defineExpose({
  animateSet: () => {
    gsap.set(badge.value, {
      clipPath: `inset(${badge.value.clientHeight / 2 + 1}px ${badge.value.clientWidth / 2 + 1}px round ${pxToVw(45)})`,
    })
  },
  animateIn: (delay = 0) => {
    gsap.to(badge.value, {
      clipPath: `inset(${pxToVw(-16)} ${pxToVw(-11)} round ${pxToVw(45)})`,
      duration: 0.65,
      ease: 'power2.out',
      delay: delay + 0.2,
    })
  },
  animateOut: (delay = 0) => {
    gsap.to(badge.value, {
      clipPath: `inset(${badge.value.clientHeight / 2 + 1}px ${badge.value.clientWidth / 2 + 1}px round ${pxToVw(45)})`,
      duration: 0.65,
      ease: 'power2.in',
      delay: delay,
    })
  },
})
</script>

<style lang="scss" scoped>
.badge {
  display: flex;
  background: $brandYellow;
  border-radius: px-to-vw(45, '4k');
  box-shadow:
    0 0 0 px-to-vw(6, '4k') #000,
    px-to-vw(6+5, '4k') px-to-vw(6+10, '4k') 0 0 #000;
  padding: px-to-vw(40, '4k') px-to-vw(60, '4k');
  overflow: hidden;

  &.red {
    background: $brandRed;
  }

  &.green {
    background: $brandGreen;
  }

  .inner {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: px-to-vw(20, '4k');
  }
}
</style>
