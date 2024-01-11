<template>
  <div>
    <editor-content :editor="editor" @keydown.enter.prevent />
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from "vue"
import Placeholder from "@tiptap/extension-placeholder"
import { Editor, EditorContent } from "@tiptap/vue-3"
import StarterKit from "@tiptap/starter-kit"

const props = defineProps({
  content: {
    type: String,
    default: "",
  },
  placeholder: {
    type: String,
    default: "",
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
  () => props.content,
  (value) => {
    if (userIsTyping.value) {
      return
    }

    const isSame = editor.value?.getHTML() === value

    if (isSame) {
      return
    }

    editor.value?.chain().setContent(`${value}`, false).run()
  }
)

onMounted(() => {
  editor.value = new Editor({
    extensions: [
      StarterKit.configure({ heading: { levels: [1, 2, 3, 4, 5, 6] } }),
      Placeholder.configure({
        // Use a placeholder:
        placeholder: props.placeholder,
        // Use different placeholders depending on the node type:
        // placeholder: ({ node }) => {
        //   if (node.type.name === 'heading') {
        //     return 'What’s the title?'
        //   }

        //   return 'Can you add some further context?'
        // },
      }),
    ],
    content: props.content,
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

  code {
    background-color: rgba(#616161, 0.1);
    color: #616161;
  }

  &:focus {
    outline: none;
  }
}

.tiptap p.is-editor-empty:first-child::before {
  content: attr(data-placeholder);
  float: left;
  color: #adb5bd;
  pointer-events: none;
  height: 0;
}

.content {
  padding: 1rem 0 0;

  h3 {
    margin: 1rem 0 0.5rem;
  }

  pre {
    border-radius: 5px;
    color: #333;
  }

  code {
    display: block;
    white-space: pre-wrap;
    font-size: 0.8rem;
    padding: 0.75rem 1rem;
    background-color: #e9ecef;
    color: #495057;
  }
}
</style>
