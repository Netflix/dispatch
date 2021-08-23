<style scoped>
.v-expansion-panel--active::before {
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
  <v-layout wrap>
    <delete-dialog />
    <v-container>
      <v-row align="center" justify="space-between">
        <v-col class="grow">
          <settings-breadcrumbs v-model="breadCrumbProject" />
        </v-col>
      </v-row>
      <v-row>
        <v-alert icon="mdi-school" prominent text type="info"
          >The role policies defined below control which user is assigned a given role. It uses
          incident characteristics (e.g IncidentType, IncidentPriority, etc.,) to resolve the
          individual. Policy order is used to resolve any conflicting policies.
        </v-alert>
      </v-row>
      <v-row>
        <v-col cols="12">
          <policy-role-builder label="Commander" v-model="commanderPolicies" :project="project" />
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12">
          <policy-role-builder label="Liasion" v-model="liasionPolicies" :project="project" />
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12">
          <policy-role-builder label="Scribe" v-model="scribePolicies" :project="project" />
        </v-col>
      </v-row>
    </v-container>
  </v-layout>
</template>

<script>
import { filter } from "lodash"
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

import PolicyRoleBuilder from "@/incident_role/PolicyRoleBuilder.vue"
import SettingsBreadcrumbs from "@/components/SettingsBreadcrumbs.vue"
import DeleteDialog from "@/incident_role/DeleteDialog.vue"

export default {
  name: "IncidentRoleTable",

  components: {
    PolicyRoleBuilder,
    DeleteDialog,
    SettingsBreadcrumbs,
  },

  computed: {
    commanderPolicies: function () {
      return filter(this.items, { role: "Incident Commander" })
    },
    liasionPolicies: function () {
      return filter(this.items, { role: "Liasion" })
    },
    scribePolicies: function () {
      return filter(this.items, { role: "Scribe" })
    },
    ...mapFields("incident_role", ["table.rows.items", "table.loading"]),
    ...mapFields("route", ["query"]),
  },

  created() {
    this.breadCrumbProject = [{ name: this.query.project }]
    this.project = { name: this.query.project }

    this.getAll()

    this.$watch(
      (vm) => [vm.page],
      () => {
        this.getAll()
      }
    )

    this.$watch(
      (vm) => [vm.breadCrumbProject],
      () => {
        this.page = 1
        this.$router.push({ query: { project: this.breadCrumbProject[0].name } })
        this.getAll()
      }
    )
  },

  methods: {
    ...mapActions("incident_role", ["getAll"]),
  },
}
</script>
