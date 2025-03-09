import { defineStore } from "pinia";
import { db } from '@/config/firebaseConfig'; 
import { collection, query, orderBy, limit, onSnapshot } from 'firebase/firestore';

export const useScoreStore = defineStore('score', {
  state: () => ({
    score: 0,
    progress: 0,
    maxTries: 5,
  }),
  actions: {
    setScore(score, progress = null) {
      if (this.progress < this.maxTries) {
        this.score = score
        if (typeof progress === 'number') {
          this.progress = progress
        } else {
          this.progress++
        }
      }
    },
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
    fetchTopScores() {
      const scoresCollection = collection(db, 'gameScores');
      const q = query(scoresCollection, orderBy('score', 'desc'), limit(5));

      this.unsubscribe = onSnapshot(q, (querySnapshot) => {
        const scores = [];
        querySnapshot.forEach((doc) => {
          scores.push(doc.data().score);
        })

        this.score1 = scores[0] || 0; // Use 0 as default if scores[0] is undefined
        this.score2 = scores[1] || 0;
        this.score3 = scores[2] || 0;
        this.score4 = scores[3] || 0;
        this.score5 = scores[4] || 0;
      });
    },
    unsubscribeFromData() {
      if (this.unsubscribe) {
        this.unsubscribe();
      }
    },
    setVideo(video) {
      this.video = "https://www.youtube.com/watch?v=3aoxOtMM2rc";
    },
  },
  onDispose() {
    this.unsubscribeFromData();
  },
});

export const useGeminiReportStore = defineStore('geminiReport', {
  state: () => ({
    text: 'Is that the Hulk playing?! Try throwing a little more gently, and slightly more to the right!',
  }),
  actions: {
    setText(text) {
      this.text = text
    }
  }
})

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

// window.setScore = (score) => {
//   useScoreStore().setScore(score)
// }

// window.setHighlights = (highlights) => {
//   useHightlightsStore().setHighlights(highlights)
// }

// window.setText = (text) => {
//   useGeminiReportStore().setText(text)
// }

// window.setData = (data) => {
//   useMobileScoreStore().setData(data)
// }
