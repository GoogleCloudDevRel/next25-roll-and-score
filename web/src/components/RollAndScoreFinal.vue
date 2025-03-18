<template>
  <BackgroundBase
    :dpr="1.5"
    v-slot="{ oglState }"
  >
    <BackgroundRings
      :oglState="oglState"
      :grayscale="true"
    />
  </BackgroundBase>
  <div
    class="wrapper"
    ref="wrapper"
  >
    <div class="header">
      <IconGoogle class="logo" />
    </div>
    <div
      class="dashboard"
      ref="dashboard"
    >
      <div
        class="block score"
        :ref="setBlocks"
      >
        <VText
          ref="scoreText"
          text="Final Score"
          variant="bold-48"
        />
        <ScoreBoard
          ref="scoreBoard"
          :useColors="false"
          textVariant="bold-80"
          :value="props.score"
        />
        <div></div>
        <div></div>
      </div>
      <div
        class="block stats"
        :ref="setBlocks"
      >
        <VText
          ref="statsText"
          text="Retrieve Stats"
          variant="bold-48"
        />
        <div class="qr">
          <img
            :src="qr"
            alt="stats"
          />
        </div>
        <div></div>
      </div>
      <div
        class="block video-replay"
        :ref="setBlocks"
      >
        <video
          :src="videoSrc"
          autoplay
          loop
          muted
          class="video"
          ref="video"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import IconGoogle from './icons/IconGoogle.vue'
import ScoreBoard from './ScoreBoard.vue'
import VButton from './VButton.vue'
import VText from './VText.vue'
import { gsap } from '@/utils/gsap'
import BackgroundBase from './background/BackgroundBase.vue'
import BackgroundRings from './background/BackgroundRings.vue'
import { generateQR } from '@/utils/qr'

const wrapper = ref()
const dashboard = ref()
const scoreBoard = ref()
const scoreText = ref()
const statsText = ref()
const btn = ref()
const blocks = ref([])
const qr = ref()

const setBlocks = (el) => {
  blocks.value.push(el)
}

const props = defineProps({
  score: {
    type: Number,
    default: 0,
  },
  gameId: {
    type: String,
    default: '',
  },
  videoSrc: {
    type: String,
    default: '',
  },
})

onMounted(async () => {
  gsap.set(wrapper.value, {
    opacity: 0,
  })
})

watch(
  () => props.gameId,
  async () => {
    qr.value = await generateQR(`${window.location.origin}?gameId=${props.gameId}#/phone`)
  },
)

async function animateSet() {
  gsap.set(blocks.value, {
    clipPath: 'inset(50% round 25px)',
  })
  btn.value.animateSet()
  await scoreText.value.prepare()
  await statsText.value.prepare()
  scoreBoard.value.animateSet()
  gsap.set(wrapper.value, {
    opacity: 1,
  })
}

async function animateIn() {
  gsap.to(blocks.value, {
    clipPath: 'inset(-5% round 25px)',
    duration: 1.2,
    ease: 'power2.inOut',
    delay: 0.2,
    onStart: () => {
      scoreText.value.animateIn(0.2)
      statsText.value.animateIn(0.3)
      btn.value.animateIn(0.4)
      scoreBoard.value.animateIn(0.4)
    },
  })
}

async function animateOut() {
  await gsap.to(blocks.value, {
    clipPath: 'inset(50% round 25px)',
    duration: 1,
    stagger: 0.1,
    ease: 'power2.inOut',
    onComplete: () => {
      scoreText.value.animateOut()
      statsText.value.animateOut()
    },
  })
}

defineExpose({
  animateSet,
  animateIn,
  animateOut,
})
</script>

<style lang="scss" scoped>
.wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 0 px-to-vw(48) px-to-vw(48);
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
}

.header {
  display: flex;
  justify-content: space-between;
  width: 100%;
  padding: px-to-vw(26) 0;
}

.logo {
  width: px-to-vw(64);
  height: auto;
}

.dashboard {
  display: grid;
  grid-template-columns: px-to-vw(440) 1fr;
  grid-template-rows: 1fr 1fr;
  gap: px-to-vw(18);
  width: 100%;
  flex: 1;
  max-height: px-to-vw(880);
}

.block {
  position: relative;
  text-align: center;
  background: #bebebe;
  box-shadow:
    0 0 0 2px #000,
    3px 4px 0 0 #000;
  border-radius: 25px;
  padding: 30px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  overflow: hidden;
}

.score {
  background: $brandGreen;
}

.stats {
  background: $brandYellow;
}

.video-replay {
  grid-column: 2 / 3;
  grid-row: 1 / 3;

  video {
    position: absolute;
    top: -1%;
    left: -1%;
    width: 102%;
    height: 102%;
    object-fit: cover;
  }
}

.qr {
  width: px-to-vw(200);
  height: px-to-vw(200);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: px-to-vw(20);
  background: #fff;
  box-shadow:
    0 0 0 2px #000,
    3px 4px 0 0 #000;
  padding: px-to-vw(16);

  img {
    width: 100%;
    aspect-ratio: 1 / 1;
  }
}
</style>
