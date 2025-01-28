<template>
  <v-dialog v-model="showExportDialog" persistent max-width="800px">
    <v-card>
      <v-card-title>
        <span class="text-h5">Export Forms</span>
      </v-card-title>
      <v-card-text v-if="exported_folders">
        <v-container> Forms have been exported successfully to </v-container>
        <v-container>
          <div v-for="folder in exported_folders" :key="folder">
            <a :href="folder" target="_blank">{{ folder }}</a>
          </div>
        </v-container>
      </v-card-text>
      <v-container
        v-if="export_clicked && !exported_folders"
        class="d-flex flex-column align-center justify-center"
        style="height: 200px"
      >
        <v-progress-circular indeterminate color="primary" size="64" class="mb-4" />
        <v-container class="text-center">Exporting forms...</v-container>
      </v-container>
      <v-card-text v-if="!export_clicked && !exported_folders">
        <v-container> Are you sure you want to export {{ selected.length }} form(s)? </v-container>
        <v-container>
          <div v-for="(item, id) in selected" :key="id">
            {{ item.incident.name }} - {{ item.form_type.name }}
          </div>
        </v-container>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="blue en-1" variant="text" @click="handleCloseExport()"> Close </v-btn>
        <v-btn color="red en-1" variant="text" @click="handleExportForms()" v-if="!export_clicked">
          Export
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

export default {
  name: "FormsExportDialog",

  data: () => ({
    export_clicked: false,
  }),

  computed: {
    ...mapFields("forms_table", [
      "dialogs.showExportDialog",
      "table.rows.selected",
      "executive_template_document",
      "exported_folders",
    ]),
  },

  methods: {
    ...mapActions("forms_table", ["closeExportDialog", "exportForms"]),
    handleCloseExport() {
      this.closeExportDialog()
      this.export_clicked = false
    },
    handleExportForms() {
      this.export_clicked = true
      this.exportForms()
    },
  },
}
</script>
