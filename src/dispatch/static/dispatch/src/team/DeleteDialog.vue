<template>
  <v-dialog v-model="showRemove" persistent max-width="800px">
    <v-card>
      <v-card-title>
        <span class="text-h5">Delete Team?</span>
      </v-card-title>
      <!--<v-alert
        :value="alert"
        type="error"
        transition="slide-y-transition"
      >There was an issue deleting.</v-alert>-->
      <v-card-text>
        <v-container> Are you sure you would like to delete this team? </v-container>
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
  name: "TeamDeleteDialog",
  data() {
    return {}
  },
  computed: {
    ...mapFields("team", ["dialogs.showRemove"]),
  },

  methods: {
    ...mapActions("team", ["remove", "closeRemove"]),
  },
}
</script>
