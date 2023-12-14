<template>
  <v-container fluid>
    <v-row align="center" justify="space-between" no-gutters>
      <v-col cols="8">
        <settings-breadcrumbs v-model="breadCrumbProject" />
      </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col>
        <v-alert closable icon="mdi-school" prominent text type="info">
          Role policies defined below control the user resolution for an incident role. It uses
          incident characteristics (e.g type, priority, etc.) and the order of the policies to
          determine the correct user.
        </v-alert>
      </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col>
        <policy-role-builder label="Incident Commander" :project="project" />
      </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col>
        <policy-role-builder label="Liaison" :project="project" />
      </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col>
        <policy-role-builder label="Scribe" :project="project" />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import PolicyRoleBuilder from "@/incident_role/PolicyRoleBuilder.vue"
import SettingsBreadcrumbs from "@/components/SettingsBreadcrumbs.vue"

export default {
  name: "IncidentRoleTable",

  components: {
    PolicyRoleBuilder,
    SettingsBreadcrumbs,
  },

  created() {
    this.breadCrumbProject = [{ name: this.$route.query.project }]
    this.project = { name: this.$route.query.project }
    this.$watch(
      (vm) => [vm.breadCrumbProject],
      () => {
        this.$router.push({ query: { project: this.breadCrumbProject[0].name } })
      }
    )
  },
}
</script>

<style>
.mdi-school {
  color: white !important;
}
</style>
