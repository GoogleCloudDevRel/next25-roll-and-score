import { defineStore } from "pinia";

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
    score1: 5910,
    score2: 4678,
    score3: 3456,
    score4: 2345,
    score5: 1234,
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

window.setScore = (score) => {
  useScoreStore().setScore(score)
}

window.setHighlights = (highlights) => {
  useHightlightsStore().setHighlights(highlights)
}

window.setText = (text) => {
  useGeminiReportStore().setText(text)
}


