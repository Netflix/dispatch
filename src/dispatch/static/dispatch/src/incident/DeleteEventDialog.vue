<template>
  <v-dialog v-model="showDeleteEventDialog" persistent max-width="800px">
    <v-card>
      <v-card-title>
        <span class="text-h5">Delete Event?</span>
      </v-card-title>
      <v-card-text>
        <v-container>Are you sure you want to delete this event?</v-container>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="blue en-1" variant="text" @click="closeDeleteEventDialog()"> Cancel </v-btn>
        <v-btn color="red en-1" variant="text" @click="deleteEvent()"> Delete </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
export default {
  name: "DeleteEventDialog",
  data() {
    return {}
  },
  computed: {
    ...mapFields("incident", ["dialogs.showDeleteEventDialog"]),
  },

  methods: {
    ...mapActions("incident", ["closeDeleteEventDialog", "deleteEvent"]),
  },
}
</script>
