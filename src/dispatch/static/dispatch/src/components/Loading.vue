<template>
  <v-dialog v-model="loading" persistent>
    <v-container fill-height>
      <div class="d-flex flex-column justify-center align-center">
        <v-progress-circular size="100" indeterminate color="info" />
      </div>
    </v-container>
  </v-dialog>
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
