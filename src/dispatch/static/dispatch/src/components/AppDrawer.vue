<template>
  <v-navigation-drawer app :value="toggleDrawer" permanent clipped class="background1">
    <vue-perfect-scrollbar class="drawer-menu--scroll" :settings="scrollSettings">
      <v-list nav>
        <v-list-group v-for="item in items" :key="item.title" v-model="item.active" no-action>
          <template v-slot:activator>
            <v-list-item-content>
              <v-list-item-title v-text="item.title"></v-list-item-title>
            </v-list-item-content>
          </template>

          <v-list-item v-for="child in item.items" :key="child.title" :to="child.route" exact>
            <v-list-item-content>
              <v-list-item-title v-text="child.title"></v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list-group>
      </v-list>
    </vue-perfect-scrollbar>
    <template v-slot:append>
      <div class="pa-3">
        <v-btn color="error" block to="/incidents/report">
          <v-icon left>error_outline</v-icon>
          Report Incident
        </v-btn>
      </div>
    </template>
  </v-navigation-drawer>
</template>
<script>
import { mapState } from "vuex"
import VuePerfectScrollbar from "vue-perfect-scrollbar"
export default {
  name: "AppDrawer",
  components: {
    VuePerfectScrollbar
  },
  props: {
    expanded: {
      type: Boolean,
      default: true
    },
    drawWidth: {
      type: [Number, String],
      default: "260"
    }
  },

  data: () => ({
    items: [
      {
        action: "dashboard",
        items: [
          { title: "Incidents", route: "/dashboard/incidents" },
          { title: "Tasks", route: "/dashboard/tasks" }
        ],
        title: "Dashboard"
      },
      {
        action: "error_outline",
        items: [
          { title: "Incidents", route: "/incidents" },
          { title: "Tasks", route: "/tasks" },
          { title: "Feedback", route: "/feedback" }
        ],
        title: "Incident"
      },
      {
        action: "people",
        items: [
          { title: "Individuals", route: "/contact/individuals" },
          { title: "Teams", route: "/contact/teams" },
          { title: "Services", route: "/contact/services" }
        ],
        title: "Contact"
      },
      {
        action: "book",
        items: [
          { title: "Tags", route: "/knowledge/tags" },
          { title: "Documents", route: "/knowledge/documents" },
          { title: "Terms", route: "/knowledge/terms" },
          { title: "Definitions", route: "/knowledge/definitions" }
        ],
        title: "Knowledge"
      },
      {
        action: "settings",
        items: [
          { title: "Incident Priorities", route: "/configuration/incidentPriorities" },
          { title: "Incident Types", route: "/configuration/incidentTypes" },
          { title: "Notifications", route: "/configuration/notifications" },
          { title: "Plugins", route: "/configuration/plugins" },
          { title: "Tag Types", route: "/configuration/tagTypes" },
          { title: "Users", route: "/configuration/users" },
          { title: "Workflows", route: "/configuration/workflows" }
        ],
        title: "Configuration"
      }
    ],
    scrollSettings: {
      maxScrollbarLength: 160
    }
  }),
  computed: {
    computeLogo() {
      return "/static/m.png"
    },
    ...mapState("app", ["toggleDrawer"])
  },
  created() {}
}
</script>
