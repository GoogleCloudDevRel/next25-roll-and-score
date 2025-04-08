import { getQueryParam } from "@/utils/get-query-param";
import { defineStore } from "pinia";
import { db } from '@/config/firebaseConfig';
import { collection, query, orderBy, limit, onSnapshot, doc, getDoc, getDocs } from "firebase/firestore";

export const saveEndGame = async () => {

}

export const subscribeTotalScore = async (gameId) => {
  const game = doc(collection(db, 'game-sessions'), gameId);
  const unsubscribe = onSnapshot(game, (gameSnapshot) => {
    const gameData = gameSnapshot.data()
    useScoreStore().setTotalScore(gameData.totalScore)
    useScoreStore().setTries(gameData.scores.length)
  })
  return unsubscribe
}

export const subscribeGameStarted = async () => {
  const stationName = useScoreStore().stationName
  const stationInfo = doc(collection(db, 'station-info'), stationName);
  const unsubscribe = onSnapshot(stationInfo, (stationInfoSnapshot) => {
    useScoreStore().setGameStarted(stationInfoSnapshot.data().isRunning)
    useScoreStore().setGameId(stationInfoSnapshot.data().gameId)
    useScoreStore().setVideoReplay(stationInfoSnapshot.data().replayVideo)
    useScoreStore().setGeminiAnalysis(stationInfoSnapshot.data().geminiAnalysis)
  })
  return unsubscribe
}

export const useScoreStore = defineStore('score', {
  state: () => ({
    totalScore: 0,
    tries: 0,
    step: 0,
    maxTries: 9,
    maxSteps: 3,
    triesPerStep: 3,
    device: getQueryParam('device', false) || '1',
    stationName: `station0${getQueryParam('device', false) || '1'}`,
    replayVideo: null,
    gameStarted: null,
    gameId: null,
    geminiAnalysis: null,
  }),
  actions: {
    setTotalScore(totalScore) {
      this.totalScore = totalScore
    },
    setTries(tries){
      this.tries = tries
    },
    setStep(step){
      this.step = step
    },
    setDevice(device) {
      this.device = device
    },
    setGameStarted(gameStarted) {
      this.gameStarted = gameStarted
    },
    setGameId(gameId) {
      this.gameId = gameId
    },
    setGeminiAnalysis(geminiAnalysis) {
      this.geminiAnalysis = geminiAnalysis
    },
    setVideoReplay(videoReplay) {
      this.replayVideo = videoReplay
    },
    reset() {
      this.totalScore = 0
      this.tries = 0
      this.step = 0
      this.maxTries = 9
      this.maxSteps = 3
      this.triesPerStep = 3
      this.replayVideo = null
      this.gameStarted = false
      this.gameId = null
      this.geminiAnalysis = null
    },
    async getStationInfo() {
      const stationInfoRef = doc(db, 'station-info', this.stationName)
      const stationInfoDocSnap = await getDoc(stationInfoRef)

      if (stationInfoDocSnap.exists()) {
        this.setGameId(stationInfoDocSnap.data().gameId)
        this.setGameStarted(stationInfoDocSnap.data().isRunning)
        this.setVideoReplay(stationInfoDocSnap.data().replayVideo)
        this.setGeminiAnalysis(stationInfoDocSnap.data().geminiAnalysis)
        console.log("gameId:", this.gameId)
      } else {
        console.log("Can't get station info!")
      }
    },
    async getGameInfo() {
      const gameDocRef = doc(db, 'game-sessions', this.gameId)
      const gameDocSnap = await getDoc(gameDocRef)
      if (gameDocSnap.exists()) {
        const gameData = gameDocSnap.data()
        this.setTotalScore(gameData.totalScore)
        this.setTries(gameData.scores.length)
        console.log(`Total score: ${this.totalScore}, tries: ${this.tries}`)
      }
    },
  }
})

