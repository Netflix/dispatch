<template>
  <v-navigation-drawer app permanent width="440" clipped class="background1">
    <v-row class="fill-height" no-gutters>
      <v-navigation-drawer width="220" permanent>
        <v-list dense nav>
          <v-list-item v-for="item in items" :key="item.title">
            <v-list-item-action>
              <v-icon>{{ item.icon }}</v-icon>
            </v-list-item-action>

            <v-list-item-content>
              <v-list-item-title>{{ item.title }}</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list>
      </v-navigation-drawer>

      <v-list class="grow">
        <v-list-item v-for="link in links" :key="link" link>
          <v-list-item-title v-text="link"></v-list-item-title>
        </v-list-item>
      </v-list>
    </v-row>
  </v-navigation-drawer>
</template>
<script>
import { mapState } from "vuex"
export default {
  name: "AppDrawer",
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
    links: ["Home", "Contacts", "Settings"],
    items: [
      { title: "Projects", icon: "mdi-view-dashboard" },
      { title: "Incidents", icon: "mdi-view-dashboard" },
      { title: "Tasks", icon: "mdi-forum" }
    ],
    items2: [
      {
        action: "project",
        items: [
          { title: "Incidents", route: "/dashboard/incidents" },
          { title: "Tasks", route: "/dashboard/tasks" }
        ],
        title: "Projects"
      },
      {
        action: "incidents",
        items: [
          { title: "Incidents", route: "/dashboard/incidents" },
          { title: "Tasks", route: "/dashboard/tasks" }
        ],
        title: "Incidents"
      },
      {
        action: "task",
        items: [
          { title: "Incidents", route: "/dashboard/incidents" },
          { title: "Tasks", route: "/dashboard/tasks" }
        ],
        title: "Tasks"
      },
      {
        action: "dashboard",
        items: [
          { title: "Incidents", route: "/dashboard/incidents" },
          { title: "Tasks", route: "/dashboard/tasks" }
        ],
        title: ""
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
          { title: "Incident Cost Types", route: "/configuration/incidentCostTypes" },
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
