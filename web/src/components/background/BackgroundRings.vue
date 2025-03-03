<template>
  <div />
</template>

<script setup>
import { onBeforeUnmount, onMounted, toRaw, watch } from 'vue'
import { Color, Mesh, Plane, Program, Texture } from 'ogl'
import { nextTick } from 'vue'
import ringVertex from './shaders/ringVert.glsl'
import ringFragment from './shaders/ringFrag.glsl'
import starFragment from './shaders/starFrag.glsl'
import { gsap, Cubic } from '@/utils/gsap'
import { convertFragmentTo300, convertVertexTo300, getHeightFromCamera } from '@/utils/webgl'
import colors from '@/utils/colors'
import geminiMSDF from '@/assets/gemini_msdf.png'
import { useRouteManager } from '@/router/useRouteManager'

const { isTransitioning, isLanding } = useRouteManager()

// Declare a prop for the oglState
const props = defineProps({
  oglState: {
    type: Object,
    required: true,
  },
  grayscale: {
    type: Boolean,
    default: false,
  },
})

const ringColors = [colors.brandRed, colors.brandGreen, colors.brandYellow, colors.brandBlue]

const STAR_POSITIONS = [
  { x: -0.9, y: 0.85, z: -1 },
  { x: 0.67, y: -0.54, z: -0.9 },
  { x: -0.4, y: -0.91, z: -0.8 },
  { x: 0.45, y: 0.7, z: -0.7 },
  { x: -0.75, y: 0.24, z: -0.6 },
  { x: 0.21, y: -0.78, z: -0.5 },
  { x: -0.95, y: -0.25, z: -0.3 },
  { x: 0.05, y: 0.96, z: -0.2 },
  { x: 0.8, y: -0, z: -0 },
]

const bgColor = new Color('#0E0D0D')

let meshes
let starMeshes

onMounted(() => {
  const { oglState } = props
  nextTick(() => {
    if (oglState) {
      const { gl, scene, renderer, camera } = oglState

      const geometry = new Plane(gl)

      const uTime = { value: 0 }
      meshes = Array.from({ length: 4 }).map((_, i, { length }) => {
        const c = ringColors[i % ringColors.length]
        const program = new Program(gl, {
          vertex: renderer.isWebgl2 ? convertVertexTo300(ringVertex) : ringVertex,
          fragment: renderer.isWebgl2 ? convertFragmentTo300(ringFragment) : ringFragment,
          uniforms: {
            uColor: {
              value: new Color(c),
            },
            bgColor: {
              value: bgColor,
            },
            uBorder: {
              value: 0,
            },
            uGrayscale: {
              value: props.grayscale ? 1 : 0,
            },
            uGrayscaleColor: {
              value: new Color('#2A2A2A'),
            },
            uTime,
          },
          depthWrite: false,
          depthTest: false,
          transparent: true,
        })

        const mesh = new Mesh(gl, { geometry, program })
        mesh.setParent(scene)
        mesh.renderOrder = length - i
        return mesh
      })

      const img = new Image()
      img.src = geminiMSDF
      img.onload = () => (texture.image = img)

      let texture = new Texture(gl)

      starMeshes = STAR_POSITIONS.map((_, i, { length }) => {
        const program = new Program(gl, {
          vertex: renderer.isWebgl2 ? convertVertexTo300(ringVertex) : ringVertex,
          fragment: renderer.isWebgl2 ? convertFragmentTo300(starFragment) : starFragment,
          uniforms: {
            tMap: {
              value: texture,
            },
            uAlpha: {
              value: 0.5,
            },
          },
          depthWrite: false,
          depthTest: false,
          transparent: true,
        })

        const mesh = new Mesh(gl, { geometry, program })
        mesh.setParent(scene)
        mesh.position.z = STAR_POSITIONS[i].z * 7.5 - 15
        mesh.renderOrder = length - i + 10
        mesh.__mapper = gsap.utils.mapRange(
          STAR_POSITIONS[i].z * 7.5 - 15,
          STAR_POSITIONS[i].z * 7.5 - 10,
          0,
          1,
        )
        return mesh
      })

      gl.clearColor(bgColor.r, bgColor.g, bgColor.b, 1)

      let progress = 0
      const speed = { value: 0 }
      let viewHeight
      let viewWidth
      let maxSide

      window.addEventListener('resize', onResize)
      function onResize() {
        viewHeight = getHeightFromCamera(camera)
        viewWidth = viewHeight * camera.aspect
        maxSide = Math.max(viewHeight, viewWidth)
      }
      onResize()

      oglState.onRender = (time) => {
        uTime.value = time
        const v = (speed.value % 2) / 2
        const p = Math.min(v * 2, 2 * (1 - v))

        meshes.forEach((mesh, i, { length }) => {
          progress = (time * 0.3 + i / 2 + speed.value) % 2
          if (progress < 0.1 && mesh.__pristine) {
            mesh.renderOrder += length - i
            mesh.__pristine = false
          }

          if (progress > 1.9) {
            mesh.__pristine = true
          }

          mesh.scale.x = progress * maxSide
          mesh.scale.y = progress * maxSide
          mesh.program.uniforms.uBorder.value = Cubic.easeOut(progress / 2)
        })

        starMeshes.forEach((mesh, i, { length }) => {
          if (mesh.position.z > camera.position.z) {
            mesh.position.z = STAR_POSITIONS[i].z * 7.5 - 15
            mesh.renderOrder += length + 10
          }

          mesh.scale.x = Cubic.easeOut(Math.min(mesh.__mapper(mesh.position.z), 1.0))
          mesh.scale.y = mesh.scale.x
          mesh.position.x = STAR_POSITIONS[i].x * (maxSide / 2)
          mesh.position.y = STAR_POSITIONS[i].y * (maxSide / 2)
          mesh.position.z += 0.05 + 0.5 * p
        })
      }

      function updateGrayscale(value) {
        meshes.forEach((mesh) => {
          gsap.to(mesh.program.uniforms.uGrayscale, {
            value: value ? 1 : 0,
            duration: 2,
            ease: 'cubic.inOut',
          })
          gsap.to(speed, {
            value: speed.value + 2,
            duration: 3,
            ease: 'cubic.inOut',
          })
        })
      }

      // watch(() => props.grayscale, updateGrayscale)

      watch(
        () => isTransitioning.value,
        () => {
          if (!isTransitioning.value) return
          updateGrayscale(!isLanding.value)
        },
      )
    }
  })
})

onBeforeUnmount(() => {
  const { oglState } = props
  const scene = toRaw(oglState.scene)
  meshes.forEach((mesh) => {
    scene.removeChild(mesh)
  })
  starMeshes.forEach((mesh) => {
    scene.removeChild(mesh)
  })
})
</script>
