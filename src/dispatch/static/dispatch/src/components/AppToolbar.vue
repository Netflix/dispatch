<template>
  <v-app-bar flat style="border-bottom: 1px solid #d2d2d2 !important" color="background0">
    <template #prepend>
      <router-link :to="{ name: 'IncidentOverview' }" style="text-decoration: none">
        <span class="button font-weight-bold">D I S P A T C H</span>
      </router-link>
    </template>
    <organization-create-edit-dialog />
    <!--<v-app-bar-nav-icon @click="handleDrawerToggle" />-->

    <v-spacer />
    <v-text-field
      v-model="queryString"
      hide-details
      prepend-inner-icon="mdi-magnify"
      label="Search"
      clearable
      variant="solo"
      single-line
      flat
      bg-color="background2"
      @keyup.enter="performSearch()"
    />
    <v-spacer />
    <v-toolbar-items>
      <v-btn icon variant="text" @click="toggleDarkTheme">
        <v-icon :icon="dark_theme ? 'mdi-white-balance-sunny' : 'mdi-moon-waxing-crescent'" />
        <v-tooltip activator="parent" location="bottom">
          Dark Mode {{ dark_theme ? "Off" : "On" }}
        </v-tooltip>
      </v-btn>
      <v-btn icon variant="text">
        <v-icon>mdi-help-circle-outline</v-icon>
        <v-menu activator="parent">
          <v-list density="compact">
            <v-list-item
              href="/api/v1/docs"
              target="_blank"
              title="API Documentation"
              append-icon="mdi-open-in-new"
            />
            <v-list-item
              href="https://netflix.github.io/dispatch/"
              target="_blank"
              title="App Documentation"
              append-icon="mdi-open-in-new"
            />
            <v-list-item
              v-if="currentVersion()"
              @click="showCommitMessage"
              append-icon="mdi-page-next-outline"
            >
              <v-list-item-title>
                Current version: {{ formatHash(currentVersion()) }}
              </v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>
      </v-btn>
      <v-btn icon size="large" variant="text">
        <v-avatar size="30px" v-if="userAvatarUrl(currentUser())">
          <v-img :src="userAvatarUrl(currentUser())" />
        </v-avatar>
        <v-avatar size="30px" v-else>
          <v-icon>mdi-account-circle</v-icon>
        </v-avatar>
        <v-menu activator="parent" width="400">
          <v-list class="pb-0">
            <v-list-item class="px-2">
              <template #prepend>
                <v-avatar v-if="userAvatarUrl(currentUser())">
                  <v-img :src="userAvatarUrl(currentUser())" />
                </v-avatar>
                <v-avatar v-else>
                  <v-icon size="30px">mdi-account-circle</v-icon>
                </v-avatar>
              </template>

              <v-list-item-title class="text-h6">
                {{ currentUser().name || currentUser().email }}
              </v-list-item-title>
              <v-list-item-subtitle> {{ currentUser().email }} </v-list-item-subtitle>

              <template #append>
                <v-tooltip location="bottom">
                  <template #activator="{ props }">
                    <v-btn icon="mdi-logout" variant="plain" v-bind="props" @click="logout()" />
                  </template>
                  <span>Logout</span>
                </v-tooltip>
              </template>
            </v-list-item>
            <v-divider />
            <v-list-subheader>Experimental Features</v-list-subheader>
            <v-switch
              v-model="currentUser().experimental_features"
              inset
              class="ml-5"
              color="blue"
              @update:model-value="updateExperimentalFeatures()"
              :label="currentUser().experimental_features ? 'Enabled' : 'Disabled'"
            />
            <v-divider />
            <v-list-subheader>Organizations</v-list-subheader>
            <v-list-item v-for="(item, i) in organizations" :key="i">
              <v-list-item-title>{{ item.name }}</v-list-item-title>
              <v-list-item-subtitle>{{ item.description }}</v-list-item-subtitle>

              <template #append>
                <v-tooltip location="bottom">
                  <template #activator="{ props }">
                    <v-btn
                      icon="mdi-pencil-outline"
                      variant="text"
                      v-bind="props"
                      @click="showCreateEditDialog(item)"
                    />
                  </template>
                  <span>Edit Organization</span>
                </v-tooltip>
                <v-tooltip location="bottom">
                  <template #activator="{ props }">
                    <v-btn
                      @click="switchOrganizations(item.slug)"
                      icon="mdi-swap-horizontal"
                      variant="text"
                      v-bind="props"
                    />
                  </template>
                  <span>Switch Organization</span>
                </v-tooltip>
              </template>
            </v-list-item>
            <v-list-item @click="showCreateEditDialog()" prepend-icon="mdi-plus">
              <v-list-item-title>Create a new organization</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>
      </v-btn>
    </v-toolbar-items>
  </v-app-bar>
