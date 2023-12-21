<template>
  <div>
    <editor-content :editor="editor" @keydown.enter.prevent />
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from "vue"
import { Editor, EditorContent } from "@tiptap/vue-3"
import StarterKit from "@tiptap/starter-kit"

const props = defineProps({
  modelValue: {
    type: String,
    default: "",
  },
  title: {
    type: Boolean,
    default: false,
  },
  description: {
    type: Boolean,
    default: false,
  },
  resolution: {
    type: Boolean,
    default: false,
  },
})

const editor = ref(null)
const plainTextValue = ref("")
const emit = defineEmits(["update:modelValue"])

const userIsTyping = ref(false)

const handleKeyDown = () => {
  userIsTyping.value = true
}

const handleBlur = () => {
  userIsTyping.value = false
}

watch(
  () => props.modelValue,
  (value) => {
    if (userIsTyping.value) {
      return
    }

    const isSame = editor.value?.getHTML() === value

    if (isSame) {
      return
    }

    if (props.title) {
      editor.value?.chain().focus().setContent(`<h2>${value}</h2>`, false).run()
    } else {
      editor.value?.chain().setContent(`${value}`, false).run()
    }
  }
)

onMounted(() => {
  editor.value = new Editor({
    extensions: [StarterKit.configure({ heading: { levels: [2] } })],
    content: props.modelValue,
    onUpdate: () => {
      let content = editor.value?.getHTML()
      // remove the HTML tags
      plainTextValue.value = content.replace(/<\/?[^>]+(>|$)/g, "")
      // Emitting the updated plain text
      emit("update:modelValue", plainTextValue.value)
    },
    keyboardShortcuts: {
      Enter: () => {}, // Override Enter key to do nothing
    },
    editorProps: {
      handleKeyDown,
      handleBlur,
    },
  })
})

onBeforeUnmount(() => {
  editor.value?.destroy()
})

// Expose plainTextValue for parent component to use
defineExpose({ plainTextValue })
</script>

<style lang="scss">
/* Basic editor styles */
.tiptap {
  > * + * {
    margin-top: 0.75em;
  }
}

input[type="checkbox"] {
  margin-right: 4px;
}
</style>
