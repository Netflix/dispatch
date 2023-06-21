<template>
  <editor-content :editor="editor" />
</template>

<script>
import { Editor, EditorContent } from "@tiptap/vue-2"
import StarterKit from "@tiptap/starter-kit"

export default {
  name: "RichResolution",

  components: {
    EditorContent,
  },

  data() {
    return {
      editor: null,
    }
  },

  mounted() {
    this.editor = new Editor({
      content: "<p>I’m running Tiptap with Vue.js. 🎉</p>",
      extensions: [StarterKit],
    })
  },

  beforeDestroy() {
    this.editor.destroy()
  },
}
</script>
