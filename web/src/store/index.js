import { getQueryParam } from "@/utils/get-query-param";
import { defineStore } from "pinia";
import { db } from '@/config/firebaseConfig';
import { collection, query, orderBy, limit, onSnapshot } from "firebase/firestore";

// TODO: fetch video replay
const fetchVideoReplay = async () => {
  try {
    const response = await fetch('/api/video-replay');
    const data = await response.json();
    console.log(data)
  } catch (error) {
    console.error('Error fetching video replay:', error);
  } finally {
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
    useScoreStore().setGeminiReport('This is a test report')
  }
}

// TODO: subscribe to score changes
export const subscribeToScoreChanges = async () => {
  const scoresCollection = collection(db, 'games');
  const q = query(scoresCollection, orderBy('totalScore', 'desc'), limit(5));

  const unsubscribe = onSnapshot(q, (querySnapshot) => {
    const scores = [];
    querySnapshot.forEach((doc) => {
      scores.push(doc.data().totalScore);
    })


  });

  return unsubscribe
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
    geminiReport: null,
  }),
  actions: {
    setScore(score) {
      if (this.tries < this.maxTries) {
        this.tries++

        if (this.tries === this.maxTries) {
          this.step++
        }

        this.score = score
      }

      if (this.tries % this.triesPerStep === 0 && this.tries < this.maxTries) {
        fetchGeminiReport()
      }

      if (this.tries === this.maxTries) {
        this.gameStarted = false
        this.geminiReport = null
      }
    },
    addScore(score) {
      if (this.tries < this.maxTries) {
        this.tries++

        if (this.tries === this.maxTries) {
          this.step++
        }

        if (this.tries % this.triesPerStep === 0 && this.tries < this.maxTries) {
          fetchGeminiReport()
        }

        this.score += score
      }

      if (this.tries === this.maxTries) {
        this.gameStarted = false
        this.geminiReport = null
      }
    },
    setDevice(device) {
      this.device = device
    },
    setGameStarted(gameStarted) {
      this.gameStarted = gameStarted
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
      this.device = getQueryParam('device', false) || '1'
      this.replayVideo = null
      this.gameStarted = false
      this.geminiReport = null
    }
  }
})

export const useHightlightsStore = defineStore('highlights', {
  state: () => ({
    score1: 0,
    score2: 0,
    score3: 0,
    score4: 0,
    score5: 0,
    video: "https://storage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
    unsubscribe: null,
  }),
  actions: {
    async fetchTopScores() {
      const scoresCollection = collection(db, 'games');
      const q = query(scoresCollection, orderBy('totalScore', 'desc'), limit(5));

      this.unsubscribe = onSnapshot(q, (querySnapshot) => {
        const scores = [];
        querySnapshot.forEach((doc) => {
          scores.push(doc.data().totalScore);
        })

        this.score1 = scores[0] || 0; // Use 0 as default if scores[0] is undefined
        this.score2 = scores[1] || 0;
        this.score3 = scores[2] || 0;
        this.score4 = scores[3] || 0;
        this.score5 = scores[4] || 0;
      });
    },
    stopFetchingTopScores() {
      if (this.unsubscribe) {
        this.unsubscribe();
      }
    },
    setVideo(video) {
      this.video = "https://www.youtube.com/watch?v=3aoxOtMM2rc";
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
    setData(data) {
      this.leaderboard = data.leaderboard
      this.finalScore = data.finalScore
      this.data = data.data
      this.description = data.description
      this.videoSrc = data.videoSrc
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
