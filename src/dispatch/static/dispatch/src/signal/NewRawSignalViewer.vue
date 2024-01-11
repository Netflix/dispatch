<script setup>
import { computed, ref, watch } from "vue"

// Necessary import for JSON language server
// eslint-disable-next-line no-unused-vars
import * as monaco from "monaco-editor"
import json_to_ast from "json-to-ast"

import { findPath, extractKeyValue, findPositions } from "@/util/jpath"
import { useStore } from "vuex"
import MonacoEditor from "@/components/MonacoEditor.vue"
import EntityTypeCreateDialogV2 from "@/entity_type/EntityTypeCreateDialogV2.vue"

// Define Props
const props = defineProps({
  value: {
    type: Object,
    default: () => ({}),
  },
})

const store = useStore()
const dialog = ref(false)
const showModal = () => {
  dialog.value = true
}

const closeDialog = () => {
  dialog.value = false
}

const newEntityTypeJpath = ref("")

const raw_str = computed(() => JSON.stringify(props.value.raw, null, "\t") || "[]")

const editorBeforeMount = (monaco) => {
  monaco.languages.registerHoverProvider("json", {
    provideHover: (model, position) => {
      const word = model.getWordAtPosition(position)

      if (word) {
        const hoveredWord = word.word

        const entity = props.value.entities.find((entity) => entity.value === hoveredWord)
        if (entity) {
          const range = new monaco.Range(
            position.lineNumber,
            word.startColumn,
            position.lineNumber,
            word.endColumn
          )
          const title = `**Entity Type**: ${entity.entity_type.name}\n`
          const pattern = `**Pattern**: ${entity.entity_type.jpath}\n`
          const value = `**Value**: ${entity.value}`
          return {
            contents: [{ value: title }, { value: pattern }, { value: value }],
            range: range,
          }
        }
      }
      return null
    },
  })
}

let glyphLines = new Set()
const newEntities = ref([])

const editorMounted = (editor, monaco) => {
  editor.onMouseDown((event) => {
    if (event.target && event.target.type === monaco.editor.MouseTargetType.GUTTER_GLYPH_MARGIN) {
      const lineNumber = event.target.position.lineNumber

      // Check if the clicked line contains a glyph
      if (glyphLines.has(lineNumber)) {
        if (!event.event.rightButton) {
          const parsedJson = JSON.parse(editor.getValue())
          const lineContent = editor.getModel().getLineContent(lineNumber)

          // Extract key and value from line content
          const { key, value } = extractKeyValue(lineContent)

          // Find path to key
          let path = findPath(parsedJson, key, value)

          if (!path) {
            path = "$"
            store.commit(
              "notification_backend/addBeNotification",
              {
                text: `Unable to automatically generate JSON Path Expression. Defaulted to $`,
                type: "exception",
              },
              { root: true }
            )
          }

          // Save path
          newEntityTypeJpath.value = path

          showModal()
        }
      }
    }
  })

  const addEntityExtractionGlyphs = () => {
    // Add a glyph margin icon to each line in the editor
    const decorations = []
    const model = editor.getModel()
    const modelValue = model.getValue()
    const ast = json_to_ast(modelValue, { loc: true })

    glyphLines.clear()

    function traverse(node) {
      // Traverse `Object` and `Array` nodes to reach their child `Property` nodes.
      if (node.type === "Object" || node.type === "Array") {
        // Recursively traverse each child
        node.children.forEach(traverse)
      } else if (node.type === "Property") {
        const { key, value } = node
        // Check for `Literal` type and string value.
        if (value.type === "Literal" && typeof value.value === "string") {
          const start = model.getPositionAt(value.loc.start.offset)
          const end = model.getPositionAt(value.loc.end.offset)

          decorations.push({
            range: new monaco.Range(start.lineNumber, 1, end.lineNumber, 1),
            options: {
              isWholeLine: true,
              glyphMarginClassName: "myGlyphMarginClass",
              glyphMarginHoverMessage: { value: `Extract new entity from "**${key.value}**"` },
            },
          })
          // Record line numbers where glyphs were added.
          glyphLines.add(start.lineNumber)
        }

        // If the value of the property is an object or array, traverse it as well
        if (value.type === "Object" || value.type === "Array") {
          traverse(value)
        }
      }
    }
    traverse(ast)

    // Apply the decorations to the editor
    editor.deltaDecorations([], decorations)
  }

  const updateDecorations = () => {
    // Get JSON string and parse it
    const jsonString = editor.getValue()

    // Create an array of all entities, combining props.value.entities and newEntities
    const allEntities = [...props.value.entities, ...newEntities.value]

    // Loop through entities
    for (const entity of allEntities) {
      // Normalize entity_type
      const entityType = entity.entity_type ? entity.entity_type : entity

      // Get JSONPath and find positions of the values
      const jpath = entityType.jpath
      const positions = findPositions(jsonString, jpath)

      // Loop through positions and decorate them
      for (const position of positions) {
        // Convert start and end positions to line and column
        const start = editor.getModel().getPositionAt(position.start)
        const end = editor.getModel().getPositionAt(position.end)

        const decoration = {
          range: new monaco.Range(start.lineNumber, start.column, end.lineNumber, end.column),
          options: {
            isWholeLine: false,
            className: "decorate",
          },
        }

        // Apply decoration
        editor.deltaDecorations([], [decoration])
      }
    }
  }

  updateDecorations()
  addEntityExtractionGlyphs()

  editor.onDidChangeModelContent(() => {
    updateDecorations()
    addEntityExtractionGlyphs()
  })

  /*
    Optimistically update decorations with the new Entity Type
    that is emitted from the EntityTypeCreateDialogV2 child component
  */
  watch(newEntities.value, () => {
    updateDecorations()
  })

  return {
    showModal,
    dialog,
    newEntityTypeJpath,
    newEntities,
  }
}

