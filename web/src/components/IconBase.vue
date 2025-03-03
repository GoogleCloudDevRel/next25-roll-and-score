<template>
  <div
    class="iconBase"
    ref="iconBase"
  >
    <component
      :class="{ active: isActive }"
      :is="currentIcon"
      v-if="currentIcon"
    />
    <span v-else>Icon not found</span>
  </div>
</template>

<script setup>
import { ref, shallowRef, watchEffect } from 'vue'
import { defineAsyncComponent } from 'vue'

const props = defineProps({
  variant: {
    type: String,
    required: true,
  },
  active: {
    type: Boolean,
    default: false,
  },
})

const iconBase = shallowRef(null)
const currentIcon = shallowRef(null)
const isActive = ref(false)

watchEffect(async () => {
  try {
    currentIcon.value = defineAsyncComponent(
      () => import(`./icons/Icon${toPascalCase(props.variant)}.vue`),
    )
  } catch (error) {
    console.error(`Failed to load icon: ${props.variant}`, error)
  }
  if (props.active) {
    isActive.value = true
  } else {
    isActive.value = false
  }
})

function toPascalCase(str) {
  return str
    .split('-')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join('')
}
</script>

<style lang="scss" scoped>
.iconBase {
  display: flex;
  align-items: center;
  justify-content: center;
}
.active {
  border-radius: 78px;
  background: linear-gradient(82deg, #e6f4ea -69.88%, $brandGreen 229.35%);
  color: black;
}

.skeeball svg {
  filter: drop-shadow(px-to-vw(5, '4k') px-to-vw(10, '4k') black);
  stroke: black;
  stroke-width: px-to-vw(3, '4k');
}
</style>
