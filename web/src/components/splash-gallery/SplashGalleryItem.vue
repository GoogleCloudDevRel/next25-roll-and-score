<template>
  <div
    ref="imageContainer"
    class="splash-gallery-item"
  >
    <VCaption
      ref="captionRef"
      :caption="'testing testing testing'"
    />
    <div
      ref="imageInner"
      class="splash-gallery-item__inner"
    >
      <img
        ref="image"
        :src="src"
      />
    </div>
  </div>
</template>

<script setup>
import gsap from 'gsap'
import { onMounted, ref, defineExpose } from 'vue'
import VCaption from '@/components/splash-gallery/VCaption.vue'

const image = ref(null)
const imageContainer = ref(null)
const imageInner = ref(null)
const captionRef = ref(null)
const tlRef = gsap.timeline()
onMounted(() => {
  // set style of image
  imageContainer.value.style.left = `${props.position.left}`
  imageContainer.value.style.top = `${props.position.top}`
  imageContainer.value.style.right = `${props.position.right}`
  imageContainer.value.style.bottom = `${props.position.bottom}`

  if (props.animate) {
    initAnimate()
  }
})
function animateIn() {
  captionRef.value.animateIn()
}

function animateOut() {
  if (tlRef.value) {
    tlRef.value.kill()
  }
  gsap.to(imageContainer.value, {
    z: imageContainer.value.style.z + 500,
    opacity: 0,
    duration: 1,
  })
}

defineExpose({
  animateIn,
  animateOut,
})

function initAnimate() {
  const x = props.position.left === 'auto' ? -Math.random() * 50 : Math.random() * 50
  const y = props.position.top === 'auto' ? -Math.random() * 50 : Math.random() * 50

  const tl = gsap.timeline({
    defaults: {
      ease: 'power1.out',
    },
    onComplete: () => {
      // remove this component from the parent
      imageContainer.value.remove()
    },
  })

  tlRef.value = tl

  tl.set(imageContainer.value, {
    x: `${x}%`,
    y: `${y}%`,
    z: -300,
  })
    .set(imageInner.value, {
      scale: 0,
    })
    .set(image.value, {
      scale: 4,
    })
    .to(
      imageInner.value,
      {
        scale: 1,
        duration: 2,
        ease: 'power1.out',
      },
      '<',
    )
    .to(
      image.value,
      {
        scale: 1,
        duration: 2,
        ease: 'power1.out',
        onStart: () => {
          setTimeout(() => {
            captionRef.value.animateIn()
          }, 1500)
        },
      },
      '<',
    )
    .to(
      imageContainer.value,
      {
        z: 50,
        duration: 10,
      },
      '<',
    )
    .to(
      image.value,
      {
        scale: 1.5,
        duration: 15,
        delay: 2,
      },
      '<',
    )
    .to(
      imageContainer.value,
      {
        opacity: 0,
        duration: 3,
        delay: 6,
      },
      '<',
    )
}

const props = defineProps({
  src: {
    type: String,
    required: true,
  },
  position: {
    type: Object,
    required: true,
  },
  id: {
    type: Number,
    required: true,
  },
  animate: {
    type: Boolean,
    required: false,
    default: true,
  },
  caption: {
    type: String,
    required: false,
    default: 'Testing',
  },
})
</script>

<style lang="scss" scoped>
.splash-gallery-item {
  position: absolute;
  top: 0;
  left: 0;
  transform-style: preserve-3d;

  @include fluid(
    'width',
    (
      xxl: 200px,
      fourk: 624px,
    )
  );

  @include fluid(
    'height',
    (
      xxl: 200px,
      fourk: 624px,
    )
  );

  @include fluid(
    'border-radius',
    (
      xxl: 10px,
      fourk: 32px,
    )
  );

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transform-origin: center;
  }

  &__inner {
    width: 100%;
    height: 100%;
    transform-origin: center;
    overflow: hidden;
    border-radius: inherit;
  }
  .vcaption {
    position: absolute;
    top: 40%;
    right: 0;
    transform: translateX(50%, -50%);
    z-index: 100;
  }
}
</style>
