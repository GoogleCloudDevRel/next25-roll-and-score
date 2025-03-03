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
  <div class="wrapper">
    <div class="header">
      <IconGoogle class="logo" />
      <VButton
        text="How it Works"
        textVariant="bold-24"
      />
    </div>
    <div
      class="dashboard"
      ref="dashboard"
    >
      <div
        class="block score"
        ref="blocks"
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
        />
        <div></div>
        <div></div>
      </div>
      <div
        class="block stats"
        ref="blocks"
      >
        <VText
          ref="statsText"
          text="Retrieve Stats"
          variant="bold-48"
        />
        <div class="qr">
          <img
            src="/images/qr.png"
            alt="stats"
          />
        </div>
        <div></div>
      </div>
      <div
        class="block video-replay"
        ref="blocks"
      >
        <video
          src="https://storage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
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
import { onMounted, ref } from 'vue'
import IconGoogle from './icons/IconGoogle.vue'
import ScoreBoard from './ScoreBoard.vue'
import VButton from './VButton.vue'
import VText from './VText.vue'
import { gsap } from '@/utils/gsap'
import BackgroundBase from './background/BackgroundBase.vue'
import BackgroundRings from './background/BackgroundRings.vue'

const dashboard = ref()
const scoreBoard = ref()
const scoreText = ref()
const statsText = ref()
const blocks = ref([])

onMounted(() => {
  blocks.value = Array.from(dashboard.value.querySelectorAll('.block'))
  animateSet()
})

function animateSet() {
  gsap.set(blocks.value, {
    clipPath: 'inset(50% round 25px)',
  })

  scoreText.value.prepare()
  statsText.value.prepare()
  scoreBoard.value.goTo(0, 0, true)
}

async function animateIn() {
  gsap.to(blocks.value, {
    clipPath: 'inset(-5% round 25px)',
    duration: 1,
    stagger: 0.1,
    ease: 'power2.inOut',
    onStart: () => {
      scoreText.value.animateIn(0.2)
      statsText.value.animateIn(0.3)
      scoreBoard.value.goTo(1234)
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
      scoreBoard.value.goTo(0)
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
  padding: px-to-vw(2);

  img {
    width: 100%;
    aspect-ratio: 1 / 1;
  }
}
</style>
