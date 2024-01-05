<template>
  <v-dialog v-model="showRemove" persistent max-width="800px">
    <v-card>
      <v-card-title>
        <span class="text-h5">Delete Form Type?</span>
      </v-card-title>
      <v-card-text>
        <v-container> Are you sure you would like to delete this form type? </v-container>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="blue en-1" variant="text" @click="closeRemove()"> Cancel </v-btn>
        <v-btn color="red en-1" variant="text" @click="remove()"> Delete </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapActions } from "vuex"
import { mapFields } from "vuex-map-fields"
export default {
  name: "IncidentFormTypeDeleteDialog",
  data() {
    return {}
  },
  computed: {
    ...mapFields("incident_cost_type", ["dialogs.showRemove"]),
  },

  methods: {
    ...mapActions("incident_cost_type", ["remove", "closeRemove"]),
  },
}
</script>
