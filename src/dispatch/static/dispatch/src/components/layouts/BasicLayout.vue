<template>
  <v-app>
    <snackbar />
    <v-content>
      <v-app-bar app flat class="v-bar--underline" color="background0">
        <router-link to="/" tag="span">
          <span class="button font-weight-bold">D I S P A T C H</span>
        </router-link>
      </v-app-bar>
      <v-card flat>
        <router-view :key="$route.path" />
      </v-card>
    </v-content>
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
