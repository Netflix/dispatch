<style>
.v-list-item--active::before {
  background-color: #e50914;
  display: block;
  content: "";
  position: absolute;
  top: 6px;
  bottom: 6px;
  left: -8px;
  width: 5px;
  opacity: 0.5 !important;
  border-radius: 0px 3px 3px 0px;
  transition: background-color 0.15s linear 0s;
}
</style>
<template>
  <v-navigation-drawer
    app
    permanent
    :width="mini ? 220 : 440"
    clipped
    class="background1"
    v-if="showChildPane"
  >
    <v-row class="fill-height" no-gutters>
      <v-navigation-drawer width="220" permanent :mini-variant="mini">
        <v-list dense flat nav>
          <span v-for="(route, index) in routes" :key="index" :to="route.path">
            <v-list-item :to="{ name: route.name }">
              <v-list-item-action>
                <v-icon>{{ route.meta.icon }}</v-icon>
              </v-list-item-action>
              <v-list-item-content>
                <v-list-item-title>{{ route.meta.title }}</v-list-item-title>
              </v-list-item-content>
            </v-list-item>
          </span>
          <v-list-item v-if="mini" @click.stop="toggleMiniNav()">
            <v-list-item-action>
              <v-icon>mdi-chevron-right</v-icon>
            </v-list-item-action>
            <v-list-item-content>
              <v-list-item-title>Minimize</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
          <v-list-item v-else @click.stop="toggleMiniNav()">
            <v-list-item-action>
              <v-icon>mdi-chevron-left</v-icon>
            </v-list-item-action>
            <v-list-item-content>
              <v-list-item-title>Minimize</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list>
        <template v-slot:append>
          <div class="pa-3">
            <v-btn v-if="mini" color="error" block :to="{ name: 'report' }">
              <v-icon> error_outline </v-icon>
            </v-btn>
            <v-btn v-else color="error" block :to="{ name: 'report' }">
              <v-icon left> error_outline </v-icon>
              Report Incident
            </v-btn>
          </div>
        </template>
      </v-navigation-drawer>
      <v-list dense nav class="grow">
        <span v-for="(subRoutes, group, idx) in children" :key="group">
          <v-subheader>
            {{ group | capitalize }}
          </v-subheader>
          <v-list-item
            v-for="(route, subIndex) in subRoutes"
            :key="subIndex"
            :to="{ name: route.name, query: childrenQueryParams }"
          >
            <v-list-item-content>
              <v-list-item-title>{{ route.meta.title }}</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
          <v-divider v-if="idx != Object.keys(children).length - 1" />
        </span>
      </v-list>
    </v-row>
  </v-navigation-drawer>
  <v-navigation-drawer app permanent width="220" :mini-variant="mini" clipped v-else>
    <v-list dense nav>
      <span v-for="(route, index) in routes" :key="index">
        <v-list-item :to="{ name: route.name }">
          <v-list-item-action>
            <v-icon>{{ route.meta.icon }}</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>{{ route.meta.title }}</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </span>
      <v-list-item v-if="mini" @click.stop="toggleMiniNav()">
        <v-list-item-action>
          <v-icon>mdi-chevron-right</v-icon>
        </v-list-item-action>
        <v-list-item-content>
          <v-list-item-title>Minimize</v-list-item-title>
        </v-list-item-content>
      </v-list-item>
      <v-list-item v-else @click.stop="toggleMiniNav()">
        <v-list-item-action>
          <v-icon>mdi-chevron-left</v-icon>
        </v-list-item-action>
        <v-list-item-content>
          <v-list-item-title>Minimize</v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </v-list>
    <template v-slot:append>
      <div class="pa-3">
        <v-btn color="error" block :to="{ name: 'report' }">
          <v-icon left> error_outline </v-icon>
          <span v-if="!mini">Report Incident</span>
        </v-btn>
      </div>
    </template>
  </v-navigation-drawer>
</template>
<script>
import { groupBy, filter } from "lodash"
import { mapState } from "vuex"

export default {
  name: "AppDrawer",
  props: {
    expanded: {
      type: Boolean,
      default: true,
    },
    drawWidth: {
      type: [Number, String],
      default: "220",
    },
  },

  data: () => ({
    scrollSettings: {
      maxScrollbarLength: 160,
    },
    mini: false,
  }),

  created() {
    this.mini = JSON.parse(localStorage.getItem("mini_nav"))
  },

  methods: {
    subIsActive(input) {
      const paths = Array.isArray(input) ? input : [input]
      return paths.some((path) => {
        return this.$route.path.indexOf(path) === 0 // current path starts with this path string
      })
    },
    toggleMiniNav() {
      this.mini = !this.mini
      localStorage.setItem("mini_nav", this.mini)
    },
  },
  computed: {
    computeLogo() {
      return "/static/m.png"
    },
    routes() {
      return this.$router.options.routes.filter((route) =>
        "menu" in route.meta ? route.meta.menu : false
      )
    },
    childrenQueryParams() {
      return this.$router.currentRoute.query
    },
    showChildPane() {
      if (Object.keys(this.children).length) {
        return Object.values(this.children)[0].length > 1
      }
      return false
    },
    children() {
      let children = this.$router.options.routes.filter(
        (route) => route.path == this.$route.matched[0].path
      )[0].children

      // Filter sub-menu children
      let menuGroups = groupBy(children, function (child) {
        return child.meta.subMenu
      })

      // determine which submenu to display
      children = menuGroups[this.$route.meta.subMenu]

      // Filter children without groups
      children = filter(children, function (child) {
        return child.meta.group
      })

      return groupBy(children, function (child) {
        return child.meta.group
      })
    },
    ...mapState("app", ["toggleDrawer"]),
  },
}
</script>
