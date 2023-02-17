<template>
  <div class="text-box">
    <v-card>
      <v-card-text>
        <div id="editor" style="height: 400px"></div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
import { mapMutations, mapGetters } from "vuex"
import loader from "@monaco-editor/loader"

export default {
  name: "PlaygroundTextBox",
  async mounted() {
    loader.init().then((monaco) => {
      const editorOptions = {
        language: "json",
        minimap: { enabled: false },
      }
      const modelUri = monaco.Uri.parse("inmemory://playground")
      const model = monaco.editor.createModel("", "json", modelUri)
      const editor = monaco.editor.create(document.getElementById("editor"), editorOptions, {
        model,
      })
      this.editor = editor
      this.monaco = monaco

      this.editor.onDidPaste(() => {
        this.updateDecorations(this.pattern)
      })
    })
  },
  data() {
    return {
      decoration: [],
      noHighlight: [],
      edit: null,
      monaco: null,
      mode: null,
    }
  },
  computed: mapGetters("playground", ["pattern"]),
  watch: {
    pattern(pattern) {
      if (pattern) {
        this.updatePattern(pattern)
        this.updateDecorations(pattern)
      }
    },
  },
  methods: {
    ...mapMutations("playground", ["updatePattern"]),
    updateDecorations(pattern) {
      if (!pattern) {
        // Check twice because we'll loop forever if we process a null pattern
        return
      }
      this.decoration = this.editor.deltaDecorations(this.decoration, this.noHighlight)
      const model = this.editor.getModel()
      const text = model.getValue()
      const regex = new RegExp(pattern, "g")
      const found = []
      let match = regex.exec(text)
      while (match !== null) {
        found.push(match)
        match = regex.exec(text)
      }

      if (found.length === 0) {
        return
      }

      const ranges = found.map((match) => {
        const startPosition = model.getPositionAt(match.index)
        const endPosition = model.getPositionAt(match.index + match[0].length)
        return new this.monaco.Range(
          startPosition.lineNumber,
          startPosition.column,
          endPosition.lineNumber,
          endPosition.column
        )
      })
      const decorationOptions = {
        isWholeLine: false,
        className: "highlight",
      }

      // Add the decoration to the editor
      this.decoration = this.editor.deltaDecorations(
        this.decoration,
        ranges.map((range) => {
          return {
            range: range,
            options: decorationOptions,
          }
        })
      )
    },
  },
}
</script>

<style>
.highlight {
  background-color: rgb(205, 238, 237);
}
</style>
