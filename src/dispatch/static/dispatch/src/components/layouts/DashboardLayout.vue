<template>
  <v-app id="dispatch">
    <!--<loading />-->
    <app-toolbar />
    <app-drawer />
    <notification-snackbars-wrapper />
    <refresh />
    <v-main>
      <organization-banner />
      <div class="page-wrapper">
        <router-view />
      </div>
    </v-main>
  </v-app>
</template>

<script>
import AppDrawer from "@/components/AppDrawer"
import AppToolbar from "@/components/AppToolbar"
import Refresh from "@/components/Refresh.vue"
import NotificationSnackbarsWrapper from "@/components/NotificationSnackbarsWrapper.vue"
import OrganizationBanner from "@/organization/OrganizationBanner.vue"

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
    Refresh,
    OrganizationBanner,
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
