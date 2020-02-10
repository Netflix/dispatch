<template>
  <v-dialog
    v-model="showDeleteDialog"
    persistent
    max-width="800px"
  >
    <v-card>
      <v-card-title>
        <span class="headline">Delete Incident?</span>
      </v-card-title>
      <!--<v-alert
        :value="alert"
        type="error"
        transition="slide-y-transition"
      >There was an issue deleting.</v-alert>-->
      <v-card-text>
        <v-container grid-list-md>
          <v-layout wrap>
            Are you sure you would like to delete this incident?
          </v-layout>
        </v-container>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn
          color="blue darken-1"
          text
          @click="close"
        >
          Cancel
        </v-btn>
        <v-btn
          color="red darken-1"
          text
          @click="performDelete(selectedIncident)"
        >
          Delete
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapState, mapActions } from "vuex"
export default {
  name: "IncidentDeleteDialog",
  data() {
    return {}
  },
  computed: {
    ...mapState("incident", ["selectedIncident", "showDeleteDialog"])
  },

  methods: {
    ...mapActions("incident", ["deleteIncident"]),

    performDelete(incident) {
      this.$store.dispatch("incident/deleteIncident", incident)
    },

    close() {
      this.$store.dispatch("incident/showDeleteDialog", false)
    }
  }
}
</script>
