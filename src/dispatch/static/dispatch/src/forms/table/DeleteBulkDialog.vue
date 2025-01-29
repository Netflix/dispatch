<template>
  <v-dialog v-model="showDeleteBulkDialog" persistent max-width="800px">
    <v-card>
      <v-card-title>
        <span class="text-h5">Delete Forms?</span>
      </v-card-title>
      <v-card-text>
        <v-container> Are you sure you want to delete {{ selected.length }} form(s)? </v-container>
        <v-container>
          <div v-for="(item, id) in selected" :key="id">
            {{ item.incident.name }} - {{ item.form_type.name }}
          </div>
        </v-container>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="blue en-1" variant="text" @click="closeDeleteBulkDialog()"> Cancel </v-btn>
        <v-btn color="red en-1" variant="text" @click="deleteBulk()"> Delete </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

export default {
  name: "FormsDeleteBulkDialog",

  data() {
    return {}
  },

  computed: {
    ...mapFields("forms_table", ["dialogs.showDeleteBulkDialog", "table.rows.selected"]),
  },

  methods: {
    ...mapActions("forms_table", ["closeDeleteBulkDialog", "deleteBulk"]),
  },
}
</script>
