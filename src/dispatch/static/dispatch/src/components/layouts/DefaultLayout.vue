<template>
  <v-app id="dispatch">
    <!--<loading />-->
    <organization-banner />
    <app-toolbar />
    <app-drawer />
    <notification-snackbars-wrapper />

    <refresh />
    <v-main>
      <div>
        <v-container ma-0 pa-0 fluid>
          <router-view />
        </v-container>
      </div>
    </v-main>
    <!-- Go to top -->
  </v-app>
</template>

<script>
import AppDrawer from "@/components/AppDrawer"
import AppToolbar from "@/components/AppToolbar"
import Refresh from "@/components/Refresh.vue"
import NotificationSnackbarsWrapper from "@/components/NotificationSnackbarsWrapper.vue"
import OrganizationBanner from "@/organization/OrganizationBanner.vue"

export default {
  components: {
    AppDrawer,
    AppToolbar,
    Refresh,
    NotificationSnackbarsWrapper,
    OrganizationBanner,
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
