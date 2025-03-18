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
        ref="btn"
        text="How it Works"
        textVariant="bold-24"
      />
    </div>
    <div
      class="dashboard"
      ref="dashboard"
    >
      <div
        v-for="station in gameStations"
        :key="station.stationID"
        :class="'block station' + station.stationID"
        ref="blocks"
      >
        <VText
          :text="'Station ' + station.stationID"
          variant="bold-48"
        />
        <VButton
          textVariant="bold-24"
          :text="station.isRunning ? 'Running' : 'Start Game'"
          :backgroundColor="station.isRunning ? 'red' : 'blue'"
          :disabled="station.isRunning"
          @click="toggleStatus(station.stationID)"
        />
        <VButton
          textVariant="bold-24"
          text="Reset Game"
          :backgroundColor="station.isRunning ? 'red' : 'grey'"
          :disabled="!station.isRunning"
          @click="toggleStatus(station.stationID)"
        />
        <div></div>
        <div></div>
      </div>
      <div
        class="block video-replay"
        ref="blocks"
      >
        <VTable
          :headers="tableHeaders"
          :items="tableData"
          :formatters="formatters"
          primaryKey="userId"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref, reactive } from 'vue'
import IconGoogle from './icons/IconGoogle.vue'
import VButton from './VButton.vue'
import VText from './VText.vue'
import { gsap } from '@/utils/gsap'
import BackgroundBase from './background/BackgroundBase.vue'
import BackgroundRings from './background/BackgroundRings.vue'
import { doc, updateDoc, onSnapshot, collection, addDoc, query, orderBy } from 'firebase/firestore'
import { db, signIn } from '@/config/firebaseConfig'
import VTable from './VTable.vue'

const tableHeaders = [
  { key: 'stationID', label: 'Station ID' },
  { key: 'startTime', label: 'Start Time' },
  { key: 'endTime', label: 'End Time' },
  { key: 'gameStatus', label: 'Game Status' },
  { key: 'analysisURL', label: 'View Analysis' },
]

const tableData = ref([])

const formatters = {
  analysisURL: (value) => {
    return value ? `<a href="${value}" target="_blank">View Analysis</a>` : ''
  },
}

// ===================================================
// Controllers
// ===================================================

const gameStations = reactive([
  {
    stationID: '01',
    isRunning: false,
    gameId: null,
  },
  {
    stationID: '02',
    isRunning: false,
    gameId: null,
  },
])
const unsubscribeListeners = {} // Store unsubscribe functions

onMounted(async () => {
  blocks.value = Array.from(dashboard.value.querySelectorAll('.block'))
  await signIn()
  setupListeners()
  setupTableData()
})

onUnmounted(() => {
  // Unsubscribe all listeners when the component is unmounted
  Object.values(unsubscribeListeners).forEach((unsubscribe) => unsubscribe())
})

const setupTableData = () => {
  const gamesCollection = collection(db, 'games')
  const q = query(gamesCollection, orderBy('startTime', 'desc'))
  unsubscribeListeners['games'] = onSnapshot(q, (snapshot) => {
    tableData.value = snapshot.docs.map((doc) => {
      const data = doc.data()
      return {
        stationID: data.stationId,
        startTime: data.startTime.toDate().toLocaleTimeString(),
        endTime: data.endTime ? data.endTime.toDate().toLocaleTimeString() : null,
        gameStatus: data.gameStatus,
        analysisURL:
          data.gameStatus === 'cancelled' || data.gameStatus === 'playing'
            ? null
            : 'https://www.google.com',
      }
    })
  })
}

const setupListeners = () => {
  const stationIDs = ['01', '02']
  stationIDs.forEach((stationID) => {
    const docRef = doc(db, 'gameStations', `station${stationID}`)
    unsubscribeListeners[stationID] = onSnapshot(
      docRef,
      (docSnap) => {
        if (docSnap.exists()) {
          const data = docSnap.data()
          const existingStation = gameStations.find((s) => s.stationID === stationID)
          if (existingStation) {
            existingStation.isRunning = data.isRunning || false
            existingStation.gameId = data.gameId || null
          } else {
            gameStations.push({
              stationID: stationID,
              isRunning: data.isRunning || false,
              gameId: data.gameId || null,
            })
          }
        } else {
          console.log(`Station ${stationID} document not found.`)
          // Handle document absence
          gameStations.push({
            stationID: stationID,
            isRunning: false,
            gameId: null,
          })
        }
      },
      (error) => {
        console.error(`Error listening to station ${stationID}:`, error)
      },
    )
  })
}

const toggleStatus = async (stationID) => {
  const station = gameStations.find((s) => s.stationID === stationID)
  if (station) {
    station.isRunning = !station.isRunning
    try {
      const gamesCollection = collection(db, 'games')
      if (station.isRunning) {
        const newGame = await addDoc(gamesCollection, {
          endTime: null,
          startTime: new Date(),
          gameStatus: 'playing',
          stationId: `station${stationID}`,
          scores: [],
          totalScore: 0,
        })
        station.gameId = newGame.id
      } else {
        const gameRef = doc(gamesCollection, station.gameId)
        await updateDoc(gameRef, {
          endTime: new Date(),
          gameStatus: 'cancelled',
        })
      }

      const docRef = doc(db, 'gameStations', `station${stationID}`)
      await updateDoc(docRef, {
        isRunning: station.isRunning,
        gameId: station.isRunning ? station.gameId : null,
      })

      console.log(`Station ${stationID} status updated in Firestore.`)
    } catch (error) {
      console.error(`Error updating station ${stationID} status:`, error)
      station.isRunning = !station.isRunning
    }
  }
}

// ===================================================
// Animation
// ===================================================

const dashboard = ref()
const btn = ref()
const blocks = ref([])

async function animateSet() {
  gsap.set(blocks.value, {
    clipPath: 'inset(50% round 25px)',
  })
  btn.value.animateSet()
  // await scoreText.value.prepare()
  // await statsText.value.prepare()
  // scoreBoard.value.animateSet()
}

async function animateIn() {
  gsap.to(blocks.value, {
    clipPath: 'inset(-5% round 25px)',
    duration: 1.2,
    ease: 'power2.inOut',
    delay: 0.2,
    onStart: () => {
      // scoreText.value.animateIn(0.2)
      // statsText.value.animateIn(0.3)
      btn.value.animateIn(0.4)
      // scoreBoard.value.animateIn(0.4)
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
      // scoreText.value.animateOut()
      // statsText.value.animateOut()
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

  .VButton {
    width: 100%;
    height: 25%;
  }
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

.station01 {
  background: $brandGreen;
}

.station02 {
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
