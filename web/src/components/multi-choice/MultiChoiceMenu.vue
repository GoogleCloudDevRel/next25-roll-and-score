<template>
  <div
    class="multichoicemenu"
    :style="{ 'grid-template-columns': `repeat(${columns}, 1fr)` }"
  >
    <MultiChoiceMenuItem
      v-for="item in items"
      :key="item.value"
      :label="item.label"
      :icon="item.icon"
      :value="item.value"
      :selected="selectedItemId === item.value"
      :square="square"
      @select="handleItemSelect"
      ref="menuItems"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import MultiChoiceMenuItem from './MultiChoiceMenuItem.vue'
const menuItems = ref([])

defineProps({
  items: {
    type: Array,
    required: true,
    validator: (value) => value.every((item) => 'label' in item),
  },
  columns: {
    type: Number,
    default: 4,
    validator: (value) => value > 0,
  },
  square: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['selection-change'])

// Track selected item
const selectedItemId = ref(null)

// Handle item selection
const handleItemSelect = ({ value, label }) => {
  selectedItemId.value = value
  emit('selection-change', { value, label })
}

onMounted(() => {
  menuItems.value.forEach((item) => {
    item.animateSet()
  })
})

const animateIn = () => {
  menuItems.value.forEach((item, index) => {
    item.animateIn(index * 0.1)
  })
}

const animateOut = () => {
  menuItems.value
    .slice()
    .reverse()
    .forEach((item, index) => {
      item.animateOut(index * 0.05)
    })
}

const animateSet = () => {
  menuItems.value.forEach((item) => {
    item.animateSet()
  })
}

defineExpose({
  animateIn,
  animateOut,
  animateSet,
})
</script>

<style lang="scss">
.multichoicemenu {
  display: grid;
  gap: px-to-vh(16, 'chromebook');
  width: 100%;
}
</style>
