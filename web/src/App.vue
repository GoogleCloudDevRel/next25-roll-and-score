<template>
  <main class="skeeball">
    <component
      :is="currentRoute"
      ref="currentRouteRef"
    />
  </main>
</template>

<script setup>
import '@/styles/global.scss'

import { ref, computed } from 'vue'

import TvView from './views/TvView.vue'
import ChromebookView from './views/ChromebookView.vue'
import NotFoundView from './views/NotFoundView.vue'
import BigTvView from './views/BigTvView.vue'
import PhoneView from './views/PhoneView.vue'

const routes = {
  '/': BigTvView,
  '/tv': TvView,
  '/chromebook': ChromebookView,
  '/phone': PhoneView,
}

const currentPath = ref(window.location.hash)

window.addEventListener('hashchange', () => {
  currentPath.value = window.location.hash
})

const isIos = /iPad|iPhone/.test(navigator.userAgent)
if (isIos) {
  document.documentElement.classList.add('ios')
}

const currentRoute = computed(() => {
  return routes[currentPath.value.slice(1) || '/'] || NotFoundView
})
</script>
