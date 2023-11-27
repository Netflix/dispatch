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
})

const emit = defineEmits(["update:modelValue"])

const editor = ref(null)

watch(
  () => props.modelValue,
  (value) => {
    const isSame = editor.value?.getHTML() === value

    if (isSame) {
      return
    }

    console.log("Setting value", value)
    editor.value?.chain().focus().setContent(value, false).run()
  }
)

onMounted(() => {
  editor.value = new Editor({
    extensions: [StarterKit.configure({ heading: { levels: [2] } })],
    content: props.modelValue,
    onUpdate: () => {
      emit("update:modelValue", editor.value?.getHTML())
    },
    keyboardShortcuts: {
      Enter: () => {}, // Override Enter key to do nothing
    },
  })
})

onBeforeUnmount(() => {
  editor.value?.destroy()
})
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
