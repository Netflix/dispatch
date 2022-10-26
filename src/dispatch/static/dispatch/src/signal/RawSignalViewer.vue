<template>
  <v-dialog v-model="dialog" persistent max-width="800px">
    <template v-slot:activator="{ on }">
      <v-btn icon v-on="on"> <v-icon>mdi-card-search-outline</v-icon> </v-btn>
    </template>
    <v-card>
      <v-card-title>
        <span class="headline">Signal Data</span>
      </v-card-title>
      <v-card-text>
        <div style="height: 400px">
          <MonacoEditor v-model="raw_str" :options="editorOptions" language="json"></MonacoEditor>
        </div>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="blue en-1" text @click="dialog = false"> Close </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  name: "RawSignalDialog",

  props: {
    value: {
      type: Object,
      default: function () {
        return {}
      },
    },
  },

  components: {
    MonacoEditor: () => import("monaco-editor-vue"),
  },

  computed: {
    raw_str: {
      get: function () {
        return JSON.stringify(this.value, null, "\t") || "[]"
      },
    },
  },

  data() {
    return {
      dialog: false,
      editorOptions: {
        automaticLayout: true,
        renderValidationDecorations: "on",
        readOnly: true,
      },
    }
  },
}
</script>
