<template>
  <svg
    ref="backing"
    width="563"
    height="235"
    viewBox="0 0 563 235"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path
      d="M538 27.5C538 20.5964 532.404 15 525.5 15H47.5C40.5964 15 35 20.5964 35 27.5C35 34.4036 29.4036 40 22.5 40C15.5964 40 10 45.5964 10 52.5V197.5C10 204.404 15.5964 210 22.5 210C29.4036 210 35 215.596 35 222.5C35 229.404 40.5964 235 47.5 235H525.5C532.404 235 538 229.404 538 222.5C538 215.596 543.596 210 550.5 210C557.404 210 563 204.404 563 197.5V52.5C563 45.5964 557.404 40 550.5 40C543.596 40 538 34.4036 538 27.5Z"
      fill="black"
    />
    <path
      d="M515.5 1.5C521.575 1.5 526.5 6.42487 526.5 12.5C526.5 20.232 532.768 26.5 540.5 26.5C546.575 26.5 551.5 31.4249 551.5 37.5V182.5C551.5 188.575 546.575 193.5 540.5 193.5C532.768 193.5 526.5 199.768 526.5 207.5C526.5 213.575 521.575 218.5 515.5 218.5H37.5C31.4249 218.5 26.5 213.575 26.5 207.5C26.5 199.768 20.232 193.5 12.5 193.5C6.42487 193.5 1.5 188.575 1.5 182.5V37.5C1.5 31.4249 6.42487 26.5 12.5 26.5C20.232 26.5 26.5 20.232 26.5 12.5C26.5 6.42487 31.4249 1.5 37.5 1.5H515.5Z"
      fill="#34A853"
      stroke="black"
      stroke-width="3"
    />
  </svg>
</template>

<script setup>
import { ref } from 'vue'
import { gsap } from '@/utils/gsap'
const backing = ref(null)
defineExpose({
  animateSet: () => {
    gsap.set(backing.value, {
      scale: 0,
    })
  },
  animateIn: (delay) => {
    gsap.to(backing.value, {
      scale: 1,
      duration: 1,
      ease: 'power2.inOut',
      delay,
    })
  },
  animateOut: () => {
    gsap.to(backing.value, {
      scale: 0,
      duration: 1,
      ease: 'power2.inOut',
    })
  },
})
</script>
