<template>
  <div
    class="imageGrid"
    ref="gridContainer"
  >
    <div
      class="imageGrid__wrapper"
      ref="gridWrapper"
    >
      <!-- Original items -->
      <ImageGridItem
        v-for="(item, index) in items"
        :key="`original-${index}`"
        :image="item.image"
        :caption="item.caption"
        ref="gridItems"
      />
      <!-- Cloned items for infinite scroll -->
      <ImageGridItem
        v-for="(item, index) in items"
        :key="`clone-${index}`"
        :image="item.image"
        :caption="item.caption"
        ref="gridItems"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import gsap from 'gsap'
import ImageGridItem from './ImageGridItem.vue'

defineProps({
  items: {
    type: Array,
    required: true,
    validator: (value) => {
      return value.every((item) => 'image' in item && 'caption' in item)
    },
  },
})

const gridContainer = ref(null)
const gridWrapper = ref(null)
const gridItems = ref([])
let animation = null
let wrapperWidth = 0

onMounted(() => {
  initInfiniteScroll()
})

const animateIn = () => {
  gridItems.value.forEach((item, index) => {
    item.animateIn(index * 0.1)
  })
}

const animateOut = () => {
  gridItems.value.forEach((item, index) => {
    item.animateOut(index * 0.05)
  })
}

const initInfiniteScroll = () => {
  // Get the width of a single set of items
  wrapperWidth = gridWrapper.value.offsetWidth / 2

  // Set initial position
  gsap.set(gridWrapper.value, {
    x: 0,
  })

  // Create seamless infinite scroll
  animation = gsap.timeline({ repeat: -1 }).to(gridWrapper.value, {
    x: `-${wrapperWidth}`,
    duration: 20,
    ease: 'none',
    onComplete: () => {
      // Immediately reset position without visual jump
      gsap.set(gridWrapper.value, { x: 0 })
    },
  })
}

onUnmounted(() => {
  if (animation) {
    animation.kill()
  }
})

defineExpose({
  animateIn,
  animateOut,
})
</script>

<style lang="scss" scoped>
.imageGrid {
  width: 100%;
  overflow: hidden;
  position: relative;

  &__wrapper {
    display: flex;
    gap: 2.39vh;
    overflow: hidden;
  }
}
</style>
