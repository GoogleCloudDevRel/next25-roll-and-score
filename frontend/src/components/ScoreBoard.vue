<template>
  <div
    :class="{
      scoreboard: true,
      [textVariant ? 'text-' + textVariant : '']: true,
      [useColors ? 'use-colors' : '']: true,
      singleDigit,
      noBackground,
      [scrollerVariant ? 'scroller-' + scrollerVariant : '']: true,
    }"
  >
    <div
      class="scroller"
      v-for="s in singleDigit ? 1 : 4"
      :key="s"
      ref="scrollers"
    >
      <div
        v-if="!noBackground"
        class="background"
      />
      <div class="clip">
        <div
          class="inner"
          :ref="setInner"
        >
          <div
            v-for="n in 20"
            :key="n"
          >
            {{ (n - 1) % 10 }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { gsap } from '@/utils/gsap'
import { onMounted, ref, watch } from 'vue'

const prevValue = ref(0)
const inners = ref([])
const scrollers = ref([])

const props = defineProps({
  value: {
    type: Number,
    default: 0,
  },
  textVariant: {
    type: String,
    default: 'tv-bold-160',
  },
  useColors: {
    type: Boolean,
    default: true,
  },
  singleDigit: {
    type: Boolean,
    default: false,
  },
  noBackground: {
    type: Boolean,
    default: false,
  },
  scrollerVariant: {
    type: String,
    default: '',
  },
  immediate: {
    type: Boolean,
    default: true,
  },
})

const setInner = (el) => {
  if (el && !inners.value.includes(el)) {
    inners.value.push(el)
  }
}

async function goTo(n, prev = 0, force = false) {
  const pad = props.singleDigit ? 0 : 4

  const prevChars = prev.toString().padStart(pad, '0').split('')
  let chars = n.toString().padStart(pad, '0').split('')
  chars.forEach((char, i) => {
    let num = parseInt(char)
    let prevNum = parseInt(prevChars[i])
    let selector = props.singleDigit ? inners.value[0] : inners.value[i]

    if (force) {
      gsap.set(selector, {
        yPercent: num === 0 ? 100 : -num * 100,
      })
      return
    }

    if (num < prevNum) {
      const diff = 10 - prevNum + num + prevNum
      gsap.to(selector, {
        yPercent: -diff * 100,
        duration: 1,
        ease: 'power2.inOut',
        onComplete: () => {
          gsap.set(selector, {
            yPercent: -num * 100,
          })
        },
      })
    } else {
      gsap.to(selector, {
        yPercent: -num * 100,
        duration: 1,
        ease: 'power2.inOut',
      })
    }
  })
}

const animateSet = () => {
  gsap.set(scrollers.value, {
    clipPath: `inset(${scrollers.value[0].clientHeight / 2 + 1}px ${scrollers.value[0].clientWidth / 2 + 1}px round ${(scrollers.value[0].clientHeight / 1.4) * 0.1}px)`,
  })
  goTo(0, 0, true)
}

const animateIn = async (delay) => {
  const shadowY = (scrollers.value[0].clientHeight / 1.4) * 0.07
  const shadowX = (scrollers.value[0].clientHeight / 1.4) * 0.05
  gsap.to(scrollers.value, {
    clipPath: `inset(${-shadowY}px ${-shadowX}px round ${(scrollers.value[0].clientHeight / 1.4) * 0.1}px)`,
    duration: 1,
    ease: 'power2.out',
    delay,
    stagger: 0.1,
  })
  gsap.delayedCall(delay, () => {
    goTo(props.value, prevValue.value)
    prevValue.value = props.value
  })
}

const animateOut = () => {
  gsap.to(scrollers.value, {
    clipPath: `inset(${scrollers.value[0].clientHeight / 2 + 1}px ${scrollers.value[0].clientWidth / 2 + 1}px round ${(scrollers.value[0].clientHeight / 1.4) * 0.1}px)`,
    duration: 1,
    ease: 'power2.inOut',
  })
  gsap.to(inners.value, {
    yPercent: -900,
    duration: 1,
    ease: 'power2.in',
  })
  prevValue.value = 0
}

onMounted(() => {
  watch(
    () => props.value,
    () => {
      goTo(props.value, prevValue.value)
      prevValue.value = props.value
    },
    { immediate: props.immediate },
  )
})

defineExpose({
  goTo,
  animateSet,
  animateIn,
  animateOut,
})
</script>

<style lang="scss" scoped>
.scoreboard {
  display: flex;
  gap: max(0.1em, 6px);
}

.scroller {
  --height: 1.4em;
  position: relative;
  height: var(--height);
  line-height: 1 !important;
  color: $brandYellow;

  .clip {
    overflow: hidden;
    padding: 0 0.225em;
  }

  .background {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    border-radius: 0.1em;
    background: $brandBlue;
    box-shadow:
      0 0 0 max(2px, 0.01em) #000,
      0.05em 0.07em 0 #000;
  }

  .use-colors & {
    color: #fff;

    &:nth-of-type(2) .background {
      background: $brandRed;
    }
    &:nth-of-type(3) .background {
      background: $brandGreen;
    }
    &:nth-of-type(4) .background {
      background: $brandYellow;
    }
  }
}

.noBackground {
  --height: 1em;
  .clip {
    padding: 0;
  }
}

.singleDigit {
  .background {
    background: #303239;
  }
}

.scroller-yellow {
  .background {
    background: $brandYellow;
  }
}

.inner {
  height: var(--height);
  display: flex;
  flex-direction: column;
  text-align: center;

  & > * {
    width: 100%;
    height: var(--height);
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-left: -0.025em;
  }
}
</style>
