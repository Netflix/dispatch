<template>
  <v-card width="100%" elevation="0">
    <v-card-subtitle> Created At: {{ item.created_at | formatRelativeDate }} </v-card-subtitle>
    <v-card-text>
      <div style="height: 800px">
        <MonacoEditor v-model="raw_str" :options="editorOptions"></MonacoEditor>
      </div>
    </v-card-text>
  </v-card>
</template>

<script>
import MonacoEditor from "monaco-editor-vue"

export default {
  name: "NewRawSignalViewer",
  components: {
    MonacoEditor,
  },
  props: {
    item: {
      type: Object,
      required: true,
    },
  },
  computed: {
    raw_str: {
      get: function () {
        return JSON.stringify(this.item.raw, null, "\t") || "[]"
      },
    },
  },
  data() {
    return {
      editorOptions: {
        automaticLayout: true,
        renderValidationDecorations: "on",
        readOnly: true,
        language: "json",
        minimap: {
          enabled: false,
        },
        scrollbar: {
          vertical: "hidden",
          horizontal: "hidden",
        },
        lineDecorationsWidth: 0,
      },
    }
  },
}
</script>
