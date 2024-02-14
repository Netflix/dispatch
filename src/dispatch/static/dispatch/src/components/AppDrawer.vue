<template>
  <v-navigation-drawer permanent :width="mini ? 220 : 440" class="background1" v-if="showChildPane">
    <v-layout class="h-100">
      <v-navigation-drawer width="220" permanent :rail="mini">
        <v-list density="compact" nav>
          <v-list-item
            v-for="(route, index) in routes"
            :key="index"
            :to="{ name: route.name }"
            :prepend-icon="route.meta.icon"
            :title="route.meta.title"
          />
          <v-list-item
            @click.stop="toggleMiniNav()"
            :prepend-icon="mini ? 'mdi-chevron-right' : 'mdi-chevron-left'"
            title="Minimize"
          />
        </v-list>
      </v-navigation-drawer>
      <v-navigation-drawer width="220">
        <v-list density="compact" nav>
          <v-list-item>
            <v-text-field
              v-if="showFilter"
              v-model="q"
              append-inner-icon="mdi-magnify"
              label="Filter"
              single-line
              hide-details
            />
          </v-list-item>
          <span v-for="(subRoutes, group, idx) in children" :key="group">
            <v-list-subheader class="text-capitalize">
              {{ group }}
            </v-list-subheader>
            <v-list-item
              v-for="(route, subIndex) in subRoutes"
              :key="subIndex"
              :to="{ name: route.name, query: childrenQueryParams }"
            >
              <v-list-item-title>{{ route.meta.title }}</v-list-item-title>
            </v-list-item>
            <v-divider v-if="idx != Object.keys(children).length - 1" />
          </span>
        </v-list>
      </v-navigation-drawer>
    </v-layout>
  </v-navigation-drawer>
  <v-navigation-drawer permanent width="220" :rail="mini" v-else>
    <v-list density="compact" nav>
      <v-list-item
        v-for="(route, index) in routes"
        :key="index"
        :to="{ name: route.name }"
        :prepend-icon="route.meta.icon"
        :title="route.meta.title"
      >
        <v-tooltip v-if="mini" activator="parent" location="right" :text="route.meta.title" />
      </v-list-item>
      <v-list-item
        @click.stop="toggleMiniNav()"
        :prepend-icon="mini ? 'mdi-chevron-right' : 'mdi-chevron-left'"
        title="Minimize"
      >
        <v-tooltip v-if="mini" activator="parent" location="right" text="Minimize" />
      </v-list-item>
    </v-list>
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
    mini: false,
    q: "",
    showFilter: false,
  }),

  created() {
    this.mini = JSON.parse(localStorage.getItem("mini_nav"))
    this.$watch(
      () => this.$router.currentRoute.value.query.project,
      (val) => {
        this.showFilter = val
        if (!val) this.q = ""
      }
    )
  },

  methods: {
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
      return this.$router.currentRoute.value.query
    },
    showChildPane() {
      if (Object.keys(this.children).length) {
        return Object.values(this.children)[0].length || this.q.length
      }
      if (this.q.length) {
        return true
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

      // Filter children if we have a filter string
      if (this.$router.currentRoute.value.query.project) {
        let q = this.q
        if (q.length) {
          children = children.filter(function (item) {
            let metadata = item.meta.group.toLowerCase() + item.meta.title.toLowerCase()

            if (item.meta.subMenu) {
              metadata = metadata + item.meta.subMenu.toLowerCase()
            }
            return metadata.includes(q.toLowerCase())
          })
        }
      }

      children = groupBy(children, function (child) {
        return child.meta.group
      })

      return children
    },
    ...mapState("app", ["toggleDrawer"]),
  },
}
</script>
