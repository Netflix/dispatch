<template>
  <v-app id="dispatch">
    <!--<loading />-->
    <app-toolbar />
    <app-drawer />
    <notification-snackbars-wrapper />
    <refresh />
    <v-main>
      <!-- Page Header -->
      <page-header />
      <div class="page-wrapper">
        <router-view />
      </div>
    </v-main>
  </v-app>
</template>

<script>
import AppDrawer from "@/components/AppDrawer"
import AppToolbar from "@/components/AppToolbar"
import PageHeader from "@/components/PageHeader"
import Refresh from "@/components/Refresh.vue"
import NotificationSnackbarsWrapper from "@/components/NotificationSnackbarsWrapper.vue"

export default {
  name: "DashboardLayout",

  data() {
    return {
      tab: null,
    }
  },
  components: {
    AppDrawer,
    AppToolbar,
    PageHeader,
    Refresh,
    NotificationSnackbarsWrapper,
  },

  created() {
    this.$vuetify.theme.light = true
  },
}
</script>

<style scoped>
.page-wrapper {
  min-height: calc(100vh - 64px - 50px - 81px);
}
</style>
