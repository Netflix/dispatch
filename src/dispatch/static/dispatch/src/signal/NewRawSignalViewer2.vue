<script setup>
import { ref, computed } from "vue"
import * as monaco from "monaco-editor"
import MonacoEditor from "@/components/MonacoEditor.vue"

// Define Props
const props = defineProps({
  value: {
    type: Object,
    default: () => ({}),
  },
})

const dialog = ref(false)

monaco.editor.defineTheme("myCustomTheme", {
  base: "vs", // can also be vs-dark or hc-black
  inherit: true, // can also be false to completely replace the builtin rules
  rules: [
    {
      token: "string.value.json",
      foreground: "#ef4444",
    },
    {
      token: "string.key.json",
      foreground: "#0a0a0a",
    },
  ],
  colors: {
    "editor.foreground": "#000000",
  },
})

const editorOptions = {
  automaticLayout: true,
  renderValidationDecorations: "on",
  readOnly: true,
  minimap: {
    enabled: false,
  },
}

// Computed property for raw_str
const raw_str = computed(() => JSON.stringify(props.value, null, "\t") || "[]")
</script>

<template>
  <MonacoEditor
    class="pl-15"
    v-model="raw_str"
    :options="editorOptions"
    language="json"
    theme="myCustomTheme"
    style="width: 890px"
  />
  <!-- <v-card>
    <div style="height: 800px">
      <MonacoEditor
        v-model="raw_str"
        :options="editorOptions"
        language="json"
        theme="myCustomTheme"
        style="width: 100%"
      />
    </div>
  </v-card> -->
</template>
