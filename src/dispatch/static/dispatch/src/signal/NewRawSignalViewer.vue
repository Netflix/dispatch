<script setup>
import { computed } from "vue"
import MonacoEditor from "@/components/MonacoEditor.vue"

// Define Props
const props = defineProps({
  value: {
    type: Object,
    default: () => ({}),
  },
})

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
          const content = `**Entity Type**: ${entity.entity_type.name}\n\n**Pattern**: ${entity.entity_type.jpath}\n\n**Value**: ${entity.value}`
          return {
            contents: [{ value: content }],
            range: range,
          }
        }
      }
      return null
    },
  })
}

const editorOptions = {
  automaticLayout: true,
  renderValidationDecorations: "on",
  renderLineHighlight: "none",
  lineDecorationsWidth: 0,
  overviewRulerLanes: 0,
  scrollBeyondLastLine: false,
  hideCursorInOverviewRuler: true,
  readOnly: true,
  wordWrap: true,
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
      :editorBeforeMount="editorBeforeMount"
      language="json"
      theme="myCustomTheme"
      style="width: 100%"
    />
  </div>
</template>
