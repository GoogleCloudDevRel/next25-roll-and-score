<script setup>
import { onBeforeUnmount, onMounted, toRaw, watchEffect, ref } from 'vue'
import { Color, Mesh, Program, Triangle, Vec2 } from 'ogl'
import { nextTick } from 'vue'
import gradVertex from './shaders/gradVert.glsl'
import gradFragment from './shaders/gradFrag.glsl'
import { gsap } from '@/utils/gsap'

// Declare a prop for the oglState
const props = defineProps({
  oglState: {
    type: Object,
    required: true,
  },
  bgColor: {
    type: String,
    required: true,
  },
  disk1: {
    type: Object,
    required: true,
  },
  disk2: {
    type: Object,
    required: true,
  },
  disk3: {
    type: Object,
    required: true,
  },
  disk4: {
    type: Object,
    required: true,
  },
  fade: {
    type: Number,
    required: true,
  },
  animate: {
    type: Boolean,
    required: true,
    default: true,
  },
})

let mesh = null

const diskProps = ['disk1', 'disk2', 'disk3', 'disk4']

// Helper function to create disk uniforms
const createDiskUniforms = (gl, diskData) => ({
  color: { value: new Color(diskData.color) },
  center: { value: new Vec2(diskData.center.x, diskData.center.y) },
  radius: { value: diskData.radius },
})

const pauseIdle = ref(false)
const programRef = ref(null)

onMounted(() => {
  const { oglState } = props
  nextTick(() => {
    if (oglState) {
      const { gl, scene } = oglState

      const geometry = new Triangle(gl)

      // Create uniforms object dynamically
      const uniforms = {
        uBGColor: { value: new Color(props.bgColor) },
        uResolution: { value: new Vec2(window.innerWidth, window.innerHeight) },
        uFade: { value: props.fade },
        uTime: { value: 0.0 },
      }

      // Add disk uniforms dynamically
      diskProps.forEach((diskProp) => {
        uniforms[`u${diskProp.charAt(0).toUpperCase()}${diskProp.slice(1)}`] = createDiskUniforms(
          gl,
          props[diskProp],
        )
      })

      const program = new Program(gl, {
        vertex: gradVertex,
        fragment: gradFragment,
        uniforms,
      })

      programRef.value = program

      watchEffect(() => {
        program.uniforms.uBGColor.value = new Color(props.bgColor)
        program.uniforms.uFade.value = props.fade
        // Update disk uniforms dynamically
        diskProps.forEach((diskProp) => {
          const uniformName = `u${diskProp.charAt(0).toUpperCase()}${diskProp.slice(1)}`
          program.uniforms[uniformName].color.value.set(props[diskProp].color)
          program.uniforms[uniformName].center.value.set(
            props[diskProp].center.x,
            props[diskProp].center.y,
          )
          program.uniforms[uniformName].radius.value = props[diskProp].radius
        })
      })

      mesh = new Mesh(gl, { geometry, program })
      mesh.setParent(scene)

      oglState.onRender = (t) => {
        if (!props.animate) return
        if (pauseIdle.value) return
        program.uniforms.uTime.value = t
        // just an example of how to animate the disks
        program.uniforms.uDisk1.center.value.x = (Math.sin(t * 0.8) * 0.5 + 0.5) * 2
        program.uniforms.uDisk3.center.value.y = (Math.cos(t * 0.2) * 0.5 + 0.5) * 0.1
        program.uniforms.uDisk4.center.value.y = (Math.cos(t * 0.2) * 0.5 + 0.5) * 0.1
        program.uniforms.uFade.value = gsap.utils.mapRange(-1, 1, 0.5, 1, Math.sin(t))
      }
      window.addEventListener('resize', () => {
        program.uniforms.uResolution.value.set(window.innerWidth, window.innerHeight)
      })
    }
  })
})

function setState(state) {
  console.log(state)
}

function animateIn() {
  console.log('animateIn')
}

function animateOut() {
  console.log('animateOut')
}

function animateSet() {
  console.log('animateSet')
}

defineExpose({
  setState,
  animateIn,
  animateOut,
  animateSet,
})

onBeforeUnmount(() => {
  const { oglState } = props
  const scene = toRaw(oglState.scene)
  // Clean up the mesh when the child is unmounted (e.g., on HMR)
  scene.traverse((child) => {
    if (child === mesh) {
      child.setParent(null)
    }
  })
})
</script>
