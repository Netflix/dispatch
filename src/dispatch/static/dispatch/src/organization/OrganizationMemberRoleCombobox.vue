<template>
  <v-container>
    <v-row no-gutter>
      <span class="text-subtitle-2">{{ label }}</span>
      <v-spacer />
      <v-tooltip location="bottom">
        <template #activator="{ props }">
          <v-btn size="small" icon variant="text" @click="addRole()" v-bind="props">
            <v-icon>mdi-plus</v-icon>
          </v-btn>
        </template>
        <span>Add Role</span>
      </v-tooltip>
    </v-row>
    <span v-for="(role, idx) in value" :key="idx">
      <v-row align="center" dense>
        <v-col cols="12" sm="1">
          <v-tooltip location="bottom">
            <template #activator="{ props }">
              <v-btn size="small" icon variant="text" @click="removeRole(idx)" v-bind="props"
                ><v-icon>mdi-minus</v-icon></v-btn
              >
            </template>
            <span>Remove Role</span>
          </v-tooltip>
        </v-col>
        <v-col cols="12" sm="10">
          <project-select v-model="role.project" label="Project" />
          <v-select v-model="role.role" :items="availableRoles.project" label="Role" />
          <v-checkbox v-model="role.default" label="Default Project" />
        </v-col>
      </v-row>
      <v-divider />
    </span>
  </v-container>
</template>

<script>
import ProjectSelect from "@/project/ProjectSelect.vue"
import { cloneDeep } from "lodash"

export default {
  name: "OrganizationMemberRoleCombobox",

  components: {
    ProjectSelect,
  },

  props: {
    modelValue: {
      type: Array,
      default: function () {
        return []
      },
    },
    type: {
      type: String,
      default: "project",
    },
    label: {
      type: String,
      default: "Role",
    },
  },

  data() {
    return {
      availableRoles: {
        project: ["Member", "Admin"],
        organization: ["Owner", "Manager"],
      },
    }
  },

  methods: {
    addRole() {
      const value = cloneDeep(this.modelValue)
      value.push({ role: "Member", default: false, project: null })
      this.$emit("update:modelValue", value)
    },
    removeRole(idx) {
      const value = cloneDeep(this.modelValue)
      value.splice(idx)
      this.$emit("update:modelValue", value)
    },
  },
}
</script>
