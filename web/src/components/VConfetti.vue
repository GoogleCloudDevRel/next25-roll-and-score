<template>
  <div
    class="confetti"
    ref="confettiContainer"
  >
    <div
      v-for="i in 100"
      :key="i"
      class="confetti-item"
      ref="confettiItems"
    >
      <IconBase variant="gemini" />
    </div>
  </div>
</template>

<script setup>
import IconBase from './IconBase.vue'
import { gsap } from '@/utils/gsap'
import { ref, onMounted } from 'vue'

const confettiContainer = ref(null)
const confettiItems = ref([])

function getRandomBetween(min, max) {
  return Math.random() * (max - min) + min
}

function animateSet() {
  if (!confettiItems.value.length) return

  // Reset all confetti items to the bottom center (starting point for explosion)
  confettiItems.value.forEach((item) => {
    gsap.set(item, {
      x: getRandomBetween(window.innerWidth / 2 - 100, window.innerWidth / 2 + 100), // Tighter cluster at center
      y: 240,
      rotation: getRandomBetween(0, 360),
      scale: getRandomBetween(0.3, 1),
      opacity: 0,
    })
  })
}

function animateIn() {
  if (!confettiItems.value.length) return

  // First make all items visible
  confettiItems.value.forEach((item) => {
    gsap.set(item, { opacity: 1 })
  })

  // Animate each confetti item in an explosion pattern
  confettiItems.value.forEach((item, index) => {
    // Create a timeline for each confetti piece
    const tl = gsap.timeline()

    // Calculate spread direction - divide the items across the full 360 degrees
    // with some randomization
    const angle = (index / confettiItems.value.length) * -180
    const radians = angle * (Math.PI / 180)

    // Calculate distance from center - some go further than others
    const distance = getRandomBetween(
      window.innerWidth / 2 - window.innerWidth / 4,
      window.innerWidth / 2 + window.innerWidth / 4,
    )

    // Calculate target position based on angle and distance
    const targetX = Math.cos(radians) * distance + window.innerWidth / 2
    const targetY = Math.sin(radians) * distance - window.innerHeight / 2 // Offset to make more upward initially

    // Phase 1: Explosion - items fly outward in all directions
    tl.to(item, {
      x: targetX,
      y: targetY,
      rotation: getRandomBetween(-360, 360),
      duration: getRandomBetween(1.5, 2.5),
      delay: getRandomBetween(0, 0.3),
      ease: 'power2.out',
    })

      // Phase 2: Fall down with gravity effect
      .to(item, {
        y: window.innerHeight + 100, // Ensure it goes below the viewport
        x: `+=${getRandomBetween(-200, 200)}`, // Drift while falling
        rotation: `+=${getRandomBetween(-720, 720)}`,
        duration: getRandomBetween(2, 3.5),
        ease: 'power1.in', // Ease-in for gravity effect
        onComplete: () => {
          // Fade out at the end of animation
          gsap.to(item, {
            opacity: 0,
            duration: 0.3,
          })
        },
      })
  })
}

onMounted(() => {
  // Initialize positions but don't animate yet
  animateSet()
})

defineExpose({
  animateSet,
  animateIn,
})
</script>

<style lang="scss" scoped>
.confetti {
  position: absolute;
  width: 100%;
  height: 100%;
  overflow: hidden;
  pointer-events: none;
  z-index: 100;
}

.confetti-item {
  position: absolute;
  bottom: 0;
  will-change: transform;
}

.confetti-item :deep(svg) {
  width: px-to-vw(240, 4k);
  height: px-to-vw(240, 4k);
  fill: var(--color, currentColor);
  vector-effect: non-scaling-stroke;
}

.confetti-item:nth-child(5n) :deep(svg) {
  --color: #{$brandRed}; /* Red */
}

.confetti-item:nth-child(5n + 1) :deep(svg) {
  --color: #{$brandGreen}; /* Green */
}

.confetti-item:nth-child(5n + 2) :deep(svg) {
  --color: #{$brandBlue}; /* Blue */
}

.confetti-item:nth-child(5n + 3) :deep(svg) {
  --color: #{$brandYellow}; /* Yellow */
}
</style>
