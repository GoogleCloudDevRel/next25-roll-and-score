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
        <div class="station-header">
          <VText
            :text="'Station ' + station.stationID"
            variant="bold-48"
          />
          <div class="station-header-buttons">
            <VButton
              textVariant="bold-24"
              :text="station.isRunning ? 'Running' : 'Start Game'"
              :backgroundColor="station.isRunning ? 'grey' : 'green'"
              :disabled="station.isRunning"
              @click="toggleStatus(station.stationID)"
            />
            <VButton
              textVariant="bold-24"
              text="Cancel Game"
              :backgroundColor="station.isRunning ? 'red' : 'grey'"
              :disabled="!station.isRunning"
              @click="toggleStatus(station.stationID)"
            />
          </div>
        </div>
        <div class="station-table">
          <VTable
            :headers="tableHeaders"
            :items="station.tableData"
            :formatters="formatters"
            primaryKey="userId"
          />
        </div>
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
import { waitFor } from '@/utils/deferred'

const tableHeaders = [
  // { key: 'stationID', label: 'Station ID' },
  { key: 'startTime', label: 'Start Time' },
  { key: 'endTime', label: 'End Time' },
  // { key: 'gameStatus', label: 'Game Status' },
  { key: 'analysisURL', label: 'View Analysis' },
]

const formatters = {
  analysisURL: (value) => {
    return value ? `<a class="button" href="${value}" target="_blank">View Analysis</a>` : ''
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
    tableData: [],
  },
  {
    stationID: '02',
    isRunning: false,
    gameId: null,
    tableData: [],
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
    gameStations.forEach((station) => {
      station.tableData = []
    })
    snapshot.docs.forEach((doc) => {
      const data = doc.data()
      if (data.gameStatus === 'cancelled') return
      const stationID = data.stationId
      const existingStation = gameStations.find((s) => `station${s.stationID}` === stationID)
      if (existingStation) {
        existingStation.tableData.push({
          stationID: data.stationId,
          startTime: data.startTime.toDate().toLocaleTimeString(),
          endTime: data.endTime ? data.endTime.toDate().toLocaleTimeString() : null,
          gameStatus: data.gameStatus,
          analysisURL:
            data.gameStatus === 'cancelled' || data.gameStatus === 'playing'
              ? null
              : `${window.location.origin}/?gameId=${doc.id}#/chromebook`,
        })
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
const blocks = ref([])

async function animateSet() {
  gsap.set(blocks.value, {
    clipPath: 'inset(50% round 25px)',
  })
}

async function animateIn() {
  await waitFor(() => gameStations.some((s) => s.tableData.length > 0))
  gsap.to(blocks.value, {
    clipPath: 'inset(-5% round 25px)',
    duration: 1.2,
    ease: 'power2.inOut',
    delay: 0.2,
  })
}

async function animateOut() {
  await gsap.to(blocks.value, {
    clipPath: 'inset(50% round 25px)',
    duration: 1,
    stagger: 0.1,
    ease: 'power2.inOut',
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
  padding: 0 px-to-vw(48) px-to-vw(48);
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden; /* Prevent overall page scrolling */
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
  grid-template-columns: 1fr 1fr;
  gap: px-to-vw(18);
  width: 100%;
  height: calc(100vh - 150px);
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
  overflow: hidden;
  height: auto;
  max-height: 100%;
}

.station01 {
  --station-color: #{$brandBlue};
  background: var(--station-color);
}

.station02 {
  --station-color: #{$brandYellow};
  background: var(--station-color);
}

.station-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: px-to-vw(26) 0;
  flex-shrink: 0;
}

.station-header-buttons {
  display: flex;
  gap: px-to-vw(18);
}

.station-table {
  width: 100%;
  flex: 1; /* Take up remaining space */
  overflow-y: auto; /* Enable vertical scrolling */
  margin-top: 15px; /* Add some spacing from the header */
  display: flex;
  flex-direction: column;
  min-height: 0; /* Important for nested flex scrolling to work */

  /* style scrollbar */
  &::-webkit-scrollbar {
    width: 12px;
  }
  &::-webkit-scrollbar-track {
    background: var(--station-color);
    border-radius: 5px;
  }
  &::-webkit-scrollbar-thumb {
    background: #fff;
    border-radius: 10px;
    border: 3px solid var(--station-color);
  }
}

.station-table :deep(.v-table) {
  width: 100%;
  table-layout: fixed;
  margin-bottom: 10px;
}

.station-table :deep(.v-table th),
.station-table :deep(.v-table td) {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-weight: 700;
}

.station-table :deep(.button) {
  background: $brandGreen;
  color: #fff;
  border-radius: 999px;
  text-decoration: none;
  text-shadow: px-to-vw(2) px-to-vw(3) 0 #000;
  -webkit-text-stroke: px-to-vw(4);
  -webkit-text-stroke-color: #000;
  box-shadow: px-to-vw(2) px-to-vw(3) 0 #000;
  border: px-to-vw(2) solid #000;
  height: min(px-to-vh(57), 57px);
  width: max-content;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 24px;

  &:hover {
    box-shadow: 0px 0px 0px 0px rgba(0, 0, 0, 1);
    transform: translateX(1px) translateY(3px);
  }
}
</style>
