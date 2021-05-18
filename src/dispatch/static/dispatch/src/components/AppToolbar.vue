<template>
  <v-app-bar clipped-left clipped-right app flat class="v-bar--underline" color="background0">
    <!--<v-app-bar-nav-icon @click="handleDrawerToggle" />-->
    <router-link to="/" style="text-decoration: none">
      <span class="button font-weight-bold">D I S P A T C H</span>
    </router-link>
    <v-spacer />
    <v-text-field
      v-model="queryString"
      hide-details
      prepend-inner-icon="search"
      label="Search"
      clearable
      solo-inverted
      flat
      @keyup.enter="performSearch()"
    />
    <v-spacer />
    <v-toolbar-items>
      <v-tooltip v-if="!$vuetify.theme.dark" bottom>
        <template v-slot:activator="{ on }">
          <v-btn v-on="on" small icon @click="toggleDarkTheme">
            <v-icon class="mr-1"> mdi-moon-waxing-crescent </v-icon>
          </v-btn>
        </template>
        <span>Dark Mode On</span>
      </v-tooltip>

      <v-tooltip v-else bottom>
        <template v-slot:activator="{ on }">
          <v-btn v-on="on" small icon @click="toggleDarkTheme">
            <v-icon>mdi-white-balance-sunny</v-icon>
          </v-btn>
        </template>
        <span>Dark Mode Off</span>
      </v-tooltip>
      <v-tooltip bottom>
        <template v-slot:activator="{ on }">
          <v-btn icon v-on="on" @click="handleFullScreen()">
            <v-icon>fullscreen</v-icon>
          </v-btn>
        </template>
        <span>Fullscreen</span>
      </v-tooltip>
      <v-menu bottom left transition="scale-transition" origin="top right">
        <template v-slot:activator="{ on, attrs }">
          <v-btn icon large text v-on="on">
            <v-avatar size="30px">
              <v-icon> account_circle </v-icon>
            </v-avatar>
          </v-btn>
        </template>
        <v-card width="300">
          <v-list>
            <v-list-item class="px-2">
              <v-list-item-content>
                <v-list-item-avatar>
                  <v-icon> account_circle </v-icon>
                </v-list-item-avatar>
                <v-list-item-title class="title"> Kevin Glisson </v-list-item-title>
                <v-list-item-subtitle> {{ currentUser().email }} </v-list-item-subtitle>
              </v-list-item-content>
            </v-list-item>

            <v-divider></v-divider>

            <v-list-item v-for="(item, i) in items" :key="i" link>
              <v-list-item-title>{{ item.title }}</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-card>
      </v-menu>
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
  data: () => ({
    items: [
      { title: "Click Me" },
      { title: "Click Me" },
      { title: "Click Me" },
      { title: "Click Me 2" },
    ],
  }),
  components: {},
  computed: {
    queryString: {
      set(query) {
        this.$store.dispatch("search/setQuery", query)
      },
      get() {
        return this.$store.state.query
      },
    },
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
      this.$router.push({ name: "GlobalSearch" })
    },
    toggleDarkTheme() {
      this.$vuetify.theme.dark = !this.$vuetify.theme.dark
    },
    ...mapState("auth", ["currentUser", "userAvatarUrl"]),
    ...mapActions("search", ["setQuery"]),
    ...mapMutations("search", ["SET_QUERY"]),
  },
}
</script>

<style lang="stylus" scoped></style>
