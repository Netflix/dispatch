<template>
  <v-dialog v-model="showRemove" persistent max-width="800px">
    <v-card>
      <v-card-title>
        <span class="headline">Delete Task?</span>
      </v-card-title>
      <v-card-text>
        <v-container grid-list-md>
          <v-layout wrap>Are you sure you would like to delete this task?</v-layout>
        </v-container>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="blue darken-1" text @click="closeRemove()">Cancel</v-btn>
        <v-btn color="red darken-1" text @click="remove()">Delete</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapActions } from "vuex"
import { mapFields } from "vuex-map-fields"
export default {
  name: "TaskDeleteDialog",
  data() {
    return {}
  },
  computed: {
    ...mapFields("task", ["dialogs.showRemove"])
  },

  methods: {
    ...mapActions("task", ["remove", "closeRemove"])
  }
}
</script>
