<template>
  <v-dialog v-model="dialog" persistent max-width="1000px">
    <template #activator="{ props }">
      <v-btn class="mr-2" icon variant="text" v-bind="props">
        <v-icon>mdi-card-search-outline</v-icon>
      </v-btn>
    </template>
    <v-card>
      <v-card-title>
        <span class="text-h5">Signal Data</span>
      </v-card-title>
      <v-card-text>
        <div style="height: 800px">
          <MonacoEditor v-model="raw_str" :options="editorOptions" language="json" />
        </div>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="blue en-1" variant="text" @click="dialog = false"> Close </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import MonacoEditor from "@/components/MonacoEditor.vue"

export default {
  name: "RawSignalViewer",

  props: {
    value: {
      type: Object,
      default: function () {
        return {}
      },
    },
  },

  components: {
    MonacoEditor,
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
        minimap: {
          enabled: false,
        },
      },
    }
  },
}
</script>
