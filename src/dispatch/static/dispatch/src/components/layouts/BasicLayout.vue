<template>
  <v-app>
    <notification-snackbars-wrapper />
    <v-main>
      <v-app-bar app flat class="v-bar--underline" color="background0">
        <router-link to="/" style="text-decoration: none">
          <span class="button font-weight-bold">D I S P A T C H</span>
        </router-link>
      </v-app-bar>
      <v-card flat>
        <router-view :key="$route.path" />
      </v-card>
    </v-main>
  </v-app>
</template>

<script>
import NotificationSnackbarsWrapper from "@/components/NotificationSnackbarsWrapper.vue"
export default {
  components: {
    NotificationSnackbarsWrapper,
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
