<template>
  <div class="ogl-container">
    <canvas
      ref="canvas"
      class="ogl-canvas"
    ></canvas>
    <slot :oglState="oglState"></slot>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref, reactive } from 'vue'
import { Renderer, Transform, Camera } from 'ogl'
import { gsap } from '@/utils/gsap'

const props = defineProps({
  dpr: Number,
})

const canvas = ref(null)

const oglState = reactive({
  renderer: null,
  gl: null,
  scene: null,
  camera: null,
  onRender: null,
  cleanup: null,
})

let raf = null

function cleanup() {
  cancelAnimationFrame(raf)
  window.removeEventListener('resize', onResize)
  if (oglState.gl) {
    const ext = oglState.gl.getExtension('WEBGL_lose_context')
    if (ext) {
      ext.loseContext()
      console.log('WebGL context lost for cleanup.')
    }
  }
}

function initOGL() {
  oglState.renderer = new Renderer({
    canvas: canvas.value,
    alpha: true,
    antialias: true,
    dpr: Math.min(props.dpr, 2) || Math.min(window.devicePixelRatio, 1),
  })
  oglState.gl = oglState.renderer.gl
  oglState.scene = new Transform()
  oglState.camera = new Camera(oglState.gl, { fov: 45 })
  oglState.camera.position.set(0, 0, 5)
  oglState.renderer.setSize(window.innerWidth, window.innerHeight)

  gsap.ticker.add((time) => {
    const { scene, camera, renderer } = oglState
    renderer.render({ scene, camera })
    if (oglState.onRender) {
      oglState.onRender(time)
    }
  })
}

function onResize() {
  if (oglState.renderer && oglState.camera) {
    oglState.renderer.setSize(window.innerWidth, window.innerHeight)
    oglState.camera.perspective({
      aspect: oglState.gl.canvas.width / oglState.gl.canvas.height,
    })
  }
}

onMounted(() => {
  initOGL()
  onResize()
  oglState.cleanup = cleanup
  window.addEventListener('resize', onResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', onResize)
})
</script>

<style lang="scss" scoped>
scoped > .ogl-container {
  width: 100%;
  height: 100%;
  position: relative;
  background-color: #000;
}

.ogl-canvas {
  display: block;
  width: 100%;
  height: 100%;
}
</style>
