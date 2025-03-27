<template>
  <div
    class="imageGridItem"
    ref="imageGridItem"
  >
    <div
      class="imageGridItem__image"
      :style="{ backgroundImage: `url(${image})` }"
      role="img"
      ref="imageDiv"
      :aria-label="'Image Grid Item'"
    ></div>
    <div
      v-if="caption"
      class="imageGridItem__text text-bold-40"
      ref="captionDiv"
    >
      <IconBase
        class="imageGridItem__icon"
        variant="gemini"
      />
      <span>{{ caption }}</span>
    </div>
  </div>
</template>

<script setup>
import IconBase from '@/components/IconBase.vue'
import gsap from 'gsap'
import { ref } from 'vue'

const imageGridItem = ref(null)
const imageDiv = ref(null)
const captionDiv = ref(null)

defineProps({
  image: {
    type: String,
    required: true,
  },
  caption: {
    type: String,
    required: false,
  },
})

const animateSet = () => {
  // gsap.set(imageGridItem.value, {

  // })
  gsap.set(imageDiv.value, {
    opacity: 0,
    clipPath: 'inset(30% 30% round 26.1%)',
  })
  gsap.set(captionDiv.value, {
    opacity: 0,
    y: '5vh',
  })
}

const animateIn = (delay) => {
  animateSet()
  gsap.to(imageDiv.value, {
    opacity: 1,
    clipPath: 'inset(0% 0% round 6.1%)',
    duration: 0.8,
    ease: 'power2.out',
    delay,
  })
  gsap.to(captionDiv.value, {
    opacity: 1,
    y: 0,
    duration: 0.5,
    ease: 'power2.out',
    delay: delay - 0.05,
  })
}

const animateOut = (delay) => {
  gsap.to(captionDiv.value, {
    opacity: 0,
    duration: 0.3,
    ease: 'power2.out',
    delay: delay - 0.05,
  })
  gsap.to(imageDiv.value, {
    clipPath: 'inset(30% 30% round 6.1%)',
    duration: 0.3,
    opacity: 0,
    ease: 'power2.out',
    delay,
  })
}

defineExpose({
  animateIn,
  animateOut,
})
</script>

<style lang="scss">
.imageGridItem {
  position: relative;
  text-align: center;

  &__image {
    height: 45vh;
    aspect-ratio: 1 / 1;
    background-size: cover;
    background-position: center center;
    background-repeat: no-repeat;
    margin-bottom: 2.39vh;
    clip-path: inset(0% 0% round 6.1%);
    opacity: 0;
  }

  &__icon {
    color: $brandGreen;
    height: 1.2em;
    width: 1.2em;
    svg {
      width: 100% !important;
      height: 100% !important;
    }
  }

  &__text {
    opacity: 0;
    display: inline-flex;
    flex-direction: row;
    align-items: center;
    color: $darkmode;
    font-size: 1.473vh !important;
    line-height: 1 !important;
    padding: 0.7em 1.2em;
    border-radius: 2.5em;
    position: relative;
    background: #0f2f1899;
    backdrop-filter: blur(100px);
    gap: 0.6em;

    @include gradient-border((45deg, #d6ffe1, #809987), 1px);

    &:before {
      border-radius: 2.5em;
    }
  }
}
</style>
