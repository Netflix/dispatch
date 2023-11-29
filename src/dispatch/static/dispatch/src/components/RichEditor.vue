<template>
  <div>
    <editor-content :editor="editor" @keydown.enter.prevent />
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from "vue"
import { Editor, EditorContent } from "@tiptap/vue-3"
import StarterKit from "@tiptap/starter-kit"
import CaseApi from "@/case/api"
import { useStore } from "vuex"

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

const store = useStore()
const editor = ref(null)
const plainTextValue = ref("")

watch(
  () => props.modelValue,
  (value) => {
    const isSame = editor.value?.getHTML() === value

    if (isSame) {
      return
    }

    if (props.title) {
      editor.value?.chain().focus().setContent(`<h2>${value}</h2>`, false).run()
    } else {
      editor.value?.chain().focus().setContent(`${value}`, false).run()
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
      // Get the case details from the Vuex store
      const caseDetails = store.state.case_management.selected
      // Update the title value
      if (props.title) {
        caseDetails.title = plainTextValue.value
      }

      if (props.description) {
        caseDetails.description = plainTextValue.value
      }

      if (props.resolution) {
        caseDetails.resolution = plainTextValue.value
      }
      // Save the changes
      CaseApi.update(caseDetails.id, caseDetails)
    },
    keyboardShortcuts: {
      Enter: () => {}, // Override Enter key to do nothing
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