</template>
<script>
import { mapActions, mapGetters, mapMutations, mapState } from "vuex"

import Util from "@/util"
import { formatHash } from "@/filters"
import OrganizationApi from "@/organization/api"
import OrganizationCreateEditDialog from "@/organization/CreateEditDialog.vue"
import UserApi from "@/auth/api"

export default {
  name: "AppToolbar",
  data: () => ({
    organizations: [],
    query: "",
    dark_theme: false,
  }),
  setup() {
    return { formatHash }
  },
  components: {
    OrganizationCreateEditDialog,
  },
  computed: {
    queryString: {
      set(query) {
        this.$store.dispatch("search/setQuery", query)
        this.query = query
      },
      get() {
        return this.$store.state.query.q
      },
    },
  },
  methods: {
    updateExperimentalFeatures() {
      UserApi.getUserInfo()
        .then((response) => {
          let userId = response.data.id
          let newUserExperimentalFeatures = this.currentUser().experimental_features
          UserApi.update(userId, {
            id: userId,
            experimental_features: newUserExperimentalFeatures,
          })
        })
        .catch((error) => {
          console.error("Error occurred while updating experimental features: ", error)
        })
    },
    handleDrawerToggle() {
      this.$store.dispatch("app/toggleDrawer")
    },
    handleFullScreen() {
      Util.toggleFullScreen()
    },
    performSearch() {
      let query = this.query
      this.$store.dispatch("search/getResults", this.$store.state.query)
      this.$router.push({ name: "ResultList", query: { q: query } })
    },
    toggleDarkTheme() {
      this.$vuetify.theme.global.name = this.$vuetify.theme.global.current.dark ? "light" : "dark"
      localStorage.setItem("dark_theme", this.$vuetify.theme.global.current.dark.toString())
      this.dark_theme = !this.dark_theme
    },
    switchOrganizations(slug) {
      this.$router.push({ params: { organization: slug } }).then(() => {
        this.$router.go()
      })
    },
    ...mapState("auth", ["currentUser"]),
    ...mapState("app", ["currentVersion"]),
    ...mapActions("auth", ["logout", "getExperimentalFeatures"]),
    ...mapActions("search", ["setQuery"]),
    ...mapActions("organization", ["showCreateEditDialog"]),
    ...mapActions("app", ["showCommitMessage"]),
    ...mapMutations("search", ["SET_QUERY"]),
    ...mapGetters("auth", ["userAvatarUrl"]),
  },

  created() {
    this.error = null
    this.loading = "error"
    let filterOptions = {
      itemsPerPage: 50,
      sortBy: ["name"],
      descending: [false],
    }

    let theme = localStorage.getItem("dark_theme")
    if (theme) {
      if (theme === "true") {
        this.dark_theme = true
        if (this.$vuetify.theme.global) this.$vuetify.theme.global.name = "dark"
        this.$vuetify.theme.dark = true
      } else {
        this.dark_theme = false
        if (this.$vuetify.theme.global) this.$vuetify.theme.global.name = "light"
        this.$vuetify.theme.dark = false
      }
    }

    OrganizationApi.getAll(filterOptions).then((response) => {
      this.organizations = response.data.items
      this.loading = false
    })

    this.getExperimentalFeatures()
  },
}
</script>
