<template>
  <v-dialog v-model="showDeleteDialog" persistent max-width="800px">
    <v-card>
      <v-card-title>
        <span class="text-h5">Delete Form?</span>
      </v-card-title>
      <v-card-text>
        <v-container> Are you sure you want to delete this form? </v-container>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="blue en-1" variant="text" @click="closeDeleteDialog()"> Cancel </v-btn>
        <v-btn color="red en-1" variant="text" @click="deleteForm(selected)"> Delete </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
export default {
  name: "FormDeleteDialog",
  data() {
    return {}
  },
  computed: {
    ...mapFields("forms", ["dialogs.showDeleteDialog", "selected"]),
  },

  methods: {
    ...mapActions("forms", ["closeDeleteDialog", "deleteForm"]),
  },
}
</script>
