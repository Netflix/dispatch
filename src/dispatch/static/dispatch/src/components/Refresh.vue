<template>
  <v-dialog v-model="show" persistent max-width="500">
    <v-card>
      <v-card-title class="text-h5"> Refresh Required </v-card-title>
      <v-card-text>{{ message }}</v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="info" variant="text" @click="performRefresh()"> Refresh </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

export default {
  data() {
    return {}
  },

  computed: {
    ...mapFields("app", ["refresh.show", "refresh.message"]),
  },

  methods: {
    ...mapActions("app", ["performRefresh"]),
  },
}
</script>
