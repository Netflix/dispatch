<template>
  <v-app>
    <snackbar />
    <v-content>
      <v-card flat>
        <v-toolbar color="primary" extended flat height="150" />
        <router-view :key="$route.path" />
      </v-card>
    </v-content>
    <!-- App Footer -->
    <v-footer height="auto" class="pa-3 app--footer">
      <span class="caption">Netflix Security &copy; {{ new Date().getFullYear() }}</span>
      <v-spacer />
      <span class="caption mr-1">Be Secure</span>
      <v-icon color="pink" small>favorite</v-icon>
    </v-footer>
  </v-app>
</template>

<script>
import Snackbar from "@/components/Snackbar.vue"
export default {
  components: {
    Snackbar
  },
  data: () => ({}),

  methods: {}
}
</script>
<style scoped lang="css">
.split-bg {
  height: 50%;
  width: 100%;
  position: absolute;
  top: 0;
  left: 0;
  content: "";
  z-index: 0;
}
</style>
