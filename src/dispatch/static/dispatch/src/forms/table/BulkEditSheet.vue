<template>
  <v-bottom-sheet
    v-model="showBulkEdit"
    :scrim="false"
    persistent
    no-click-animation
    :retain-focus="false"
  >
    <export-forms-dialog />
    <delete-bulk-dialog />
    <v-card :loading="bulkEditLoading" rounded="0">
      <v-list>
        <v-list-item>
          <v-list-item-subtitle>{{ selected.length }} selected</v-list-item-subtitle>

          <template #append>
            <v-btn variant="text" @click="showExportDialog()">
              <v-icon>mdi-account-arrow-right</v-icon>
              Export
            </v-btn>
            <v-btn variant="text" color="primary" @click="showDeleteBulkDialog()">
              <v-icon color="primary">mdi-delete</v-icon>
              Delete
            </v-btn>
          </template>
        </v-list-item>
      </v-list>
    </v-card>
  </v-bottom-sheet>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

import ExportFormsDialog from "@/forms/table/ExportFormsDialog.vue"
import DeleteBulkDialog from "@/forms/table/DeleteBulkDialog.vue"

export default {
  name: "FormsBulkEditSheet",

  components: {
    DeleteBulkDialog,
    ExportFormsDialog,
  },

  computed: {
    ...mapFields("forms_table", ["table.rows.selected", "table.bulkEditLoading"]),

    showBulkEdit: function () {
      return this.selected?.length ? true : false
    },
  },

  methods: {
    ...mapActions("forms_table", ["deleteBulk", "showExportDialog", "showDeleteBulkDialog"]),
  },
}
</script>
