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
import json_to_ast from "json-to-ast"
import { getByKey } from "ast-get-values-by-key"

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
      matches: [],
      decoration: [],
      noHighlight: [],
      editor: null,
      monaco: null,
      model: null,
    }
  },
  computed: mapGetters("playground", ["pattern", "jpath"]),
  watch: {
    pattern(newPattern) {
      this.clearAllDecorations()
      if (!newPattern && !this.jpath) {
        this.clearAllDecorations()
      }
      this.updatePattern(newPattern)
      this.updateDecorations(newPattern, this.jpath)
    },
    jpath(newJsonPath) {
      this.clearAllDecorations()
      if (!newJsonPath && !this.pattern) {
        this.clearAllDecorations()
      }
      this.updateJsonPath(newJsonPath)
      this.updateDecorations(this.pattern, newJsonPath)
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

      let regex = null
      if (pattern) {
        regex = new RegExp(pattern, "g")
      }

      this.matches = []

      if (jpath) {
        const jpathMatches = jsonpath.query(JSON.parse(editorText), jpath)
        if (jpathMatches.length) {
          jpathMatches.forEach((jpathMatch) => {
            if (!pattern) {
              this.matches.push({
                value: jpathMatch,
                index: editorText.indexOf(jpathMatch),
              })
            } else {
              jpathMatch = jpathMatch.toString()
              this.findMatchesWithRegex(regex, editorText, jpathMatch)
            }
          })
        }
      } else {
        let values = this.flattenValues(JSON.parse(editorText))
        values.forEach((value) => {
          value = value.toString()
          this.findMatchesWithRegex(regex, editorText, value)
        })
      }
      if (!this.matches.length) {
        return
      }

      if (jpath) {
        const ranges = []
        const ast = json_to_ast(model.getValue())
        const nodes = jsonpath.nodes(JSON.parse(editorText), this.jpath)
        const jpathTree = nodes.map((node) => node.path.filter((item) => item !== "$"))
        for (var p of jpathTree) {
          if (!pattern) {
            const el = this.extractPath(ast, p)
            ranges.push(
              new this.monaco.Range(
                el.value.loc.start.line,
                el.value.loc.start.column,
                el.value.loc.end.line,
                el.value.loc.end.column
              )
            )
          } else {
            const el = this.extractPath(ast, p)
            const matches = el.value.value.matchAll(regex)
            for (const match of matches) {
              ranges.push(
                new this.monaco.Range(
                  el.value.loc.start.line,
                  el.value.loc.start.column + match.index + 1,
                  el.value.loc.start.line,
                  el.value.loc.start.column + match.index + match[0].length + 1
                )
              )
            }
          }
        }
        try {
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
        } catch (error) {
          console.error(error)
        }
      } else {
        const ranges = []
        let indexOfNext = 0
        const seenIndexes = new Set()
        for (let [index, match] of this.matches.entries()) {
          let startPos, endPos

          // JSON Paths can return an Object of matches, which is not supported.
          // See: test_find_entities_with_field_only, case #2, in test_entity_service.py
          if (typeof match.value === "object" || Array.isArray(match.value)) {
            return
          }
          // Coerce all values to a string, necessary because we can't call .length
          match.value = match.value.toString()
          startPos = model.getPositionAt(match.index)
          endPos = model.getPositionAt(match.index + match.value.length)
          ranges.push(this.newRange(startPos, endPos))

          // Get the index of the next match
          indexOfNext = editorText.indexOf(match.value, editorText.indexOf(match.value) + 1)

          while (indexOfNext != -1) {
            if (seenIndexes.has(indexOfNext)) {
              break
            }
            startPos = model.getPositionAt(indexOfNext)
            endPos = model.getPositionAt(indexOfNext + match.value.length)
            ranges.push(this.newRange(startPos, endPos))
            seenIndexes.add(indexOfNext)
            indexOfNext = editorText.indexOf(match.value, indexOfNext + 1)
          }
          ranges.push(this.newRange(startPos, endPos))
        }
        try {
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
        } catch (error) {
          console.error(error)
        }
      }
    },
    newRange(startPos, endPos) {
      return new this.monaco.Range(
        startPos.lineNumber,
        startPos.column,
        endPos.lineNumber,
        endPos.column
      )
    },
    extractPath(ast, path) {
      if (!ast || !path) return null
      let currentNode = ast
      let currentPath = []
      for (let i = 0; i < path.length; i++) {
        currentPath.push(path[i])
        if (currentNode.type === "Object") {
          let propertyNode = currentNode.children.find((child) => {
            return (
              child.type === "Property" &&
              child.key.type === "Identifier" &&
              child.key.value === path[i]
            )
          })
          if (!propertyNode) return null
          currentNode = propertyNode.value
        } else if (currentNode.type === "Array") {
          let index = path[i]
          if (index >= currentNode.children.length) return null
          currentNode = currentNode.children[index]
        } else {
          return null
        }
      }
      return { value: currentNode, path: currentPath }
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
    findMatchesWithRegex(regex, editorText, value) {
      try {
        const matches = value.matchAll(regex)
        for (const match of matches) {
          this.matches.push({
            value: match[0],
            index: editorText.indexOf(value) + match.index,
          })
        }
      } catch (error) {
        console.error(error)
      }
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
    "created_at": 1918698901,
    "updated_at": 2118698901
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
