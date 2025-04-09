<template>
  <div class="splash-gallery-container">
    <div class="splash-gallery-title">
      <VText
        forceSet
        ref="titleRef"
        :text="title"
        variant="bold-128"
        class="title"
        gradient
      />
      <VText
        forceSet
        ref="subTitleRef"
        :text="subTitle"
        variant="bold-32"
        class="sub-title"
        gradient
      />
    </div>
    <div class="splash-gallery">
      <SplashGalleryItem
        v-for="(image, index) in images"
        ref="galleryItemsRef"
        :key="index"
        :src="image.src"
        :alt="image.alt"
        :position="image.position"
        :caption="image.caption"
        :id="image.id"
        @item-done="handleItemDone"
      />
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import SplashGalleryItem from './SplashGalleryItem.vue'
import VText from '@/components/VText.vue'
import gsap from 'gsap'
const images = ref([])

const count = ref(0)
const intervalId = ref(null)
const isVisible = ref(true)
const titleRef = ref(null)
const subTitleRef = ref(null)
const galleryItemsRef = ref([])
const props = defineProps({
  title: {
    type: String,
    required: false,
    default: 'Kayak to AI',
  },
  subTitle: {
    type: String,
    required: false,
    default: 'Let Gemini guide your adventures',
  },
  imageContent: {
    type: Array,
    required: true,
    default: () => [
      {
        src: 'https://fastly.picsum.photos/id/813/300/300.jpg?hmac=P1QaCX9HgZK2OE_XcRiYdFI9wkhiSmgYKor-9yDp00c',
        alt: 'Image 1',
        caption: 'Caption 1',
        position: {
          left: '10%',
          top: '10%',
          right: 'auto',
          bottom: 'auto',
        },
      },
      {
        src: 'https://fastly.picsum.photos/id/960/300/300.jpg?hmac=33HCKWbjLrPghX-xdgDHytx4nbiWfmdQdI-Fwsgj_00',
        alt: 'Image 2',
        caption: 'Caption 2',
        position: {
          left: 'auto',
          top: '10%',
          right: '10%',
          bottom: 'auto',
        },
      },
      {
        src: 'https://fastly.picsum.photos/id/813/300/300.jpg?hmac=P1QaCX9HgZK2OE_XcRiYdFI9wkhiSmgYKor-9yDp00c',
        alt: 'Image 3',
        caption: 'Caption 3 testing long caption',
        position: {
          left: '10%',
          right: 'auto',
          top: 'auto',
          bottom: '10%',
        },
      },
      {
        src: 'https://fastly.picsum.photos/id/960/300/300.jpg?hmac=33HCKWbjLrPghX-xdgDHytx4nbiWfmdQdI-Fwsgj_00',
        alt: 'Image 4',
        caption: 'Caption 4',
        position: {
          left: 'auto',
          top: 'auto',
          right: '10%',
          bottom: '0%',
        },
      },
      {
        src: 'https://fastly.picsum.photos/id/813/300/300.jpg?hmac=P1QaCX9HgZK2OE_XcRiYdFI9wkhiSmgYKor-9yDp00c',
        alt: 'Image 5',
        caption: 'Caption 5',
        position: {
          left: 'auto',
          top: 'auto',
          right: '30%',
          bottom: '10%',
        },
      },
      {
        src: 'https://fastly.picsum.photos/id/960/300/300.jpg?hmac=33HCKWbjLrPghX-xdgDHytx4nbiWfmdQdI-Fwsgj_00',
        alt: 'Image 6',
        caption: 'Caption 6',
        position: {
          top: '0%',
          left: '30%',
          right: 'auto',
          bottom: 'auto',
        },
      },
    ],
  },
})

const imageContentRef = ref(props.imageContent)

async function spawnImage() {
  if (count.value >= imageContentRef.value.length) {
    count.value = 0
  }

  const obj = {
    src: imageContentRef.value[count.value].src,
    position: imageContentRef.value[count.value].position,
    id: count.value,
    caption: imageContentRef.value[count.value].caption,
  }
  images.value.push(obj)
  count.value++
}

function startInterval() {
  if (!intervalId.value) {
    spawnImage()
    intervalId.value = setInterval(spawnImage, 1500)
  }
}

function stopInterval() {
  if (intervalId.value) {
    clearInterval(intervalId.value)
    intervalId.value = null
  }
}

function handleVisibilityChange() {
  if (document.hidden) {
    isVisible.value = false
    stopInterval()
  } else {
    isVisible.value = true
    startInterval()
  }
}

function handleItemDone(id) {
  console.log('item done', id)
}

function animateIn() {
  gsap.to(titleRef.value.$el, {
    opacity: 1,
    duration: 3,
    z: 0,
    ease: 'power2.out',
  })
  gsap.to(subTitleRef.value.$el, {
    opacity: 1,
    duration: 3,
    delay: 0.25,
    z: 0,
    ease: 'power2.out',
  })

  startInterval()
  document.addEventListener('visibilitychange', handleVisibilityChange)
}

function animateOut() {
  gsap.to(titleRef.value.$el, {
    opacity: 0,
    duration: 1,
    z: -100,
    ease: 'power2.out',
  })
  gsap.to(subTitleRef.value.$el, {
    opacity: 0,
    duration: 1,
    z: -100,
    ease: 'power2.out',
  })
  galleryItemsRef.value.forEach((item) => {
    item.animateOut()
  })
  // animate out all the
  stopInterval()
}

defineExpose({
  animateIn,
  animateOut,
})

onMounted(() => {
  imageContentRef.value = props.imageContent
  //animateIn()
})

onUnmounted(() => {
  stopInterval()
  document.removeEventListener('visibilitychange', handleVisibilityChange)
})
</script>

<style lang="scss" scoped>
.splash-gallery-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 1000;
}
.splash-gallery {
  position: relative;
  width: 100vw;
  height: 100vh;
  perspective: 600px;
}
.splash-gallery-title {
  position: absolute;
  width: 100vw;
  height: 100vh;
  left: 0;
  top: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  perspective: 600px;
  .title,
  .sub-title {
    line-height: 1.2;
    transform-style: preserve-3d;
    transform: translate3d(0, 0, -100px);
    opacity: 0;
  }
  .sub-title {
    margin-top: 0.5vw;
  }
}
</style>
