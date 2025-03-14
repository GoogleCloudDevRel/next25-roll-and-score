<template>
  <div
    :class="['qr-code', { 'qr-code--device-1': scoreStore.device === '1' }]"
    ref="qrCodeRef"
  >
    <img
      :src="src"
      alt="QR Code"
    />
    <VText
      text="How it works"
      variant="tv-bold-40"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { generateQR } from '@/utils/qr'
import VText from './VText.vue'
import { useScoreStore } from '@/store'

const qrCodeRef = ref(null)
const scoreStore = useScoreStore()

const props = defineProps({
  value: {
    type: String,
    required: true,
  },
})

const src = ref(null)

onMounted(async () => {
  src.value = await generateQR(props.value)
})
</script>

<style lang="scss">
.qr-code {
  position: absolute;
  top: px-to-vw(100, 4k);
  right: px-to-vw(100, 4k);
  background: #fff;
  border-radius: px-to-vw(32, 4k);
  width: px-to-vw(350, 4k);
  padding: px-to-vw(48, 4k);
  padding-bottom: px-to-vw(32, 4k);
  border: px-to-vw(3, 4k) solid #000;
  box-shadow: px-to-vw(10, 4k) px-to-vw(10, 4k) 0 #000;
  gap: px-to-vw(32, 4k);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  color: $brandBlue;
  text-transform: uppercase;

  &--device-1 {
    top: px-to-vw(100, 4k);
    left: px-to-vw(100, 4k);
    bottom: unset;
    right: unset;
  }

  * {
    white-space: nowrap;
  }

  img {
    width: 100%;
  }
}
</style>
