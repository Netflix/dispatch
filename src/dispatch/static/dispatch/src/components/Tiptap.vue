<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from "vue"
import { Editor, EditorContent, BubbleMenu } from "@tiptap/vue-3"
import StarterKit from "@tiptap/starter-kit"

const props = defineProps({
  modelValue: {
    type: String,
    default: "",
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

    editor.value?.chain().focus().setContent(value, false).run()
  }
)

onMounted(() => {
  editor.value = new Editor({
    extensions: [StarterKit],
    content: props.modelValue,
    onUpdate: () => {
      emit("update:modelValue", editor.value?.getHTML())
    },
  })
})

onBeforeUnmount(() => {
  editor.value?.destroy()
})
</script>

<template>
  <div>
    <bubble-menu :editor="editor" v-if="editor">
      <v-btn-toggle v-model="toggle" color="primary" variant="outlined" density="compact">
        <v-btn
          @click="editor.chain().focus().toggleBold().run()"
          :class="{ 'is-active': editor.isActive('bold') }"
        >
          <v-icon size="large">mdi-format-bold</v-icon>
        </v-btn>
        <v-btn
          @click="editor.chain().focus().toggleItalic().run()"
          :class="{ 'is-active': editor.isActive('italic') }"
          icon="mdi-format-italic"
        ></v-btn>
        <v-btn
          @click="editor.chain().focus().toggleStrike().run()"
          :class="{ 'is-active': editor.isActive('strike') }"
          icon="mdi-format-strikethrough-variant"
        ></v-btn>
      </v-btn-toggle>
    </bubble-menu>
    <editor-content :editor="editor" />
  </div>
</template>

<style>
.bubble-menu {
  backdrop-filter: blur(12px) saturate(190%) contrast(50%) brightness(130%) !important;
  border: 0.5px solid rgb(216, 216, 216) !important;
  border-radius: 8px !important;
  box-shadow: rgba(0, 0, 0, 0.09) 0px 3px 12px !important;
  color: rgb(60, 65, 73) !important;
  opacity: 2 !important;
}

input[type="checkbox"] {
  margin-right: 4px;
}
</style>
