<template>
  <MobileControlCard ref="mobileControlCard" />
</template>

<script setup>
import MobileControlCard from '@/components/mobile-control-card/MobileControlCard.vue'
</script>

<style lang="scss" scoped>
.routes {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
}
</style>