export const subscribeToHighlightsChanges = async () => {
  const highlightsStore = useHightlightsStore()
  const scoresCollection = collection(db, 'game-sessions');
  const q = query(scoresCollection, orderBy('totalScore', 'desc'), limit(5));
  const unsubscribe = onSnapshot(q, (querySnapshot) => {
    const scores = [];
    let recordings = [];

    querySnapshot.forEach((doc) => {
      scores.push(doc.data().totalScore);
      recordings = [recordings, ...doc.data().recordingsWithFeedback]
    })
    highlightsStore.setScores(scores)

    recordings.shift()
    if (recordings.length > 0) {
      const randomIndex = Math.floor(Math.random() * recordings.length);
      highlightsStore.setVideo(recordings[randomIndex].video)
    } else {
      highlightsStore.setVideo("")
    }

  })

  return unsubscribe
}

export const useHightlightsStore = defineStore('highlights', {
  state: () => ({
    score1: 0,
    score2: 0,
    score3: 0,
    score4: 0,
    score5: 0,
    video: "",
  }),
  actions: {
    setScores(scores) {
      this.score1 = scores[0] || 0;
      this.score2 = scores[1] || 0;
      this.score3 = scores[2] || 0;
      this.score4 = scores[3] || 0;
      this.score5 = scores[4] || 0;
    },
    setVideo(video) {
      this.video = video;
    },
  }
});

export const useMobileScoreStore = defineStore('mobileScore', {
  state: () => ({
    leaderboard: 0,
    finalScore: 0,
    data: 0,
    description: '',
    videoSrc: '',
  }),
  actions: {
    async setData() {
      const gameId = getQueryParam('gameId', false)
      const scoresCollection = collection(db, 'game-sessions')
      const allGames = await getDocs(scoresCollection)
      const sortedGames = allGames.docs.map(game => ({ id: game.id, ...game.data() })).sort((a, b) => b.totalScore - a.totalScore)

      const leaderboardPos = sortedGames.findIndex(game => game.id === gameId) + 1
      const game = sortedGames[leaderboardPos - 1]

      this.leaderboard = leaderboardPos
      this.finalScore = game.totalScore

      const recordingsWithFeedback = game.recordingsWithFeedback
      let randomRecording = ""
      let randomGeminiFeedback = ""

      if (recordingsWithFeedback.length > 0) {
        const randomIndex = Math.floor(Math.random() * recordingsWithFeedback.length);
        randomRecording = recordingsWithFeedback[randomIndex].video;
        randomGeminiFeedback = recordingsWithFeedback[randomIndex].geminiFeedback;
      }

      this.description = randomGeminiFeedback
      this.videoSrc = randomRecording
    }
  }
})

export const useChromebookStore = defineStore('chromebook', {
  state: () => ({
    finalScore: 0,
    gameId: null,
    videoSrc: '',
  }),
  actions: {
    async setData() {
      const gameId = getQueryParam('gameId', false)
      const scoresCollection = doc(collection(db, 'game-sessions'), gameId)
      const game = await getDoc(scoresCollection)
      const gameData = game.data()
      const recordingsWithFeedback = gameData.recordingsWithFeedback
      let randomRecording = ""

      if (recordingsWithFeedback.length > 0) {
        const randomIndex = Math.floor(Math.random() * recordingsWithFeedback.length);
        randomRecording = recordingsWithFeedback[randomIndex].video;
      }

      this.finalScore = gameData.totalScore
      this.gameId = gameId
      this.videoSrc = randomRecording;
    }
  }
})

window.setScore = (score) => {
  useScoreStore().setScore(score)
}

window.addScore = (score) => {
  useScoreStore().addScore(score)
}

window.setHighlights = (highlights) => {
  useHightlightsStore().setHighlights(highlights)
}

window.setGeminiAnalysis = (text) => {
  useScoreStore().setGeminiAnalysis(text)
}

window.setData = (data) => {
  useMobileScoreStore().setData(data)
}

window.setGameStarted = (gameStarted) => {
  useScoreStore().setGameStarted(gameStarted)
}
