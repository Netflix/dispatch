<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-select :items="languages" v-model="language" label="Language" />
      </v-col>
      <v-col cols="12">
        <div style="height: 100vh">
          <MonacoEditor v-model="text" :options="editorOptions" :language="language" />
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import MonacoEditor from "@/components/MonacoEditor.vue"

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
