<template>
  <div
    class="geminicoach"
    ref="content"
  >
    <VText
      ref="textContent"
      variant="tv-bold-160"
      animateBy="lines"
      :text="text"
    />
    <div
      class="badgeTop"
      v-if="showBadge"
    >
      <VBadge ref="badge">
        <IconBase variant="gemini" />
        <VText
          text="GEMINI COACH"
          variant="tv-bold-72"
        />
      </VBadge>
    </div>
    <div
      class="background"
      ref="bg"
    >
      <svg
        class="svgTop"
        ref="svgTop"
        viewBox="0 0 2806 153"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M2650.33 3H155.672C128.117 3 105.779 25.3379 105.779 52.8931C105.779 80.4483 83.4414 102.786 55.8862 102.786C28.3311 102.786 5.99316 125.124 5.99316 152.679L2800.01 152.679C2800.01 125.124 2777.67 102.786 2750.11 102.786C2722.56 102.786 2700.22 80.4483 2700.22 52.8931C2700.22 25.3379 2677.88 3 2650.33 3Z"
          :fill="bgColor"
        />
      </svg>
      <svg
        ref="svg"
        class="box"
        viewBox="0 0 2812 900"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        preserveAspectRatio="none"
      >
        <path
          d="M6 0H2806V900H6V0Z"
          :fill="bgColor"
        />
      </svg>
      <svg
        class="svgBottom"
        viewBox="0 0 2806 154"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M155.673 150.321H2650.33C2677.88 150.321 2700.22 127.936 2700.22 100.321C2700.22 72.7071 2722.56 50.3213 2750.11 50.3213C2777.67 50.3213 2800.01 27.9355 2800.01 0.321289L5.99365 0.321304C5.99365 27.9355 28.3315 50.3213 55.8867 50.3213C83.442 50.3213 105.78 72.7071 105.78 100.321C105.78 127.936 128.118 150.321 155.673 150.321Z"
          :fill="bgColor"
        />
      </svg>
    </div>
  </div>
</template>

<script setup>
import { gsap } from '@/utils/gsap'
import VText from './VText.vue'
import { nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import VBadge from './VBadge.vue'
import IconBase from './IconBase.vue'

const badge = ref(null)
const svg = ref(null)
const svgTop = ref(null)
const bg = ref(null)
const content = ref(null)
const textContent = ref(null)

const props = defineProps({
  text: {
    type: String,
    required: true,
  },
  showBadge: {
    type: Boolean,
    default: true,
  },
  bgColor: {
    type: String,
    default: '#4285F4',
  },
  immediate: {
    type: Boolean,
    default: true,
  },
})

function prepare() {
  const height = content.value.clientHeight - svgTop.value.clientHeight * 2
  svg.value.style.setProperty('height', `${height}px`)
}

watch(
  () => props.text,
  async () => {
    await nextTick()
    setTimeout(prepare, 60)
  },
  { immediate: props.immediate },
)

onMounted(() => {
  window.addEventListener('resize', prepare)
})

onUnmounted(() => {
  window.removeEventListener('resize', prepare)
})

defineExpose({
  animateSet: async () => {
    await textContent.value.prepare()
    badge.value?.animateSet()
    prepare()
    gsap.set(bg.value, {
      scale: 0,
    })
  },
  animateIn: () => {
    textContent.value.animateIn(0.35)
    badge.value?.animateIn()
    gsap.to(bg.value, {
      scale: 1,
      duration: 1,
      ease: 'power2.inOut',
    })
  },
  animateOut: () => {
    textContent.value.animateOut(0)
    badge.value?.animateOut()
    console.log(textContent.value.splitText)
    gsap.to(bg.value, {
      scale: 0,
      duration: 1,
      ease: 'power2.inOut',
      delay: textContent.value.splitText?.lines.length * 0.1 || 0,
    })
  },
})
</script>

<style lang="scss" scoped>
.geminicoach {
  position: relative;
  width: px-to-vw(2820, '4k');
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: px-to-vw(100) px-to-vw(200);
  z-index: 0;
}

svg {
  display: block;
}

.background {
  position: absolute;
  width: 100%;
  height: auto;
  z-index: -1;
  display: flex;
  flex-direction: column;
  align-items: center;
  filter: drop-shadow(px-to-vw(0, 4k) px-to-vw(2, 4k) #000000)
    drop-shadow(px-to-vw(0, 4k) px-to-vw(-2, 4k) #000000)
    drop-shadow(px-to-vw(2, 4k) px-to-vw(0, 4k) #000000)
    drop-shadow(px-to-vw(-2, 4k) px-to-vw(0, 4k) #000000)
    drop-shadow(px-to-vw(20, 4k) px-to-vw(30, 4k) #000);
}

.shadow {
  margin-top: px-to-vw(20, 4k);
  margin-left: px-to-vw(20, 4k);
  z-index: -2;
}

.svgTop {
  position: absolute;
  bottom: calc(100% - 3px);
}

.svgBottom {
  position: absolute;
  top: calc(100% - 3px);
  z-index: -1;
}

.box {
  width: 100%;
}

.badgeTop {
  position: absolute;
  z-index: 1;
  bottom: 100%;
  transform: translateY(50%);
}
</style>
