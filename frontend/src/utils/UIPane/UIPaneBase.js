import { Pane } from 'tweakpane'

export default class UIPaneBase {
  constructor(identifier, jsonPath = null) {
    this.pane = new Pane()
    this.addEventListeners()
    this.paneState = {}
    this.identifier = identifier
    this.isDisposed = false
    if (jsonPath) {
      this.setFromJSON(jsonPath)
    } else {
      this.setStateFromLocalStorage()
    }
  }

  async setFromJSON(filePath) {
    const response = await fetch(filePath)
    const json = await response.json()
    console.log(json)
    this.paneState = json
    this.pane.importState(this.paneState)
  }

  setStateFromLocalStorage() {
    if (localStorage.getItem(`paneState-${this.identifier}`)) {
      this.paneState = JSON.parse(localStorage.getItem(`paneState-${this.identifier}`))
      setTimeout(() => {
        this.pane.importState(this.paneState)
        console.log(this.paneState)
      }, 1)
    }
  }

  showSaveFeedback(type = 'save') {
    const feedback = document.createElement('div')
    feedback.textContent = type === 'save' ? 'State saved' : 'State exported'
    feedback.style.position = 'absolute'
    feedback.style.backgroundColor = 'white'
    feedback.style.padding = '10px'
    feedback.style.borderRadius = '5px'
    feedback.style.fontSize = '12px'
    feedback.style.top = '10px'
    feedback.style.left = '10px'
    feedback.style.color = 'black'
    document.body.appendChild(feedback)
    setTimeout(() => {
      feedback.remove()
    }, 2000)
  }

  addEventListeners() {
    document.addEventListener('keydown', this.handleKeyDown.bind(this))
  }

  handleKeyDown(event) {
    if (this.isDisposed) {
      return
    }
    if (!this.identifier) {
      console.error('identifier required to save or export')
      return
    }
    // save to local storage
    if (event.metaKey && event.key === 's') {
      event.preventDefault()
      this.paneState = this.pane.exportState()
      this.storeState()
      this.showSaveFeedback('save')
    }
    // export to json
    if (event.metaKey && event.key === 'e') {
      event.preventDefault()
      this.exportToJson()
      this.showSaveFeedback('export')
    }
    //export as props
    if (event.metaKey && event.key === 'p') {
      event.preventDefault()
      this.logProps()
      this.showSaveFeedback('props')
    }
  }

  logProps() {
    this.storeState()
    if (!this.props) {
      console.error('props required to export')
      return
    }
    // get values from this.props proxy
    console.log(JSON.parse(JSON.stringify(this.props)))
  }

  exportToJson() {
    this.storeState()
    const json = JSON.stringify(this.paneState)
    const blob = new Blob([json], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${this.identifier}-pane-state.json`
    a.click()
  }

  addBinding(params, name, options = {}) {
    this.pane.addBinding(params, name, options)
    return this
  }

  addFolder(params) {
    this.pane.addFolder(params)
    return this
  }

  on(event, callback) {
    this.pane.on(event, callback)
    return this
  }

  storeState() {
    localStorage.setItem(`paneState-${this.identifier}`, JSON.stringify(this.paneState))
    console.log(localStorage.getItem(`paneState-${this.identifier}`))
  }

  clearState() {
    localStorage.removeItem(`paneState-${this.identifier}`)
    this.paneState = {}
  }

  getState() {
    return this.paneState
  }

  dispose() {
    this.pane.dispose()
    document.removeEventListener('keydown', this.handleKeyDown)
    this.isDisposed = true
  }
}
