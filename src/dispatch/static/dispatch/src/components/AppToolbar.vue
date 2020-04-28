<template>
  <v-app-bar clipped-left clipped-right app color="primary" dark>
    <v-app-bar-nav-icon @click="handleDrawerToggle" />
    <span class="title ml-3 mr-5">Dispatch</span>
    <v-text-field
      v-model="queryString"
      flat
      hide-details
      solo-inverted
      prepend-inner-icon="search"
      label="Search"
      clearable
      class="search"
      @keyup.enter="performSearch()"
    />
    <v-spacer />
    <v-toolbar-items>
      <v-tooltip bottom>
        <template v-slot:activator="{ on }">
          <v-btn icon v-on="on" @click="handleFullScreen()">
            <v-icon>mdi-fullscreen</v-icon>
          </v-btn>
        </template>
        <span>Fullscreen</span>
      </v-tooltip>
      <v-tooltip bottom>
        <template v-slot:activator="{ on }">
          <v-btn icon large text v-on="on">
            <v-avatar size="30px">
              <img :src="userInfo().thumbnailPhotoUrl" :alt="userInfo().fullName" />
            </v-avatar>
          </v-btn>
        </template>
        <span>{{ userInfo().email }}</span>
      </v-tooltip>
      <!--
        <v-menu offset-y origin="center center" class="elelvation-1" :nudge-bottom="14" transition="scale-transition">
        <v-btn icon text slot="activator">
          <v-badge color="red" overlap>
            <span slot="badge">3</span>
            <v-icon medium>notifications</v-icon>
          </v-badge>
        </v-btn>
        <notification-list></notification-list>
      </v-menu>
      -->
    </v-toolbar-items>
  </v-app-bar>
</template>
<script>
import { mapActions, mapMutations, mapState } from "vuex"

import Util from "@/util"
export default {
  name: "AppToolbar",
  components: {},
  computed: {
    toolbarColor() {
      return this.$vuetify.options.extra.mainNav
    },
    queryString: {
      set(query) {
        this.$store.dispatch("search/setQuery", query)
      },
      get() {
        return this.$store.state.query
      }
    }
  },
  methods: {
    handleDrawerToggle() {
      this.$store.dispatch("app/toggleDrawer")
    },
    handleFullScreen() {
      Util.toggleFullScreen()
    },
    performSearch() {
      this.$store.dispatch("search/getResults", this.$store.state.query)
      this.$router.push("/search")
    },
    ...mapState("auth", ["userInfo"]),
    ...mapActions("search", ["setQuery"]),
    ...mapMutations("search", ["SET_QUERY"])
  }
}
</script>

<style lang="stylus" scoped></style>