const addNewEntityType = (entityType) => {
  newEntities.value.push(entityType)
}

const editorOptions = {
  automaticLayout: true,
  renderValidationDecorations: "on",
  renderLineHighlight: "true",
  lineDecorationsWidth: 0,
  overviewRulerLanes: 0,
  scrollBeyondLastLine: false,
  hideCursorInOverviewRuler: true,
  readOnly: true,
  wordWrap: true,
  glyphMargin: true,
  contextmenu: false,
  scrollbar: {
    vertical: "hidden",
  },
  minimap: {
    enabled: false,
  },
}
</script>

<template>
  <div style="height: 820px">
    <MonacoEditor
      v-model="raw_str"
      :options="editorOptions"
      :editorMounted="editorMounted"
      :editorBeforeMount="editorBeforeMount"
      language="json"
      theme="myCustomTheme"
      style="width: 100%"
    />
    <EntityTypeCreateDialogV2
      v-model="dialog"
      :dialog="dialog"
      :newEntityTypeJpath="newEntityTypeJpath"
      :editorValue="raw_str"
      :signalId="value.signal.id"
      :signalObj="props.value"
      @update:dialog="closeDialog"
      @new-entity-type="addNewEntityType($event)"
    />
  </div>
</template>

<style lang="scss">
.decorate {
  background-color: rgba(203, 243, 252, 0.726);
  color: rgb(107, 111, 118) !important;
  border-bottom: 1px solid rgba(71, 71, 71, 0.1);
  padding: 4px;
}

.myGlyphMarginClass {
  background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><title>vector-point-plus</title><path fill="%23777" d="M9 9V15H15V9H9M11 11H13V13H11V11M18 15V18H15V20H18V23H20V20H23V18H20V15H18Z" /></svg>')
    center center no-repeat;
  background-size: contain;
}

.hover-row {
  max-height: 30px !important;
  opacity: 2 !important;
  color: rgb(25, 28, 24) !important;
  font-size: 0.6875rem !important;
  backdrop-filter: blur(12px) saturate(190%) contrast(50%) brightness(130%) !important;
  background-color: rgba(255, 255, 255, 0.5) !important;
  border: 0.5px solid rgb(216, 216, 216) !important;
}
</style>
