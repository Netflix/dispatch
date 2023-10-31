<template>
  <v-dialog v-model="showRemove" persistent max-width="800px">
    <v-card>
      <v-card-title>
        <span class="text-h5">Delete Search Filter?</span>
      </v-card-title>
      <v-card-text>
        <v-container> Are you sure you would like to delete this search filter? </v-container>
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
  name: "SearchFilterDeleteDialog",

  data() {
    return {}
  },

  computed: {
    ...mapFields("search", ["dialogs.showRemove"]),
  },

  methods: {
    ...mapActions("search", ["remove", "closeRemove"]),
  },
}
</script>
