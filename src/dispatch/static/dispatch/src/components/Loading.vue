<template>
  <v-layout row justify-center>
    <v-dialog v-model="loading" persistent content content-class="centered-dialog">
      <v-container fill-height>
        <v-layout column justify-center align-center>
          <v-progress-circular size="100" indeterminate color="info" />
        </v-layout>
      </v-container>
    </v-dialog>
  </v-layout>
</template>

<script>
import { mapFields } from "vuex-map-fields"

export default {
  data() {
    return {}
  },

  computed: {
    ...mapFields("app", ["loading"]),
  },
}
</script>
