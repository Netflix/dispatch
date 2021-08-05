<template>
  <v-app>
    <div class="app-root">
      <router-view />
      <v-snackbar bottom right :value="updateExists" :timeout="-1" color="info">
        An update is available
        <template v-slot:action="{ attrs }">
          <v-btn text v-bind="attrs" @click="refreshApp"> Update </v-btn>
        </template>
      </v-snackbar>
    </div>
  </v-app>
</template>

<script>
import update from "./mixins/update"

export default {
  data() {
    return {}
  },
  mixins: [update],
}
</script>

<style scoped>
.setting-fab {
  top: 50% !important;
  right: 0;
  border-radius: 0;
}
</style>
