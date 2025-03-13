import { defineStore } from "pinia";

export const useScoreStore = defineStore('score', {
  state: () => ({
    score: 0,
    tries: 0,
    step: 0,
    maxTries: 9,
    maxSteps: 3,
    triesPerStep: 3,
    device: '1' // or '2'
  }),
  actions: {
    setScore(score) {
      if (this.tries < this.maxTries) {
        this.tries++

        if(this.tries === this.maxTries) {
          this.step++
        }

        this.score = score
      }
    },
    setDevice(device) {
      this.device = device
    }
  }
})

export const useHightlightsStore = defineStore('highlights', {
  state: () => ({
    score1: 600,
    score2: 500,
    score3: 400,
    score4: 200,
    score5: 100,
    video: "https://storage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
  }),
  actions: {
    setHighlights(highlights) {
      this.score1 = highlights[0]
      this.score2 = highlights[1]
      this.score3 = highlights[2]
      this.score4 = highlights[3]
      this.score5 = highlights[4]
    },
    setVideo(video) {
      this.video = video
    }
  }
})

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

window.setScore = (score) => {
  useScoreStore().setScore(score)
}

window.setHighlights = (highlights) => {
  useHightlightsStore().setHighlights(highlights)
}

window.setText = (text) => {
  useGeminiReportStore().setText(text)
}

window.setData = (data) => {
  useMobileScoreStore().setData(data)
}
