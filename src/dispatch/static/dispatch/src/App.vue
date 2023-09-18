<template>
  <div class="app-root">
    <router-view />
    <v-snackbar location="bottom right" :model-value="updateExists" :timeout="-1" color="info">
      An update is available
      <template #action="{ attrs }">
        <v-btn variant="text" v-bind="attrs" @click="refreshApp"> Update </v-btn>
      </template>
    </v-snackbar>
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

.v-list-item--active::before {
  background-color: #e50914;
  display: block;
  content: "";
  position: absolute;
  top: 6px;
  bottom: 6px;
  left: -8px;
  width: 5px;
  opacity: 0.5 !important;
  border-radius: 0px 3px 3px 0px;
  transition: background-color 0.15s linear 0s;
}
</style>
