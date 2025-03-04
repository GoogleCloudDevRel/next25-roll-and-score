<template>
  <div
    :class="['VText', variant ? `text-${variant}` : '', { gradient: gradient }, { center: center }]"
    ref="el"
  >
    {{ innerText }}
  </div>
</template>

<script setup>
import SplitText from '@activetheory/split-text'
import { isFontReady } from '@activetheory/split-text'
import { gsap, waitUntil } from '@/utils/gsap'
import { onMounted, ref, onUnmounted, watch, shallowRef, nextTick } from 'vue'

const props = defineProps({
  text: String,
  variant: String,
  splitType: {
    type: String,
    default: 'words, lines',
  },
  animateBy: {
    type: String,
    default: 'words',
  },
  type: {
    type: String,
  },
  useBalance: {
    type: Boolean,
    default: true,
  },
  gradient: {
    type: Boolean,
    default: false,
  },
  balanceRatio: {
    type: Number,
    default: 1,
  },
  forceSet: {
    type: Boolean,
    default: false,
  },
  icon: {
    type: String,
    default: null,
  },
  center: {
    type: Boolean,
    default: false,
  },
})

const el = ref(null)
const splitText = shallowRef(null)
const text = String(props.text)
const innerText = shallowRef(text)
const prepared = shallowRef(false)
const isPreparing = shallowRef(false)
const isAnimated = shallowRef(false)

let splitType = props.splitType || 'words, lines'

const handleGradient = () => {
  if (props.gradient) {
    const lines = splitText.value.lines
    lines.forEach((line) => {
      line.__words.forEach((word) => {
        gsap.set(word, {
          backgroundSize: `${line.clientWidth}px 100%`,
          backgroundPosition: `${line.clientWidth - word.offsetLeft}px 0%`,
        })
      })
    })
  }
}

let setOpts = {}
const prepare = async (force = true, opts) => {
  setOpts = opts
  if (prepared.value) return animateSet(force, setOpts)
  isPreparing.value = true
  await isFontReady()
  splitText.value = new SplitText(el.value, {
    type: splitType,
    balanceRatio: props.balanceRatio,
    useBalance: props.useBalance,
  })

  handleGradient()

  if (props.forceSet) animateSet(true, setOpts)
  window.addEventListener('resize', handleResize)
  prepared.value = true
  isPreparing.value = false

  await animateSet(force, setOpts)
}

const animateSet = async (force = true, { yPercent = 115 } = {}) => {
  await waitUntil(() => !isPreparing.value && prepared.value)
  isAnimated.value = force ? false : isAnimated.value

  for (const item of splitText.value[props.animateBy === 'lines' ? 'words' : props.animateBy]) {
    gsap.set(item, {
      yPercent: force ? yPercent : 0,
    })
  }
}

const animateIn = async (
  delay = 0,
  { ease = 'power2.inOut', duration = 0.7, stagger = 0.1, yPercent = 115 } = {},
) => {
  if (isAnimated.value) return
  isAnimated.value = true

  await waitUntil(() => !isPreparing.value && prepared.value)

  if (props.animateBy === 'lines') {
    return await Promise.all(
      splitText.value.lines.map((line, i) => {
        return gsap.fromTo(
          line.__words,
          {
            yPercent,
          },
          {
            yPercent: 0,
            ease,
            duration,
            delay: delay + i * 0.1,
          },
        )
      }),
    )
  }

  await gsap.fromTo(
    splitText.value[props.animateBy],
    {
      yPercent,
    },
    {
      yPercent: 0,
      ease,
      duration,
      stagger,
      delay,
    },
  )
}

const animateOut = async (
  delay = 0,
  { ease = 'power2.inOut', duration = 0.7, stagger = 0.1, yPercent = -115 } = {},
) => {
  if (!isAnimated.value) return
  isAnimated.value = false

  await waitUntil(() => !isPreparing.value && prepared.value)

  if (props.animateBy === 'lines') {
    return await Promise.all(
      splitText.value.lines.map((line, i) => {
        return gsap.to(line.__words, {
          yPercent,
          ease,
          duration,
          delay: delay + i * 0.1,
        })
      }),
    )
  }

  await gsap.to(splitText.value[props.animateBy], {
    yPercent,
    ease,
    duration,
    stagger,
    delay: delay,
  })
}

const handleResize = () => {
  splitText.value.revert()
  splitText.value.split()
  handleGradient()
  animateSet(!isAnimated.value, setOpts)
}

watch(
  () => props.text,
  async () => {
    if (prepared.value) {
      splitText.value.revert()
      innerText.value = props.text
      await nextTick()
      splitText.value.split()
      handleGradient()
      animateSet(!isAnimated.value, setOpts)
    } else {
      innerText.value = props.text
    }
  },
)

onMounted(async () => {
  if (props.icon) {
    console.log('icon', props.icon)
    el.value.classList.add('icon')
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

defineExpose({
  prepare,
  animateSet,
  animateIn,
  animateOut,
  splitText,
  ready: () => waitUntil(() => !isPreparing.value && prepared.value),
})
</script>

<style lang="scss" scoped>
.VText {
  position: relative;
  &.center {
    text-align: center;
    margin: 0 auto;
  }
  :global(html:not(.ios)) & {
    text-wrap: balance;
  }
}

:global(.line) {
  overflow: hidden;
  margin-bottom: -0.065em;
  padding-bottom: 0.065em;
}

:global(.skeeball .line) {
  padding-right: 0.1em;
  margin-right: -0.1em;
  margin-bottom: -0.13em;
  padding-bottom: 0.13em;
}

:global(.word) {
  position: relative;
  display: inline-block;
  margin-left: -0.0025em;
}

:global(.char) {
  position: relative;
  display: inline-block;
}
</style>
