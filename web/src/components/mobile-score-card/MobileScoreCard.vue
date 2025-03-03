<template>
  <div class="mobileScoreCard">
    <div class="wrapper">
      <div class="heading">
        <VText
          variant="mobile-bold-42"
          text="Roll & Score"
          center
          ref="heading"
        />
        <div
          class="backing-wrapper"
          ref="backing"
        >
          <MobileScoreCardBacking />
        </div>
      </div>
      <div
        class="video-wrapper"
        ref="videoWrapper"
      >
        <video
          autoplay
          loop
          muted
          playsinline
          :src="videoSrc"
        />
      </div>
      <div class="scores-wrapper">
        <VBadge
          variant="red"
          :ref="addBadgeRef"
        >
          <div class="badge-inner red">
            <VText
              variant="mobile-bold-15"
              text="Leaderboard"
              center
            />
            <div class="score-wrapper">
              <VText
                variant="mobile-bold-24"
                :text="`#${leaderboard}`"
                center
              />
            </div>
          </div>
        </VBadge>
        <VBadge
          variant="green"
          :ref="addBadgeRef"
        >
          <div class="badge-inner">
            <VText
              variant="mobile-bold-15"
              text="Final Score"
              center
            />
            <div class="score-wrapper">
              <VText
                variant="mobile-bold-24"
                :text="finalScore"
                center
              />
            </div>
          </div>
        </VBadge>
        <VBadge
          variant="yellow"
          :ref="addBadgeRef"
        >
          <div class="badge-inner">
            <VText
              variant="mobile-bold-15"
              text="Data"
              center
            />
            <div class="score-wrapper">
              <VText
                variant="mobile-bold-24"
                :text="`${data}%`"
                center
              />
            </div>
          </div>
        </VBadge>
      </div>
      <div
        class="description-wrapper"
        ref="descriptionWrapper"
      >
        <VText
          variant="mobile-medium-15"
          :text="description"
          animateBy="lines"
          center
          ref="descriptionText"
        />
      </div>
      <div
        class="button-wrapper"
        ref="button"
      >
        <VButton
          textVariant="mobile-bold-15"
          text="Learn More"
          backgroundColor="yellow"
        />
      </div>
    </div>
  </div>
  <BackgroundBase :dpr="1.5">
    <template v-slot="{ oglState }">
      <BackgroundRings
        :oglState="oglState"
        grayscale
      />
    </template>
  </BackgroundBase>
</template>

<script setup>
import MobileScoreCardBacking from './MobileScoreCardBacking.vue'
import VText from '@/components/VText.vue'
import BackgroundRings from '@/components/background/BackgroundRings.vue'
import BackgroundBase from '@/components/background/BackgroundBase.vue'
import VBadge from '@/components/VBadge.vue'
import VButton from '@/components/VButton.vue'
import { onMounted, ref } from 'vue'
import gsap from 'gsap'

const backing = ref(null)
const videoWrapper = ref(null)
const descriptionWrapper = ref(null)
const button = ref(null)
const badges = ref([])
const descriptionText = ref(null)
const addBadgeRef = (el) => {
  if (el) {
    badges.value.push(el)
  }
}

defineProps({
  videoSrc: {
    type: String,
    required: true,
  },
  leaderboard: {
    type: Number,
    required: true,
  },
  finalScore: {
    type: Number,
    required: true,
  },
  data: {
    type: Number,
    required: true,
  },
  description: {
    type: String,
    required: true,
  },
})

const heading = ref(null)

onMounted(() => {
  heading.value.prepare()
  descriptionText.value.prepare()
  animateSet()
  window.scrollTo(0, 0)
})

const backings = [backing, videoWrapper, descriptionWrapper]

const animateSet = () => {
  heading.value.animateSet()
  descriptionText.value.animateSet()
  badges.value.forEach((badge) => {
    badge.animateSet()
  })

  const backingValues = backings.map((_backing) => _backing.value)
  backingValues.forEach((_backing) => {
    gsap.set(_backing, {
      scale: 0,
    })
  })

  gsap.set(button.value, {
    scale: 0,
  })
}

