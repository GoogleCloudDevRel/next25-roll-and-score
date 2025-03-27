import UIPaneBase from './UIPaneBase'

export default class UIPane extends UIPaneBase {
  constructor(identifier, jsonPath = null, props = null) {
    super(identifier, jsonPath)
    this.props = props
  }
}
