<template>
  <v-app>
    <div class="app-root">
      <router-view />
      <v-snackbar bottom right :value="updateExists" :timeout="0" color="info">
        An update is available
        <v-btn text @click="refreshApp">
          Update
        </v-btn>
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
  mixins: [update]
}
</script>

<style scoped>
.setting-fab {
  top: 50% !important;
  right: 0;
  border-radius: 0;
}
</style>
