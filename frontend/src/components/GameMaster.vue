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
        :class="'block station' + stationId"
        ref="blocks"
      >
        <div class="station-header">
          <VText
            :text="'Station ' + stationId"
            variant="bold-48"
          />
          <div class="station-header-buttons">
            <VButton
              textVariant="bold-24"
              :text="gameStarted ? 'Running' : 'Start Game'"
              :backgroundColor="gameStarted ? 'grey' : 'green'"
              :disabled="isStartGameDisabled"
              @click="startGame(stationId)"
            />
            <VButton
              textVariant="bold-24"
              text="Cancel Game"
              :backgroundColor="gameStarted ? 'red' : 'grey'"
              :disabled="!gameStarted"
              @click="cancelGame(stationId, currentGameID)"
            />
          </div>
        </div>
        <div class="station-table">
          <VTable
            :headers="tableHeaders"
            :items="tableData"
            :formatters="formatters"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import BackgroundBase from './background/BackgroundBase.vue'
import BackgroundRings from './background/BackgroundRings.vue'
import IconGoogle from './icons/IconGoogle.vue'
import VButton from './VButton.vue'
import VText from './VText.vue'
import VTable from './VTable.vue'

import { onMounted, onUnmounted, ref, watch } from 'vue'
import { db } from '@/config/firebaseConfig'
import { doc, getDoc, onSnapshot, collection, query, orderBy, limit } from 'firebase/firestore'
import { gsap } from '@/utils/gsap'
import { getQueryParam } from '@/utils/get-query-param'
import { subscribeGameStarted, useScoreStore } from '@/store'
import { storeToRefs } from 'pinia'

const scoreStore = useScoreStore()
const { gameStarted } = storeToRefs(scoreStore)

const tableHeaders = [
  { key: 'gameId', label: 'Game ID' },
  { key: 'startTime', label: 'Start Time' },
  { key: 'endTime', label: 'End Time' },
  { key: 'gameStatus', label: 'Game Status' },
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

const device = getQueryParam('device', false) || '1'
const stationId = device.padStart(2, '0')
const isStartGameDisabled = ref(false)
const currentGameID = ref(null)
const tableData = ref([])

let unsubscribeGameStarted = null
let unsubscribeTableChanges = null

onMounted(async () => {
  console.log(stationId)

  getUnfinishedGameID()
  blocks.value = Array.from(dashboard.value.querySelectorAll('.block'))
  unsubscribeGameStarted = subscribeGameStarted()
  unsubscribeTableChanges = subscribeTableData()
})

onUnmounted(() => {
  unsubscribeGameStarted()
  unsubscribeTableChanges()
})

const getUnfinishedGameID = async () => {
  try {
    const docRef = doc(db, 'station-info', `station${stationId}`)
    const docSnap = await getDoc(docRef)

    if (docSnap.exists() && docSnap.data()?.gameId) {
      currentGameID.value = docSnap.data()?.gameId
    }
  } catch (error) {
    console.error('Error fetching unfishined game ID from Firestore:', error)
  }
}

function capitalizeFirstLetter(str) {
  if (!str) {
    return '' // Handle empty or null strings
  }
  return str.charAt(0).toUpperCase() + str.slice(1)
}

const subscribeTableData = async () => {
  const gamesCollection = collection(db, 'game-sessions')
  const q = query(gamesCollection, orderBy('startDateTime', 'desc'), limit(50))
  unsubscribeTableChanges = onSnapshot(q, (snapshot) => {
    tableData.value = [] // Reset the array

    snapshot.docs.forEach((doc) => {
      const data = doc.data()
      if (data.stationId === stationId && data.gameStatus === 'completed') {
        tableData.value.push({
          gameId: doc.id,
          startTime: data.startDateTime.toDate().toLocaleTimeString(),
          endTime: data.endDateTime ? data.endDateTime.toDate().toLocaleTimeString() : null,
          gameStatus: capitalizeFirstLetter(data.gameStatus),
          analysisURL:
            data.gameStatus === 'completed'
              ? `${window.location.origin}/?gameId=${doc.id}#/chromebook`
              : null,
        })
      }
    })
  })
}

watch(
  () => gameStarted.value,
  (v) => {
    isStartGameDisabled.value = v
  },
)

const startGame = async (stationId) => {
  console.log(`Starting game for Station ${stationId}`)
  isStartGameDisabled.value = true

  try {
    const response = await fetch('/api/start_game', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        stationId: stationId,
      }),
    })

    const data = await response.json()
    currentGameID.value = data.gameId
    console.log('Game started successfully:', data.gameId)
  } catch (error) {
    console.error('Error creating game:', error)
  }
}

const cancelGame = async (stationId, gameId) => {
  console.log(`Cancelling game ${gameId} for Station ${stationId}`)
  try {
    const response = await fetch('/api/cancel_game', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        stationId: stationId,
        gameId: gameId,
      }),
    })
    const data = await response.json()
    console.log(`Game ${gameId} cancelled successfully:`, data)
  } catch (error) {
    console.error(`Error cancelling game: ${gameId} for Station ${stationId}`, error)
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
  // await waitFor(() => tableData.length > 0)
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
  // grid-template-columns: 1fr 1fr;
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
