<template>
  <div
    class="VBadge badge"
    :class="[variant]"
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
import { shallowRef } from 'vue'

const badge = shallowRef(null)
const inner = shallowRef(null)

defineProps({
  variant: {
    type: String,
    default: '',
  },
})

defineExpose({
  animateSet: () => {
    gsap.set(badge.value, {
      scale: 0,
    })
    gsap.set(inner.value, {
      yPercent: 200,
    })
  },
  animateIn: (delay = 0) => {
    gsap.to(inner.value, {
      yPercent: 0,
      duration: 0.65,
      ease: 'power2.out',
      delay: delay + 0.2,
    })
    gsap.to(badge.value, {
      scale: 1,
      duration: 1,
      ease: 'power2.inOut',
      delay: delay,
    })
  },
  animateOut: (delay = 0) => {
    gsap.to(inner.value, {
      yPercent: -200,
      duration: 0.65,
      ease: 'power2.in',
      delay: delay,
    })
    gsap.to(badge.value, {
      scale: 0,
      duration: 1,
      ease: 'power2.inOut',
      delay: delay + 0.1,
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
