<template>
  <div class="playground-editor">
    <v-card style="height: 600px" elevation="4" outlined>
      <v-card-text>
        <div id="playground-editor" style="height: 560px"></div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
import { mapMutations, mapGetters } from "vuex"
import loader from "@monaco-editor/loader"
import jsonpath from "jsonpath"

export default {
  name: "PlaygroundTextBox",
  props: {
    text: {
      type: String,
      required: false,
    },
  },
  created() {
    loader.init().then((monaco) => {
      const editorOptions = {
        minimap: { enabled: false },
        renderLineHighlight: "none",
        language: "json",
        value: this.getDefaultValue(),
      }
      // Create a unique URI for the in-memory model
      const modelUri = monaco.Uri.parse("inmemory://playground")
      // Create the model with an osquery log as the initial value
      const model = monaco.editor.createModel(this.getDefaultValue(), "json", modelUri)
      // Create the editor and pass the model to the options
      const editor = monaco.editor.create(
        document.getElementById("playground-editor"),
        editorOptions,
        {
          model,
        }
      )
      // Store the references to the model and editor
      this.model = model
      this.editor = editor
      this.monaco = monaco

      // Register an event listener for when the content of the model changes
      this.editor.onDidChangeModelContent(() => {
        // Call the updateDecorations method and pass the current pattern and jpath
        this.updateDecorations(this.pattern, this.jpath)
      })
    })
  },
  beforeDestroy() {
    this.editor.dispose()
    this.model.dispose()
  },
  data() {
    return {
      decoration: [],
      noHighlight: [],
      edit: null,
      monaco: null,
      model: null,
    }
  },
  computed: mapGetters("playground", ["pattern", "jpath"]),
  watch: {
    pattern(newPattern) {
      if (!newPattern && !this.jpath) {
        this.clearAllDecorations()
      }
      if (newPattern) {
        this.updatePattern(newPattern)
        this.updateDecorations(newPattern, this.jpath)
      }
    },
    jpath(newJsonPath) {
      if (!newJsonPath && !this.pattern) {
        this.clearAllDecorations()
      }
      if (newJsonPath) {
        this.updateJsonPath(newJsonPath)
        this.updateDecorations(this.pattern, newJsonPath)
      }
    },
    text(newText) {
      this.editor.getModel().setValue(newText)
    },
  },
  methods: {
    ...mapMutations("playground", ["updatePattern", "updateJsonPath"]),
    /**
     * Update the decorations in the editor
     *
     * @param {string} pattern The pattern to match against
     * @param {string} jpath The jpath to use
     */
    updateDecorations(pattern, jpath) {
      if (!pattern && !jpath) {
        return
      }

      const model = this.editor.getModel()
      const editorText = model.getValue()
      if (!editorText) {
        return
      }
      this.clearAllDecorations()

      let regex = null
      if (pattern) {
        regex = new RegExp(pattern, "g")
      }

      const matches = []

      if (jpath) {
        const jpathMatches = jsonpath.query(JSON.parse(editorText), jpath)
        if (jpathMatches.length) {
          jpathMatches.forEach((jpathMatch) => {
            if (!pattern) {
              matches.push(jpathMatch)
            } else {
              let matchResult = regex.exec(jpathMatch)
              while (matchResult) {
                matches.push({
                  value: matchResult[0],
                  index: editorText.indexOf(jpathMatch) + matchResult.index,
                })
                matchResult = regex.exec(jpathMatch)
              }
              if (!matches.length) {
                return
              }
            }
          })
        }
      } else if (pattern) {
        // Should only search string values
        let values = this.flattenValues(JSON.parse(editorText))
        values.forEach((value) => {
          if (typeof value === "string") {
            let matchResult = regex.exec(value)
            while (matchResult) {
              matches.push({
                value: matchResult[0],
                index: editorText.indexOf(value) + matchResult.index,
              })
              matchResult = regex.exec(value)
            }
          }
        })
      }

      if (!matches.length) {
        return
      }

      const ranges = matches.map((match) => {
        let startPos, endPos
        if (typeof match === "string") {
          startPos = model.getPositionAt(editorText.indexOf(match))
          endPos = model.getPositionAt(editorText.indexOf(match) + match.length)
        } else {
          startPos = model.getPositionAt(match.index)
          endPos = model.getPositionAt(match.index + match.value.length)
        }

        return new this.monaco.Range(
          startPos.lineNumber,
          startPos.column,
          endPos.lineNumber,
          endPos.column
        )
      })

      this.decoration = this.editor.deltaDecorations(
        this.decoration,
        ranges.map((range) => {
          return {
            range,
            options: {
              isWholeLine: false,
              className: "highlight",
            },
          }
        })
      )
    },
    flattenValues(obj) {
      if (typeof obj === "string") {
        return [obj]
      }
      let values = []
      for (let key in obj) {
        let value = obj[key]
        if (Array.isArray(value)) {
          value.forEach((val) => {
            values = values.concat(this.flattenValues(val))
          })
        } else if (typeof value === "object") {
          values = values.concat(this.flattenValues(value))
        } else {
          values.push(value)
        }
      }
      return values
    },
    clearAllDecorations() {
      this.decoration = this.editor.deltaDecorations(this.decoration, this.noHighlight)
    },
    getDefaultValue() {
      const defaultEditorValue = `{
  "name": "process_events",
  "hostIdentifier": "host1",
  "calendarTime": "2022-10-19T10:35:01Z",
  "time": 1618698901,
  "columns": {
    "pid": 888,
    "path": "/bin/process",
    "cmdline": "/bin/process -arg1 value1 -arg2 value2",
    "state": "running",
    "parent": 555,
    "created_at": 1618698901,
    "updated_at": 1618698901
  }
}`
      return defaultEditorValue
    },
  },
}
</script>

<style>
.highlight {
  background-color: rgb(176, 227, 243);
}
</style>
