<template>
  <v-container grid-list-md>
    <v-layout wrap>
      <v-flex xs12>
        <v-select :items="languages" v-model="language" label="Language"></v-select>
      </v-flex>
      <v-flex xs12>
        <div style="height: 100vh">
          <MonacoEditor v-model="text" :options="editorOptions" :language="language"></MonacoEditor>
        </div>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import MonacoEditor from "monaco-editor-vue"

export default {
  name: "QueryTextTab",

  components: {
    MonacoEditor,
  },

  computed: {
    ...mapFields("query", ["selected.text", "selected.language", "selected.loading"]),
  },

  data() {
    return {
      languages: ["json", "psql", "sql"],
      editorOptions: {
        automaticLayout: true,
        renderValidationDecorations: "on",
      },
    }
  },
}
</script>
