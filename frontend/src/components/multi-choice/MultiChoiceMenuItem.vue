<template>
  <div
    class="multiChoiceMenuItemWrapper"
    :class="{ square }"
  >
    <div
      class="multiChoiceMenuItem"
      :class="{ selected }"
      @click="handleClick"
      ref="innerItem"
    >
      <div class="multiChoiceMenuItem__icon">
        <IconBase
          class="multiChoiceMenuItem__icon__icon"
          :variant="icon"
        />
      </div>
      <div class="multiChoiceMenuItem__label text-medium-28">
        <VText
          ref="vtext"
          :text="label"
          :gradient="selected"
          variant="medium-28"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import IconBase from '@/components/IconBase.vue'
import VText from '@/components/VText.vue'
import gsap from 'gsap'
import { ref, onMounted } from 'vue'

const innerItem = ref(null)
const vtext = ref(null)

const props = defineProps({
  value: {
    type: String,
    default: '',
    required: true,
  },
  square: {
    type: Boolean,
    default: false,
  },
  label: {
    type: String,
    default: '',
    required: true,
  },
  icon: {
    type: String,
    default: '',
    required: false,
  },
  solidColor: {
    type: String,
    required: false,
    validator: (value) => ['red', 'greeb', 'yellow', 'blue'].includes(value),
  },
  selected: {
    type: Boolean,
    default: false,
  },
})

onMounted(() => {
  vtext.value.prepare()
})

const animateSet = () => {
  gsap.set(innerItem.value, {
    y: '101%',
  })
  vtext.value.animateSet()
}

const animateIn = (delay) => {
  gsap.to(innerItem.value, {
    y: '0',
    duration: 0.5,
    ease: 'power2.out',
    delay,
  })
  vtext.value.animateIn(delay / 5)
}

const animateOut = (delay) => {
  gsap.to(innerItem.value, {
    y: '101%',
    duration: 0.3,
    ease: 'power2.out',
    delay,
  })
  vtext.value.animateOut(delay - 0.1)
}

const emit = defineEmits(['select'])

const handleClick = () => {
  emit('select', { value: props.value, label: props.label })
}

defineExpose({
  animateIn,
  animateSet,
  animateOut,
})
</script>

<style lang="scss" scoped>
.shopping {
  .multiChoiceMenuItemWrapper {
    .multiChoiceMenuItem {
      background: linear-gradient(
          61.53deg,
          rgba(72, 87, 113, 0.1) -39.88%,
          rgba(137, 166, 215, 0.1) 121.44%
        ),
        linear-gradient(0deg, rgba(37, 49, 75, 0.15), rgba(37, 49, 75, 0.15));

      &__label {
        color: #fff;
      }

      &__icon {
        color: linear-gradient(207.21deg, #4285f4 -27.19%, #d9e7ff 175.32%);
        justify-content: flex-start;
        align-items: flex-start;
      }

      &.selected {
        background: linear-gradient(
          50.24deg,
          rgba(66, 133, 244, 0.1) -4.95%,
          rgba(217, 231, 255, 0.2) 117.88%
        );
        @include gradient-border((45deg, #ffffff, #4285f4), 1px);
      }
    }
  }
}

.kayak {
  .multiChoiceMenuItemWrapper {
    .multiChoiceMenuItem {
      background: linear-gradient(
          215.08deg,
          rgba(48, 50, 57, 0.32) 23.97%,
          rgba(75, 137, 93, 0.1664) 120.38%
        ),
        linear-gradient(0deg, rgba(0, 0, 0, 0.3), rgba(0, 0, 0, 0.3));

      @include gradient-border((45deg, #4e4e4e, #e1e1e1), 1px);

      &.selected {
        background: linear-gradient(
            215.08deg,
            rgba(48, 50, 57, 0.32) 23.97%,
            rgba(75, 137, 93, 0.1664) 120.38%
          ),
          linear-gradient(0deg, rgba(0, 0, 0, 0), rgba(0, 0, 0, 0));
        @include gradient-border((45deg, #e6f4ea, #34a853), 1px);
      }

      &__icon {
        color: #1c1b1f;
        background: linear-gradient(82.43deg, #e6f4ea -69.88%, #34a853 229.35%);
      }

      &__label {
        color: #cecece;
      }
    }
  }
}

.multiChoiceMenuItemWrapper {
  overflow: hidden;
  &.square {
    aspect-ratio: 1;
    width: 100%;
    height: auto;
  }
}

.multiChoiceMenuItem {
  padding: px-to-vh(32, 'chromebook');
  border-radius: px-to-vh(24, 'chromebook');
  border-width: 1px;
  justify-content: space-between;
  flex-direction: column;
  display: flex;
  height: 100%;
  box-sizing: border-box;
  cursor: pointer;
  transition: background 0.3s linear;

  &:before {
    border-radius: px-to-vh(24, 'chromebook');
    transition: all 0.9s linear;
  }

  // base styles

  &__icon {
    width: px-to-vh(48, 'chromebook');
    height: px-to-vh(48, 'chromebook');
    border-radius: 100%;
    display: flex;
    align-items: center;
    justify-content: center;

    &__icon {
      width: px-to-vh(29, 'chromebook') !important;
      height: px-to-vh(29, 'chromebook') !important;
      svg {
        width: 100% !important;
        height: 100% !important;
      }
    }
  }

  &__label {
    font-size: px-to-vh(28, 'chromebook') !important;
    line-height: 1 !important;
    color: #bebebe;

    .VText {
      font-size: px-to-vh(28, 'chromebook') !important;
    }
  }
}
</style>
