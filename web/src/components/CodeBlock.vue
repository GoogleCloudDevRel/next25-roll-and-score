<template>
  <div class="codeblock__wrapper">
    <div
      class="codeblock"
      ref="codeBlockRef"
    >
      <div class="codeblock__title">
        <TitleWithIcon
          ref="titleRef"
          icon="gemini"
          textVariant="bold-24"
          title="Code Execution"
        />
      </div>
      <slot></slot>
    </div>
  </div>
</template>

<script setup>
import { nextTick, onMounted, ref, watch } from 'vue'
import Prism from 'prismjs'
import 'prismjs/components/prism-python'
import 'prismjs/themes/prism.css' // You can choose different themes
import 'prismjs/plugins/line-numbers/prism-line-numbers'
import gsap from 'gsap'
import TitleWithIcon from './TitleWithIcon.vue'

const props = defineProps({
  language: {
    type: String,
    default: 'python',
  },
  code: {
    type: String,
    default: '',
  },
})

const codeBlockRef = ref(null)
const titleRef = ref(null)
const codeClass = `language-${props.language}`
const animatedIn = ref(false)
const hookAdded = ref(false)
const tlRef = ref(null)
const highlightCode = () => {
  // Now you can access the slot content
  const codeEl = codeBlockRef.value.querySelector('code')

  if (!hookAdded.value) {
    Prism.hooks.add('after-highlight', function (env) {
      const code = env.element.innerHTML.split('\n')
      env.element.innerHTML = code
        .map(
          (line, index) =>
            /* html */ `<span class="line-wrapper" data-line="${index + 1}"><span class="line-text">${line}</span></span>`,
        )
        .join('\n')
    })
    hookAdded.value = true
  }

  if (codeEl) {
    if (!codeEl.classList.contains(codeClass)) {
      codeEl.classList.add(codeClass)
    }
    Prism.highlightElement(codeEl)
  }
}

onMounted(async () => {
  await nextTick()
  highlightCode()
  titleRef.value.prepare()
  animateSet()
})

// Re-highlight when code changes
watch(
  () => props.code,
  async () => {
    await nextTick()
    highlightCode()
    if (codeBlockRef.value) {
      const preElement = codeBlockRef.value.querySelector('pre')
      console.log('preElement', preElement.scrollHeight)
      preElement.scrollTop = preElement.scrollHeight
    }
  },
  { deep: true },
)

const revealCode = () => {
  const lines = codeBlockRef.value.querySelectorAll('.line-wrapper')

  console.log('revealCode')
  // Reset any existing animations
  gsap.set(lines, {
    '--line-mask': 0,
    '--text-opacity': 0,
    '--line-mask-origin': 'center left',
  })

  gsap.to(lines, {
    '--line-mask': 1,
    duration: 0.5,
    stagger: {
      amount: 0.8,
      from: 'start',
      onComplete: function () {
        const target = this.targets()[0]
        gsap.set(target, { '--line-mask-origin': 'center right' })
        gsap.to(target, {
          '--line-mask': 0,
          '--text-opacity': 1,
          duration: 0.5,
          ease: 'power1.inOut',
        })
      },
    },
    ease: 'power1.inOut',
  })
}

const animateIn = () => {
  if (tlRef.value) {
    tlRef.value.kill()
  }
  const tl = gsap.timeline()
  tlRef.value = tl
  tl.to(codeBlockRef.value, {
    top: 0,
    duration: 1,
    ease: 'power4.out',
    onStart: () => {
      setTimeout(() => {
        revealCode()
        titleRef.value.animateSet()
        titleRef.value.animateIn()
        animatedIn.value = true
      }, 500)
    },
  })
}

const animateOut = () => {
  if (tlRef.value) {
    tlRef.value.kill()
  }
  const tl = gsap.timeline()
  tlRef.value = tl
  tl.to(codeBlockRef.value, {
    top: '100%',
    duration: 1,
    ease: 'power4.out',
  })
}

