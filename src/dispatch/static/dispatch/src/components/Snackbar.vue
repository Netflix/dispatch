<template>
  <v-snackbar v-model="show" :timeout="timeout" :color="type">
    {{ text }}
    <v-btn color="primary" text @click="closeSnackbar">Close</v-btn>
  </v-snackbar>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

export default {
  data() {
    return {
      timeout: 6000
    }
  },

  computed: {
    ...mapFields("app", ["snackbar.text", "snackbar.type", "snackbar.show"])
  },

  methods: {
    customizeSnackbar: function() {
      if (this.type == "error") {
        this.timeout = 0
      }
    },
    ...mapActions("app", ["closeSnackbar"])
  },

  beforeUpdate() {
    this.customizeSnackbar()
  }
}
</script>
