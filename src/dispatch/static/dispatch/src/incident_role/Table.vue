<template>
  <v-layout wrap>
    <v-container>
      <v-row align="center" justify="space-between" no-gutters>
        <v-col>
          <settings-breadcrumbs v-model="breadCrumbProject" />
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-alert width="100%" icon="mdi-school" prominent text type="info"
          >Role policies defined below control the user resolution for a incident role. It uses
          incident characteristics (e.g IncidentType, IncidentPriority, etc.,) and the order of the
          policies to determine the correct user.
        </v-alert>
      </v-row>
      <v-row no-gutters>
        <v-col>
          <policy-role-builder label="Incident Commander" :project="project" />
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col>
          <policy-role-builder label="Liasion" :project="project" />
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col>
          <policy-role-builder label="Scribe" :project="project" />
        </v-col>
      </v-row>
    </v-container>
  </v-layout>
</template>

<script>
import { mapFields } from "vuex-map-fields"

import PolicyRoleBuilder from "@/incident_role/PolicyRoleBuilder.vue"
import SettingsBreadcrumbs from "@/components/SettingsBreadcrumbs.vue"

export default {
  name: "IncidentRoleTable",

  components: {
    PolicyRoleBuilder,
    SettingsBreadcrumbs,
  },

  computed: {
    ...mapFields("route", ["query"]),
  },

  created() {
    this.breadCrumbProject = [{ name: this.query.project }]
    this.project = { name: this.query.project }
    this.$watch(
      (vm) => [vm.breadCrumbProject],
      () => {
        this.$router.push({ query: { project: this.breadCrumbProject[0].name } })
      }
    )
  },
}
</script>
