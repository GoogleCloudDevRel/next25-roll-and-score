import { getQueryParam } from "@/utils/get-query-param";
import { defineStore } from "pinia";
import { db } from '@/config/firebaseConfig';
import { collection, query, orderBy, limit, onSnapshot, doc, updateDoc, getDoc, getDocs } from "firebase/firestore";

export const saveEndGame = async () => {
  if (getQueryParam('manual')) return
  const scoreStore = useScoreStore()
  const gameId = scoreStore.gameId
  const game = doc(collection(db, 'games'), gameId);
  const gameData = await getDoc(game)
  await updateDoc(game, {
    gameStatus: "completed",
    endTime: new Date(),
    totalScore: gameData.data().scores.reduce((acc, curr) => acc + curr, 0)
  })
  const station = doc(collection(db, 'game-stations'), `station0${scoreStore.device}`)
  await updateDoc(station, {
    isRunning: false,
    gameId: null,
  })
  scoreStore.setGameStarted(false)
}

export const subscribeToScoreChanges = async () => {
  const scoreStore = useScoreStore()

  let gameId = null
  let unsubFirebase = null
  const unsubscribe = scoreStore.$subscribe((mutation, state) => {
    if (state.gameId && state.gameId !== gameId) {
      unsubFirebase?.()
      gameId = state.gameId
      unsubFirebase = handleScoreChanges(gameId)
    }
  })

  return unsubscribe
}

export const handleScoreChanges = async (gameId) => {
  const game = doc(collection(db, 'games'), gameId);
  let prevScoreLength = 0
  const unsubscribe = onSnapshot(game, (gameSnapshot) => {
    const gameData = gameSnapshot.data()
    if (gameData.scores.length > prevScoreLength) {
      if (gameData.scores.length - prevScoreLength === 1) {
        useScoreStore().addScore(gameData.scores[gameData.scores.length - 1])
      } else {
        gameData.scores.forEach((score) => {
          useScoreStore().addScore(score)
        })
      }
      prevScoreLength = gameData.scores.length
    }
  })

  return unsubscribe
}

export const subscribeGameStarted = async () => {
  const gameStartedCollection = collection(db, 'gameStations');
  const q = query(gameStartedCollection);

  const scoreStore = useScoreStore()

  const device = Number(scoreStore.device)
  const stationName = `station0${device}`

  const unsubscribe = onSnapshot(q, (querySnapshot) => {
    querySnapshot.forEach((doc) => {
      if (doc.id === stationName) {
        scoreStore.setGameStarted(doc.data().isRunning)
        scoreStore.setGameId(doc.data().gameId)
      }
    })
  })

  return unsubscribe
}

// TODO: fetch video replay
const fetchVideoReplay = async () => {
  try {
    const response = await fetch('/api/video-replay');
    const data = await response.json();
    console.log(data)
  } catch (error) {
    console.error('Error fetching video replay:', error);
  } finally {
    await new Promise((resolve) => setTimeout(resolve, 5000))
    useScoreStore().setVideoReplay('https://storage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4')
  }
}

// TODO: fetch gemini report
const fetchGeminiReport = async () => {
  await fetchVideoReplay()

  try {
    const response = await fetch('/api/gemini-report');
    const data = await response.json();
    console.log(data)
    useScoreStore().setGeminiReport(data.geminiReport);
  } catch (error) {
    console.error('Error fetching gemini report:', error);
  } finally {
    await new Promise((resolve) => setTimeout(resolve, 5000))
    useScoreStore().setGeminiReport('This is a test report')
  }
}

export const useScoreStore = defineStore('score', {
  state: () => ({
    score: 0,
    tries: 0,
    step: 0,
    maxTries: 9,
    maxSteps: 3,
    triesPerStep: 3,
    device: getQueryParam('device', false) || '1',
    replayVideo: null,
    gameStarted: false,
    gameId: null,
    geminiReport: null,
  }),
  actions: {
    setScore(score) {
      this.geminiReport = null
      this.replayVideo = null
      if (this.tries < this.maxTries) {
        this.tries++

        this.score = score
      }

      if (this.tries % this.triesPerStep === 0) {
        this.step++
        console.log(this.step, this.tries)
        if (this.step < this.maxSteps) {
          fetchGeminiReport()
        }
      }
    },
    addScore(score) {
      this.geminiReport = null
      this.replayVideo = null
      if (this.tries < this.maxTries) {
        this.tries++

        this.score += score
      }

      if (this.tries % this.triesPerStep === 0) {
        this.step++
        console.log(this.step, this.tries)
        if (this.step < this.maxSteps) {
          fetchGeminiReport()
        }
      }
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
    setGeminiReport(geminiReport) {
      this.geminiReport = geminiReport
    },
    setVideoReplay(videoReplay) {
      this.replayVideo = videoReplay
    },
    reset() {
      this.score = 0
      this.tries = 0
      this.step = 0
      this.maxTries = 9
      this.maxSteps = 3
      this.triesPerStep = 3
      this.replayVideo = null
      this.gameStarted = false
      this.gameId = null
      this.geminiReport = null
    }
  }
})

export const subscribeToHighlightsChanges = async () => {
  const highlightsStore = useHightlightsStore()
  const scoresCollection = collection(db, 'games');
  const q = query(scoresCollection, orderBy('totalScore', 'desc'), limit(5));
  const unsubscribe = onSnapshot(q, (querySnapshot) => {
    const scores = [];
    querySnapshot.forEach((doc) => {
      scores.push(doc.data().totalScore);
    })
    console.log(scores)
    highlightsStore.setScores(scores)
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
    // TODO: fetch/retrieve video
    video: "https://storage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
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
      this.video = video || "https://www.youtube.com/watch?v=3aoxOtMM2rc";
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
      const scoresCollection = collection(db, 'games')
      const allGames = await getDocs(scoresCollection)
      const sortedGames = allGames.docs.map(game => ({ id: game.id, ...game.data() })).sort((a, b) => b.totalScore - a.totalScore)

      const leaderboardPos = sortedGames.findIndex(game => game.id === gameId) + 1
      const game = sortedGames[leaderboardPos - 1]

      this.leaderboard = leaderboardPos
      this.finalScore = game.totalScore

      // TBD:
      this.description = `Preliminary analysis of "The Maestro's" skeeball session reveals a near-perfect execution of technique and strategy.
      Trajectory analysis indicates consistent arc angles and velocity, resulting in an unprecedented point accumulation.
      Further research is warranted to determine if this level of skeeball proficiency constitutes a new paradigm in competitive arcade gaming.`
      this.description = this.description.replace(/\n/g, '<br>')
      // TBD:
      this.videoSrc = 'https://storage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4'
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
      const scoresCollection = doc(collection(db, 'games'), gameId)
      const game = await getDoc(scoresCollection)
      const gameData = game.data()

      this.finalScore = gameData.totalScore
      this.gameId = gameId
      // TBD:
      this.videoSrc = 'https://storage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4'
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

window.setGeminiReport = (text) => {
  useScoreStore().setGeminiReport(text)
}

window.setData = (data) => {
  useMobileScoreStore().setData(data)
}

window.setGameStarted = (gameStarted) => {
  useScoreStore().setGameStarted(gameStarted)
}
