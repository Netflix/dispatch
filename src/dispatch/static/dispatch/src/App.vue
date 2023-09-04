<template>
  <v-app>
    <div class="app-root">
      <router-view />
      <v-snackbar location="bottom right" :model-value="updateExists" :timeout="-1" color="info">
        An update is available
        <template #action="{ attrs }">
          <v-btn variant="text" v-bind="attrs" @click="refreshApp"> Update </v-btn>
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
