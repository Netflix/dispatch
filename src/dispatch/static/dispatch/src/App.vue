<template>
  <div class="app-root">
    <v-app>
      <router-view />
      <v-snackbar location="bottom right" :model-value="updateExists" :timeout="-1" color="info">
        An update is available
        <template #actions="{ attrs }">
          <v-btn variant="text" v-bind="attrs" @click="refreshApp"> Update </v-btn>
        </template>
      </v-snackbar>
    </v-app>
  </div>
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

<style>
.setting-fab {
  top: 50% !important;
  right: 0;
  border-radius: 0;
}

a {
  color: rgb(var(--v-theme-anchor));
}
</style>
