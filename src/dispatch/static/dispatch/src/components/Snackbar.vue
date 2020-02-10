<template>

  <v-snackbar v-model="show">
    {{ text }}
    <v-btn text :color="color" @click.native="closeSnackbar" :timeout="timeout">Close</v-btn>
  </v-snackbar>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

export default {
  data() {
    return {}
  },

  computed: {
    ...mapFields("app", ["snackbar.text", "snackbar.timeout", "snackbar.show", "snackbar.color"])
  },

  methods: {
    ...mapActions("app", ["closeSnackbar"])
  }
}
</script>
