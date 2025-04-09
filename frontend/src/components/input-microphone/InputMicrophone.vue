<template>
  <div class="input-microphone-wrapper">
    <div
      ref="containerRef"
      class="input-microphone"
    >
      <div class="input-microphone__text">
        <IconGemini
          ref="iconGeminiRef"
          class="input-microphone__gemini"
        />
        <p
          ref="textRef"
          class="text-body-24"
        >
          {{ speechText || props.cta }}
        </p>
      </div>
      <IconBase
        v-if="!ended"
        ref="iconRecordRef"
        @click="handleClick"
        class="input-microphone__button"
        variant="mic"
        :active="recording"
      />
      <IconBase
        v-else
        ref="iconSendRef"
        @click="handleEndedClick"
        class="input-microphone__button"
        variant="send"
        :active="ended"
      />
    </div>
  </div>
</template>

<script setup>
import IconBase from '../IconBase.vue'
const emit = defineEmits([
  'input-microphone-clicked',
  'input-microphone-result',
  'input-microphone-end',
  'input-microphone-start',
])

const props = defineProps({
  cta: {
    type: String,
    default: '',
  },
  language: {
    type: String,
    default: 'en-US',
  },
})

import { ref, onMounted } from 'vue'
import IconGemini from '../icons/IconGemini.vue'
import gsap from 'gsap'
const currentCta = ref('')
const speechText = ref('')
const recognition = ref(null)
const recording = ref(false)
const ended = ref(false)
const containerRef = ref(null)
const iconGeminiRef = ref(null)
const textRef = ref(null)
const iconRecordRef = ref(null)
const iconSendRef = ref(null)
const tlRef = gsap.timeline()
const initRecorder = () => {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
  if (!SpeechRecognition) {
    console.error('SpeechRecognition not supported')
    return
  }
  recognition.value = new SpeechRecognition()
  recognition.value.lang = props.language
  recognition.value.interimResults = true
  recognition.value.continuous = true
  initRecognitionEvents()
}

const initRecognitionEvents = () => {
  recognition.value.onstart = () => {
    recording.value = true
    speechText.value = 'Listening...'
    emit('input-microphone-start')
  }

  recognition.value.onend = () => {
    ended.value = true
    emit('input-microphone-end')
  }

  recognition.value.onresult = (event) => {
    let text = ''
    for (let i = event.resultIndex; i < event.results.length; ++i) {
      if (event.results[i].isFinal) {
        text = event.results[i][0].transcript
      } else {
        text += event.results[i][0].transcript
      }
    }
    handleOnResult(text)
  }
}

const handleOnResult = (text) => {
  speechText.value = text
  emit('input-microphone-result', { speechText: text })
}

const handleEndedClick = () => {
  // send the data!!\
  speechText.value = props.cta
  ended.value = false
}

const handleClick = () => {
  recording.value = !recording.value
  console.log('recording.value', recording.value)
  //emit('input-microphone-clicked', { recordingState: recording.value })
  recording.value ? recognition.value.start() : recognition.value.stop()
}

const animateIn = () => {
  const tl = gsap.timeline()
  tlRef.value = tl
  tl.to(containerRef.value, {
    opacity: 1,
    duration: 1,
    z: 0,
    ease: 'power2.out',
  })
    .to(
      iconGeminiRef.value.$el,
      {
        opacity: 1,
        duration: 2,
        ease: 'power2.inOut',
      },
      '<',
    )
    .to(
      textRef.value,
      {
        opacity: 1,
        duration: 2,
      },
      '-=1',
    )
    .to(
      iconRecordRef.value.$el,
      {
        opacity: 1,
        duration: 2,
        ease: 'power2.inOut',
      },
      '<',
    )
}

const animateOut = () => {
  if (tlRef.value) {
    tlRef.value.kill()
  }
  tlRef.value = gsap.timeline()
  tlRef.value.to(containerRef.value, {
    opacity: 0,
    duration: 1,
  })
  tlRef.value.to(iconGeminiRef.value.$el, {
    opacity: 0,
    duration: 1,
  })
  tlRef.value.to(textRef.value, {
    opacity: 0,
  })
}
const animateSet = () => {
  if (tlRef.value) {
    tlRef.value.kill()
  }
  gsap.set(containerRef.value, {
    opacity: 0,
    z: -100,
  })
  gsap.set(iconGeminiRef.value.$el, {
    opacity: 0,
  })
  gsap.set(textRef.value, {
    opacity: 0,
  })
  gsap.set(iconRecordRef.value.$el, {
    opacity: 0,
  })
}

defineExpose({
  animateIn,
  animateOut,
  animateSet,
})

// Initialize on component creation
onMounted(() => {
  animateSet()
  currentCta.value = props.cta
  initRecorder()
})
</script>

<style lang="scss" scoped>
.input-microphone-wrapper {
  position: relative;
  display: flex;
  flex-direction: row;
  align-items: center;
  perspective: 1000px;
  transform-style: preserve-3d;
}
.input-microphone {
  position: relative;
  display: flex;
  flex-direction: row;
  width: 100%;
  transform-style: preserve-3d;

  &__button {
    cursor: pointer;
    position: absolute;
    right: 48px;
    top: 50%;
    transform: translate(50%, -50%);
    color: $darkmode;
  }

  &__gemini {
    flex-shrink: 0;
    margin-right: 16px;
  }

  &__text {
    display: flex;
    flex-direction: row;
    align-items: center;
    color: $darkmode;
    font-size: 32px;
    width: 100%;
    padding: 28px 78px 28px 48px;
    border-radius: 2em;
    position: relative;
    background: rgba(230, 244, 234, 0.1);
    backdrop-filter: blur(10px);

    &:before {
      content: '';
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 100%;
      height: calc(100% - 1px);
      border-radius: 70px;
      border: 1px solid transparent;
      background: linear-gradient(45deg, #e1e1e1, #333333) border-box;
      mask:
        linear-gradient(#000 0 0) padding-box,
        linear-gradient(#000 0 0);
      mask-composite: exclude;
    }
  }
}
</style>
