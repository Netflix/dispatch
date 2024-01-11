<template>
  <v-app>
    <notification-snackbars-wrapper />
    <v-main>
      <organization-banner />
      <v-app-bar flat style="border-bottom: 1px solid #d2d2d2 !important" color="background0">
        <template #prepend>
          <router-link :to="{ name: 'IncidentOverview' }" style="text-decoration: none">
            <span class="button font-weight-bold">D I S P A T C H</span>
          </router-link>
        </template>
      </v-app-bar>
      <router-view :key="$route.path" />
    </v-main>
  </v-app>
</template>

<script>
import NotificationSnackbarsWrapper from "@/components/NotificationSnackbarsWrapper.vue"
import OrganizationBanner from "@/organization/OrganizationBanner.vue"

export default {
  components: {
    NotificationSnackbarsWrapper,
    OrganizationBanner,
  },
  data: () => ({}),

  methods: {},
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
