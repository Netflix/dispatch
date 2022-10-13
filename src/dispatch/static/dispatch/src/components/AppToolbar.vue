<template>
  <v-app-bar clipped-left clipped-right app flat class="v-bar--underline" color="background0">
    <router-link :to="{ name: 'IncidentOverview' }" style="text-decoration: none">
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
      <v-menu offset-y>
        <template v-slot:activator="{ on, attrs }">
          <v-btn icon v-bind="attrs" v-on="on">
            <v-icon>help_outline</v-icon>
          </v-btn>
        </template>
        <v-list dense>
          <v-list-item href="/api/v1/docs" target="_blank">
            <v-list-item-title>API Documentation</v-list-item-title>
            <v-list-item-action>
              <v-list-item-icon>
                <v-icon small>open_in_new</v-icon>
              </v-list-item-icon>
            </v-list-item-action>
          </v-list-item>
          <v-list-item href="https://hawkins.gitbook.io/dispatch/" target="_blank">
            <v-list-item-title>App Documentation</v-list-item-title>
            <v-list-item-action>
              <v-list-item-icon>
                <v-icon small>open_in_new</v-icon>
              </v-list-item-icon>
            </v-list-item-action>
          </v-list-item>
        </v-list>
      </v-menu>
      <organization-menu />
      <organization-member-edit-dialog />
      <organization-create-edit-dialog />
    </v-toolbar-items>
  </v-app-bar>
</template>
<script>
import { mapActions, mapMutations } from "vuex"

import Util from "@/util"
import OrganizationMenu from "@/organization/OrganizationMenu.vue"
import OrganizationMemberEditDialog from "@/organization/OrganizationMemberEditDialog.vue"
import OrganizationCreateEditDialog from "@/organization/OrganizationCreateEditDialog.vue"
export default {
  name: "AppToolbar",
  components: {
    OrganizationMenu,
    OrganizationCreateEditDialog,
    OrganizationMemberEditDialog,
  },
  computed: {
    queryString: {
      set(query) {
        this.$store.dispatch("search/setQuery", query)
      },
      get() {
        return this.$store.state.query.q
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
      localStorage.setItem("dark_theme", this.$vuetify.theme.dark.toString())
    },
    ...mapActions("search", ["setQuery"]),
    ...mapMutations("search", ["SET_QUERY"]),
  },

  created() {
    let theme = localStorage.getItem("dark_theme")
    if (theme) {
      if (theme === "true") {
        this.$vuetify.theme.dark = true
      } else {
        this.$vuetify.theme.dark = false
      }
    }
  },
}
</script>

<style lang="stylus" scoped></style>
