<template>
  <v-breadcrumbs :items="crumbs">
    <template v-slot:divider>
      <v-icon>mdi-chevron-right</v-icon>
    </template>
    <template v-slot:item="{ item }">
      <v-breadcrumbs-item v-if="item.projectSelect">
        <project-menu-select v-model="project" />
      </v-breadcrumbs-item>
      <v-breadcrumbs-item v-else-if="item.organizationSelect">
        <organization-menu-select v-model="localOrganization" />
      </v-breadcrumbs-item>
      <v-breadcrumbs-item v-else :to="item.to" :disabled="item.disabled">
        {{ item.text | capitalize }}
      </v-breadcrumbs-item>
    </template>
  </v-breadcrumbs>
</template>

<script>
import { mapFields } from "vuex-map-fields"

import ProjectMenuSelect from "@/project/ProjectMenuSelect.vue"
import OrganizationMenuSelect from "@/organization/OrganizationMenuSelect.vue"

export default {
  name: "SettingsBreadCrumbs",

  props: {
    value: {
      type: Array,
      default: function () {
        return []
      },
    },
    organization: {
      type: Array,
      default: function () {
        return []
      },
    },
  },

  components: {
    ProjectMenuSelect,
    OrganizationMenuSelect,
  },

  computed: {
    project: {
      get() {
        return this.value[0]
      },
      set(value) {
        this.$emit("input", [value])
      },
    },
    localOrganization: {
      get() {
        return this.value[0]
      },
      set(value) {
        this.$emit("organization", [value])
      },
    },
    crumbs() {
      return [
        {
          text: "Settings",
          disabled: false,
        },
        {
          organizationSelect: true,
        },
        {
          projectSelect: true,
        },
        {
          text: this.meta.title,
          disabled: false,
        },
      ]
    },
    ...mapFields("route", ["query", "params", "meta"]),
  },
}
</script>
