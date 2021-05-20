<template>
  <v-app-bar clipped-left clipped-right app flat class="v-bar--underline" color="background0">
    <organization-create-dialog />
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
        <template v-slot:activator="{ on }">
          <v-btn icon large text v-on="on">
            <v-avatar size="30px">
              <v-icon> account_circle </v-icon>
            </v-avatar>
          </v-btn>
        </template>
        <v-card width="300">
          <v-list>
            <v-list-item class="px-2">
              <v-list-item-avatar>
                <v-icon size="30px"> account_circle </v-icon>
              </v-list-item-avatar>
              <v-list-item-content>
                <v-list-item-title class="title" v-text="currentUser().name || currentUser().email">
                </v-list-item-title>
                <v-list-item-subtitle> {{ currentUser().email }} </v-list-item-subtitle>
              </v-list-item-content>
            </v-list-item>

            <v-divider></v-divider>
            <v-subheader>Organizations</v-subheader>
            <v-list-item
              v-for="(item, i) in organizations"
              :key="i"
              @click="switchOrganizations(item.name)"
            >
              <v-list-item-content>
                <v-list-item-title>{{ item.name }}</v-list-item-title>
                <v-list-item-subtitle>{{ item.description }}</v-list-item-subtitle>
              </v-list-item-content>
            </v-list-item>
          </v-list>
          <v-list-item @click="showCreateDialog()">
            <v-list-item-avatar>
              <v-icon size="30px">mdi-plus</v-icon>
            </v-list-item-avatar>
            <v-list-item-content>
              <v-list-item-title>Create a new organization</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
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
import OrganizationApi from "@/organization/api"
import OrganizationCreateDialog from "@/organization/CreateDialog.vue"

export default {
  name: "AppToolbar",
  data: () => ({
    organizations: [],
  }),
  components: {
    OrganizationCreateDialog,
  },
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
    switchOrganizations(name) {
      this.$router.replace({ params: { organization: name } })
      this.$router.go(this.$router.currentRoute)
    },
    ...mapState("auth", ["currentUser", "userAvatarUrl"]),
    ...mapActions("search", ["setQuery"]),
    ...mapActions("organization", ["showCreateDialog"]),
    ...mapMutations("search", ["SET_QUERY"]),
  },

  created() {
    this.error = null
    this.loading = "error"
    let filterOptions = {
      itemsPerPage: 50,
      sortBy: ["name"],
      descending: [false],
    }

    OrganizationApi.getAll(filterOptions).then((response) => {
      this.organizations = response.data.items
      this.loading = false
    })
  },
}
</script>

<style lang="stylus" scoped></style>