const animateSet = () => {
  gsap.set(codeBlockRef.value, {
    top: '100%',
  })
  const lines = codeBlockRef.value.querySelectorAll('.line-wrapper')
  gsap.set(lines, {
    '--line-mask': 0,
    '--text-opacity': 0,
    '--line-mask-origin': 'center left',
  })
  titleRef.value.animateSet()
}

defineExpose({
  animateIn,
  animateOut,
  animateSet,
  revealCode,
})
</script>

<style lang="scss">
.codeblock {
  height: 100%;

  &__title {
    border-bottom: 1px solid rgba(38, 53, 47, 0.35);
    @include fluid(
      'padding-bottom',
      (
        xxl: 32px,
        fourk: 114px,
      )
    );
    display: flex;
    justify-content: flex-start;
    align-items: center;
    svg {
      max-width: 80%;
      color: $lightGreen;
    }
  }

  &__wrapper {
    height: 100%;
    width: 100%;
    overflow: hidden;
  }

  @include fluid(
    'border-radius',
    (
      xxl: 31px,
      fourk: 74px,
    )
  );
  @include fluid(
    'padding',
    (
      xxl: 48px 64px,
      fourk: 192px 192px,
    )
  );

  position: relative;
  box-shadow: -135.86px 110.157px 149.079px 0px rgba(0, 0, 0, 0.15);
  width: 100%;
  margin: 0 auto;
  overflow: hidden;
  background: rgba(38, 53, 47, 0.35);
  backdrop-filter: blur(10px);
  color: white;

  &:before {
    @include fluid(
      'border-radius',
      (
        xxl: 32px,
        fourk: 75px,
      )
    );
  }

  @include gradient-border((45deg, rgba(120, 122, 121, 0.35), rgba(38, 53, 47, 0.35)), 1px);

  pre {
    margin: 0 !important;
    padding: 0 !important;
    overflow-x: hidden;
    word-wrap: break-word;
    white-space: pre !important; // Force preserve whitespace
    background: none;
    overflow-y: scroll;
    height: 100%;
    &::-webkit-scrollbar {
      display: none;
    }
  }

  code {
    line-height: 1.5;
    display: block;
    white-space: pre !important; // Force preserve whitespace
    word-wrap: break-word;
    tab-size: 4;
    span {
      white-space: pre !important; // Force preserve whitespace
    }

    .line-wrapper {
      --line-mask: 0;
      --text-opacity: 0;
      --line-mask-origin: center left;
      display: inline-block;
      position: relative;
      line-height: 1.2;
      overflow: hidden;
      border-radius: 3px;

      &::before {
        content: '';
        position: absolute;
        top: calc(50%);
        transform-origin: var(--line-mask-origin);
        transform: translateY(-50%) scaleX(var(--line-mask));
        left: 0;
        width: 100%;
        height: calc(100% + 1px);
        background: linear-gradient(270deg, #123a1d, #34a853 65.38%);
        background-size: 400% 400%;
        animation: gradient 10s linear infinite;
        z-index: 1;
      }

      &:nth-child(odd) {
        &::before {
          background: linear-gradient(-270deg, #206b34, #34a853 65.38%);
        }
      }

      @keyframes gradient {
        0% {
          background-position: 0% 50%;
        }
        50% {
          background-position: 100% 50%;
        }
        100% {
          background-position: 0% 50%;
        }
      }
      .line-text {
        opacity: var(--text-opacity);
      }
    }
  }

  /*
Name: Duotone Sea
Author: by Simurai, adapted from DuoTone themes by Simurai for Atom (http://simurai.com/projects/2016/01/01/duotone-themes)

Conversion: Bram de Haan (http://atelierbram.github.io/Base2Tone-prism/output/prism/prism-base2tone-sea-dark.css)
Generated with Base16 Builder (https://github.com/base16-builder/base16-builder)
*/

  code[class*='language-'],
  pre[class*='language-'] {
    font-family: Consolas, Menlo, Monaco, 'Andale Mono WT', 'Andale Mono', 'Lucida Console',
      'Lucida Sans Typewriter', 'DejaVu Sans Mono', 'Bitstream Vera Sans Mono', 'Liberation Mono',
      'Nimbus Mono L', 'Courier New', Courier, monospace;
    @include fluid(
      'font-size',
      (
        xxl: 18px,
        fourk: 32px,
      )
    );
    line-height: 1.375;
    direction: ltr;
    text-align: left;
    white-space: pre;
    word-spacing: normal;
    word-break: normal;

    -moz-tab-size: 4;
    -o-tab-size: 4;
    tab-size: 4;

    -webkit-hyphens: none;
    -moz-hyphens: none;
    -ms-hyphens: none;
    hyphens: none;
    //background: #1d262f;
    color: #57718e;
    text-shadow: none !important;
  }

  pre > code[class*='language-'] {
    font-size: 1em;
  }

  pre[class*='language-']::-moz-selection,
  pre[class*='language-'] ::-moz-selection,
  code[class*='language-']::-moz-selection,
  code[class*='language-'] ::-moz-selection {
    text-shadow: none;
    background: #004a9e;
  }

  pre[class*='language-']::selection,
  pre[class*='language-'] ::selection,
  code[class*='language-']::selection,
  code[class*='language-'] ::selection {
    text-shadow: none;
    background: #004a9e;
  }

  /* Code blocks */
  pre[class*='language-'] {
    padding: 1em;
    margin: 0.5em 0;
    overflow: auto;
  }

  /* Inline code */
  :not(pre) > code[class*='language-'] {
    padding: 0.1em;
    border-radius: 0.3em;
  }

  .token.comment,
  .token.prolog,
  .token.doctype,
  .token.cdata {
    color: #4a5f78;
  }

  .token.punctuation {
    color: #4a5f78;
  }

  .token.namespace {
    opacity: 0.7;
  }

  .token.tag,
  .token.operator,
  .token.number {
    color: #0aa370;
    background: none;
  }

  .token.property,
  .token.function {
    color: #57718e;
  }

  .token.tag-id,
  .token.selector,
  .token.atrule-id {
    color: #ebf4ff;
  }

  code.language-javascript,
  .token.attr-name {
    color: #7eb6f6;
  }

  code.language-css,
  code.language-scss,
  .token.boolean,
  .token.string,
  .token.entity,
  .token.url,
  .language-css .token.string,
  .language-scss .token.string,
  .style .token.string,
  .token.attr-value,
  .token.keyword,
  .token.control,
  .token.directive,
  .token.unit,
  .token.statement,
  .token.regex,
  .token.atrule {
    color: #47ebb4;
  }

  .token.placeholder,
  .token.variable {
    color: #47ebb4;
  }

  .token.deleted {
    text-decoration: line-through;
  }

  .token.inserted {
    border-bottom: 1px dotted #ebf4ff;
    text-decoration: none;
  }

  .token.italic {
    font-style: italic;
  }

  .token.important,
  .token.bold {
    font-weight: bold;
  }

  .token.important {
    color: #7eb6f6;
  }

  .token.entity {
    cursor: help;
  }

  pre > code.highlight {
    outline: 0.4em solid #34659d;
    outline-offset: 0.4em;
  }

  /* overrides color-values for the Line Numbers plugin
 * http://prismjs.com/plugins/line-numbers/
 */
  .line-numbers.line-numbers .line-numbers-rows {
    border-right-color: #1f2932;
  }

  .line-numbers .line-numbers-rows > span:before {
    color: #2c3847;
  }

  /* overrides color-values for the Line Highlight plugin
* http://prismjs.com/plugins/line-highlight/
*/
  .line-highlight.line-highlight {
    background: rgba(10, 163, 112, 0.2);
    background: -webkit-linear-gradient(left, rgba(10, 163, 112, 0.2) 70%, rgba(10, 163, 112, 0));
    background: linear-gradient(to right, rgba(10, 163, 112, 0.2) 70%, rgba(10, 163, 112, 0));
  }
}
</style>
