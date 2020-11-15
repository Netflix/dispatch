<template>
  <v-app id="dispatch">
    <!--<loading />-->
    <app-toolbar />
    <app-drawer />
    <snackbar />
    <refresh />
    <v-content>
      <!-- Page Header -->
      <page-header />
      <div class="page-wrapper">
        <v-container pa-4 grid-list-lg>
          <router-view />
        </v-container>
      </div>
      <!-- App Footer -->
      <v-footer height="auto" class="pa-3 app--footer">
        <span class="caption">Netflix Security &copy; {{ new Date().getFullYear() }}</span>
        <v-spacer />
        <span class="caption mr-1">Be Secure</span>
        <v-icon color="pink" small>favorite</v-icon>
      </v-footer>
    </v-content>
    <!-- Go to top -->
  </v-app>
</template>

<script>
import AppDrawer from "@/components/AppDrawer"
import AppToolbar from "@/components/AppToolbar"
import PageHeader from "@/components/PageHeader"
import Snackbar from "@/components/Snackbar.vue"
import Refresh from "@/components/Refresh.vue"

export default {
  components: {
    AppDrawer,
    AppToolbar,
    PageHeader,
    Snackbar,
    Refresh
  },

  created() {
    this.$vuetify.theme.light = true
  }
}
</script>

<style scoped>
.page-wrapper {
  min-height: calc(100vh - 64px - 50px - 81px);
}
</style>
