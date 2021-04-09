<template>
  <v-container>
    <v-row no-gutter>
      <span class="subtitle-2">{{ label }}</span>
      <v-spacer />
      <v-tooltip bottom>
        <template v-slot:activator="{ on }">
          <v-btn small icon @click="addRole()" v-on="on">
            <v-icon>add</v-icon>
          </v-btn>
        </template>
        <span>Add Role</span>
      </v-tooltip>
    </v-row>
    <span v-for="(role, idx) in value" :key="idx">
      <v-row align="center" dense>
        <v-col cols="12" sm="1">
          <v-tooltip bottom>
            <template v-slot:activator="{ on }">
              <v-btn small icon @click="removeRole(idx)" v-on="on"><v-icon>remove</v-icon></v-btn>
            </template>
            <span>Remove Role</span>
          </v-tooltip>
        </v-col>
        <v-col cols="12" sm="10">
          <project-select v-model="role.project" label="Project" />
          <v-select v-model="role.role" :items="availableRoles.project" label="Role" />
          <v-checkbox v-model="role.default" label="Default Project"></v-checkbox>
        </v-col>
      </v-row>
      <v-divider />
    </span>
  </v-container>
</template>

<script>
import ProjectSelect from "@/project/ProjectSelect.vue"
export default {
  name: "UserRoleCombobox",

  components: {
    ProjectSelect,
  },

  props: {
    value: {
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
      this.value.push({ role: "Member", default: false, project: null })
    },
    removeRole(idx) {
      this.value.splice(idx)
    },
  },
}
</script>