const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

const animateIn = () => {
  setTimeout(async () => {
    const backingValues = backings.map((_backing) => _backing.value)

    const backingAnimate = {
      scale: 1,
      duration: 1,
      ease: 'power2.inOut',
    }

    gsap.to(backingValues[0], {
      ...backingAnimate,
      duration: 0.8,
      delay: 0.1,
    })

    heading.value.animateIn(0.4)

    await wait(400)

    gsap.to(backingValues[1], {
      ...backingAnimate,
      duration: 0.8,
      delay: 0.6,
    })

    badges.value.forEach((badge, index) => {
      badge.animateIn(0.5 + index * 0.1)
    })

    gsap.to(backingValues[2], {
      ...backingAnimate,
      duration: 0.8,
      delay: 0.8,
    })

    descriptionText.value.animateIn(1.4)
    gsap.to(button.value, {
      ...backingAnimate,
      duration: 0.8,
      delay: 1,
    })
  }, 100)
}

const animateOut = async () => {
  await heading.value.animateOut()
  const backingValues = backings.map((_backing) => _backing.value)
  gsap.to(backingValues, {
    scale: 0,
    duration: 0.5,
    stagger: 0.1,
    ease: 'power2.inOut',
  })
  gsap.to(button.value, {
    scale: 0,
    duration: 0.5,
    delay: 0.1,
    ease: 'power2.inOut',
  })

  badges.value.forEach((badge, index) => {
    badge.animateOut(index * 0.1)
  })
}

defineExpose({
  animateIn,
  animateSet,
  animateOut,
})
</script>

<style lang="scss" scoped>
$border-radius: 12.5px;
$gap: 10px;
$boxShadow: 2px 3px 0px 0px #000000;
.ogl-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}
.mobileScoreCard {
  width: 100%;
  padding: 0 $gap;
  position: relative;
  z-index: 2;
  min-height: 100vh;

  .wrapper {
    display: flex;
    align-items: center;
    flex-direction: column;
    gap: $gap;
  }

  .button-wrapper {
    position: fixed;
    bottom: 30px;
  }

  .description-wrapper {
    background: #2a2a2a;
    border-radius: $border-radius;
    padding: 30px 15px;
    width: 100%;
    color: #fff;
    box-shadow: $boxShadow;
    margin-bottom: 94px;
  }

  .scores-wrapper {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    width: 100%;
    gap: $gap;
    .badge {
      border-radius: $border-radius;
      width: 100%;
      justify-content: center;
      box-shadow: $boxShadow;
      .badge-inner {
        padding: 15px 5px;
        .score-wrapper {
          margin-top: 8px;
        }
      }
      &.red {
        .score-wrapper {
          color: $brandGreen;
        }
      }
      &.green {
        .score-wrapper {
          color: $brandYellow;
        }
      }
      &.yellow {
        .score-wrapper {
          color: $brandBlue;
        }
      }
    }
  }

  .video-wrapper {
    width: 100%;
    height: 100%;
    background-color: #bebebe;
    border-radius: $border-radius;
    aspect-ratio: 16 / 9;
    overflow: hidden;
    box-shadow: $boxShadow;
    video {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  }

  .heading {
    position: sticky;
    top: 30px;
    margin-top: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: $brandYellow;
    height: 60px;
    padding: 0 16px;
    margin-bottom: 12px;
    z-index: 2;

    .backing-wrapper {
      position: absolute;
      width: 100%;
      height: auto;
      display: flex;
      margin-top: 5px;

      svg {
        position: relative;
        width: 100%;
        height: auto;
        z-index: 1;
      }
    }

    .VText {
      position: relative;
      z-index: 2;
      width: 100%;
    }
  }
}
</style>
