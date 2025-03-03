<template>
  <div class="leaderboard">
    <div class="heading">
      <VText
        ref="heading"
        variant="tv-bold-96"
        text="High Score"
        :center="true"
      />
    </div>
    <div class="list">
      <div class="listItem topScoreRow">
        <div class="leaderboard__list__item__rank">
          <Scoreboard
            textVariant="tv-bold-110"
            :singleDigit="true"
            :value="0"
            scrollerVariant="yellow"
            :immediate="false"
            :ref="setRankNumber"
          />
        </div>
        <div class="leaderboard__list__item__score">
          <div class="topScore">
            <Scoreboard
              textVariant="tv-bold-150"
              :useColors="false"
              :ref="setScoreNumber"
              :value="score1"
              :immediate="false"
              :noBackground="true"
            />
            <LeaderboardBacking />
          </div>
        </div>
      </div>
      <div class="listItem">
        <div class="leaderboard__list__item__rank">
          <Scoreboard
            textVariant="tv-bold-110"
            :singleDigit="true"
            :value="0"
            :ref="setRankNumber"
            :immediate="false"
          />
        </div>
        <div class="leaderboard__list__item__score">
          <Scoreboard
            textVariant="tv-bold-110"
            :useColors="false"
            :ref="setScoreNumber"
            :value="score2"
            :immediate="false"
          />
        </div>
      </div>
      <div class="listItem">
        <div class="leaderboard__list__item__rank">
          <Scoreboard
            textVariant="tv-bold-110"
            :singleDigit="true"
            :value="0"
            :ref="setRankNumber"
            :immediate="false"
          />
        </div>
        <div class="leaderboard__list__item__score">
          <Scoreboard
            textVariant="tv-bold-110"
            :useColors="false"
            :ref="setScoreNumber"
            :value="score3"
            :immediate="false"
          />
        </div>
      </div>
      <div class="listItem">
        <div class="leaderboard__list__item__rank">
          <Scoreboard
            textVariant="tv-bold-110"
            :singleDigit="true"
            :value="0"
            :ref="setRankNumber"
            :immediate="false"
          />
        </div>
        <div class="leaderboard__list__item__score">
          <Scoreboard
            textVariant="tv-bold-110"
            :useColors="false"
            :ref="setScoreNumber"
            :value="score4"
            :immediate="false"
          />
        </div>
      </div>
      <div class="listItem">
        <div class="leaderboard__list__item__rank">
          <Scoreboard
            textVariant="tv-bold-110"
            :singleDigit="true"
            :value="0"
            :ref="setRankNumber"
            :immediate="false"
          />
        </div>
        <div class="leaderboard__list__item__score">
          <Scoreboard
            textVariant="tv-bold-110"
            :useColors="false"
            :ref="setScoreNumber"
            :value="score5"
            :immediate="false"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import VText from '@/components/VText.vue'
import Scoreboard from '@/components/ScoreBoard.vue'
import LeaderboardBacking from '@/components/leaderboard/LeaderboardBacking.vue'
const rankNumbers = ref([])
const scoreNumbers = ref([])

const props = defineProps({
  score1: {
    type: Number,
    default: 0,
  },
  score2: {
    type: Number,
    default: 0,
  },
  score3: {
    type: Number,
    default: 0,
  },
  score4: {
    type: Number,
    default: 0,
  },
  score5: {
    type: Number,
    default: 0,
  },
})

const setRankNumber = (el) => {
  if (el && !rankNumbers.value.includes(el)) {
    rankNumbers.value.push(el)
  }
}
const setScoreNumber = (el) => {
  if (el && !scoreNumbers.value.includes(el)) {
    scoreNumbers.value.push(el)
  }
}

const heading = ref(null)

function animateSet() {
  heading.value.prepare()
  rankNumbers.value.forEach((number) => {
    number.animateSet()
  })
  scoreNumbers.value.forEach((number) => {
    number.animateSet()
  })
}

const animateIn = async () => {
  setTimeout(() => {
    heading.value.animateIn()
  }, 100)
  rankNumbers.value.forEach((number, index) => {
    setTimeout(
      () => {
        number.goTo(index + 1)
      },
      (index + 1) * 150,
    )
  })
  scoreNumbers.value.forEach((number, index) => {
    setTimeout(
      () => {
        number.animateIn()
      },
      (index + 1) * 150,
    )
  })
}

const animateOut = () => {
  heading.value.animateOut()
  scoreNumbers.value.forEach((number, index) => {
    number.goTo(0, props[`score${index + 1}`])
  })
  rankNumbers.value.forEach((number, index) => {
    number.goTo(0, index + 1)
  })
}

defineExpose({
  animateSet,
  animateIn,
  animateOut,
})
</script>

<style lang="scss" scoped>
.leaderboard {
  padding: px-to-vw(100, 4k);
  .heading {
    text-align: center;
    margin-bottom: px-to-vw(100, 4k);
  }
  .list {
    display: flex;
    flex-direction: column;
    gap: px-to-vw(100, 4k);

    .listItem {
      display: flex;
      gap: px-to-vw(54, 4k);
    }

    .topScoreRow {
      align-items: center;
      padding-bottom: px-to-vw(50, 4k);
    }
  }

  .leaderboard__list__item__score {
    width: 100%;
  }

  .topScore {
    position: relative;
    display: flex;
    justify-content: center;
    align-items: center;

    .scoreboard {
      z-index: 1;
    }
    svg {
      width: 100%;
      height: auto;
      position: absolute;
      margin-top: 2%;
    }
  }
}
</style>
