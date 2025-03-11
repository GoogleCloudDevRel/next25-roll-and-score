<template>
  <div class="mobileControlCard">
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
          <MobileControlCardBacking />
        </div>
      </div>
      <div class="controls">
        <div
          class="button-wrapper"
          ref="button"
          v-for="station in gameStations"
          :key="station.stationID"
        >
          <VText
            variant="mobile-bold-24"
            :text="'Station: ' + station.stationID"
            center
          />
          <VButton
            textVariant="mobile-bold-15"
            :text="station.isRunning ? 'Running' : 'Start Game'"
            :backgroundColor="station.isRunning ? 'red' : 'green'"
            :disabled="station.isRunning"
            @click="toggleStatus(station.stationID)"
          />
          <VButton
            textVariant="mobile-bold-15"
            text="Reset Game"
            backgroundColor="blue"
            :disabled="!station.isRunning"
            @click="toggleStatus(station.stationID)"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import MobileControlCardBacking from './MobileContorlCardBacking.vue'
import VText from '@/components/VText.vue'
import VButton from '@/components/VButton.vue'
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { doc, updateDoc, onSnapshot } from 'firebase/firestore'
import { auth, db, onAuthStateChanged } from '@/config/firebaseConfig'

const gameStations = reactive([])
const unsubscribeListeners = {} // Store unsubscribe functions

onAuthStateChanged(auth, (user) => {
  if (user) {
    // User is signed in.
    const uid = user.uid
    console.log('User is signed in:', uid)
  } else {
    // User is signed out.
    console.log('User is signed out.')
    window.location.hash = '/login'  
  }
})

onMounted(async () => {
  window.scrollTo(0, 0)
  setupListeners()
})

onUnmounted(() => {
  // Unsubscribe all listeners when the component is unmounted
  Object.values(unsubscribeListeners).forEach((unsubscribe) => unsubscribe())
})

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
          } else {
            gameStations.push({
              stationID: stationID,
              isRunning: data.isRunning || false,
            })
          }
        } else {
          console.log(`Station ${stationID} document not found.`)
          // Handle document absence
          gameStations.push({
            stationID: stationID,
            isRunning: false,
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
      const docRef = doc(db, 'gameStations', `station${stationID}`)
      await updateDoc(docRef, {
        isRunning: station.isRunning,
      })
      console.log(`Station ${stationID} status updated in Firestore.`)
    } catch (error) {
      console.error(`Error updating station ${stationID} status:`, error)
      station.isRunning = !station.isRunning
    }
  }
}
</script>

<style lang="scss" scoped>
$border-radius: 12.5px;
$gap: 10px;
$boxShadow: 2px 3px 0px 0px #000000;
.mobileControlCard {
  width: 100%;
  padding: 0 $gap;
  position: relative;
  z-index: 2;
  min-height: 100vh;
  background-color: #000000;

  .wrapper {
    display: flex;
    align-items: center;
    flex-direction: column;
    gap: $gap;
  }

  .heading {
    position: sticky;
    top: 30px;
    margin-top: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: $brandYellow;
    height: 3em;
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

  .controls {
    width: 65%;
  }

  .button-wrapper {
    position: relative;
    z-index: 2;
    background-color: gray;
    padding: 2em;
    margin-top: 1em;
    border-radius: 0.5em;
    gap: $gap;

    .VText {
      color: $brandYellow;
    }

    .VButton {
      position: relative;
      width: 100%;
      margin-top: 1em;
      z-index: 2;
    }
  }
}
</style>
