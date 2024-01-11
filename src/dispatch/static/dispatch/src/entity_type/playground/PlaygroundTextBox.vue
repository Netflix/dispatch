<template>
  <div class="playground-editor" style="height: 500px">
    <div id="playground-editor" style="height: 500px" />
  </div>
</template>

<script>
import { mapMutations, mapGetters } from "vuex"
import loader from "@monaco-editor/loader"
import jsonpath from "jsonpath"
import json_to_ast from "json-to-ast"
import { markRaw } from "vue"

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
        automaticLayout: true,
        value: this.getDefaultValue(),
      }
      let uuid = crypto.randomUUID()
      // Create a unique URI for the in-memory model
      const modelUri = monaco.Uri.parse(`inmemory://playground-${uuid}`)
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
      this.editor = markRaw(editor)
      this.monaco = markRaw(monaco)

      // Register an event listener for when the content of the model changes
      this.editor.onDidChangeModelContent(() => {
        // Call the updateDecorations method and pass the current pattern and jpath
        this.updateDecorations(this.pattern, this.jpath)
      })
      this.editor.layout()
    })
  },
  beforeUnmount() {
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
      try {
        JSON.parse(editorText)
      } catch (e) {
        this.clearAllDecorations()
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

      const ranges = []
      const ast = json_to_ast(model.getValue())

      if (jpath) {
        const nodes = jsonpath.nodes(JSON.parse(editorText), this.jpath)
        const jpathTree = nodes.map((node) => node.path.filter((item) => item !== "$"))

        for (const p of jpathTree) {
          const el = this.extractPath(ast, p)
          /**
           * JSON Paths can return an Object of matches, which is not supported.
           *
           * @see test_find_entities_with_field_only, case #2, in test_entity_service.py
           */
          if (el.value.type === "Object") {
            break
          }

          let valueToMatch
          let alignIndex

          // matchAll cannot be called on numbers
          if (typeof el.value.value === "number") {
            // matchAll cannot be called on string
            valueToMatch = el.value.raw
            // There's no parentheses
            alignIndex = 0
          } else {
            valueToMatch = el.value.value
            // There's parentheses, which we don't want to match on
            alignIndex = 1
          }

          if (!pattern) {
            ranges.push(
              new this.monaco.Range(
                el.value.loc.start.line,
                el.value.loc.start.column + alignIndex,
                el.value.loc.end.line,
                el.value.loc.end.column - alignIndex
              )
            )
          } else {
            const matches = valueToMatch.matchAll(regex)
            for (const match of matches) {
              ranges.push(
                new this.monaco.Range(
                  el.value.loc.start.line,
                  el.value.loc.start.column + match.index + alignIndex,
                  el.value.loc.start.line,
                  el.value.loc.start.column + match.index + match[0].length + alignIndex
                )
              )
            }
          }
        }
      } else {
        const seenIndexes = new Set()

        for (const match of this.matches) {
          let startPos, endPos

          // Values must be coerced to strings to get their length
          match.value = match.value.toString()

          // Position of first occurence
          startPos = model.getPositionAt(match.index)
          endPos = model.getPositionAt(match.index + match.value.length)

          // Push the first occurence of the pattern to ranges for decoration
          ranges.push(this.newRange(startPos, endPos))

          let indexOfNext = editorText.indexOf(match.value, editorText.indexOf(match.value) + 1)

          /**
           * Loop through the model until we extract all occurences.
           *
           * @see Array.prototype.indexOf(), always returns -1 when searchElement is NaN
           */
          while (indexOfNext !== -1) {
            if (seenIndexes.has(indexOfNext)) {
              break
            }

            startPos = model.getPositionAt(indexOfNext)
            endPos = model.getPositionAt(indexOfNext + match.value.length)
            ranges.push(this.newRange(startPos, endPos))
            seenIndexes.add(indexOfNext)
            indexOfNext = editorText.indexOf(match.value, indexOfNext + 1)
          }
        }
      }

      this.applyNewDecorations(ranges)
    },
    newRange(startPos, endPos) {
      return new this.monaco.Range(
        startPos.lineNumber,
        startPos.column,
        endPos.lineNumber,
        endPos.column
      )
    },
    /**
     * Extracts the path to a value within an abstract syntax tree (AST)
     *
     * @param {Object} ast - The abstract syntax tree to extract the path from
     * @param {Array} path - An array of keys or indices representing the path to the desired value
     * @returns {Object} An object with two properties: 'value' and 'path', where 'value' is the extracted value and 'path' is the full path to the value
     * @returns {null} If the value is not found in the AST or if either the 'ast' or 'path' arguments are missing
     */
    extractPath(ast, path) {
      // Return null if either the ast or path is missing
      if (!ast || !path) return null

      // Keep track of the current node in the iteration and the current path
      let currentNode = ast
      let currentPath = []

      // Iterate over the path elements
      for (let i = 0; i < path.length; i++) {
        // Add the current path element to the current path
        currentPath.push(path[i])

        if (currentNode.type === "Object") {
          // Find the property node in the children of the current node that matches the current path element
          let propertyNode = currentNode.children.find((child) => {
            return (
              child.type === "Property" &&
              child.key.type === "Identifier" &&
              child.key.value === path[i]
            )
          })
          // If the property node is not found, return null
          if (!propertyNode) return null

          // Set the current node to the value of the property node
          currentNode = propertyNode.value
        } else if (currentNode.type === "Array") {
          // Get the current path element as the index
          let index = path[i]
          // If the index is out of bounds, return null
          if (index >= currentNode.children.length) return null
          // Set the current node to the child at the given index
          currentNode = currentNode.children[index]
        } else {
          // Return null if the current node is neither an object nor an array
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
    applyNewDecorations(ranges) {
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
  background-color: rgb(238, 176, 176);
}
</style>
