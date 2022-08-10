<template>
  <v-navigation-drawer v-model="showEdit" app clipped right width="500">
    <template v-slot:prepend>
      <v-list-item two-line>
        <v-list-item-content>
          <v-list-item-title class="title"> Edit </v-list-item-title>
          <v-list-item-subtitle>Member</v-list-item-subtitle>
        </v-list-item-content>
        <v-btn icon color="info" :loading="loading" @click="save()">
          <v-icon>save</v-icon>
        </v-btn>
        <v-btn icon color="secondary" @click="closeEdit">
          <v-icon>close</v-icon>
        </v-btn>
      </v-list-item>
    </template>
    <v-card flat>
      <v-card-text>
        <v-container grid-list-md>
          <v-layout wrap>
            <v-flex xs12>
              <span class="subtitle-2">Contact Information</span>
            </v-flex>
            <v-flex xs12>
              <v-text-field v-model="email" disabled label="Email" hint="Member's email." />
            </v-flex>
            <v-flex xs12>
              <span class="subtitle-2">Role</span>
            </v-flex>
            <v-flex xs12>
              <v-radio-group v-model="role" column>
                <v-tooltip max-width="250px" left>
                  <template v-slot:activator="{ on, attrs }">
                    <v-radio v-bind="attrs" v-on="on" label="Member" value="Member"> </v-radio>
                  </template>
                  <span>
                    Members can view and act on incidents, as well as view most other data within
                    the organization.
                  </span>
                </v-tooltip>
                <v-tooltip max-width="250px" left>
                  <template v-slot:activator="{ on, attrs }">
                    <v-radio v-bind="attrs" v-on="on" label="Admin" value="Admin"> </v-radio>
                  </template>
                  <span>
                    Admin privileges on any teams of which they're a member. They can create new
                    teams and projects, as well as remove teams and projects which they already hold
                    membership on (or all teams, if open membership is on). Additionally, they can
                    manage memberships of teams that they are members of.
                  </span>
                </v-tooltip>
                <v-tooltip max-width="250px" left>
                  <template v-slot:activator="{ on, attrs }">
                    <v-radio v-bind="attrs" v-on="on" label="Manager" value="Manager"> </v-radio>
                  </template>
                  <span>
                    Gains admin access on all teams as well as the ability to add and remove
                    members.
                  </span>
                </v-tooltip>
                <v-tooltip max-width="250px" left>
                  <template v-slot:activator="{ on, attrs }">
                    <v-radio v-bind="attrs" v-on="on" label="Owner" value="Owner"> </v-radio>
                  </template>
                  <span
                    >Unrestricted access to the organization, its data, and its settings. Can add,
                    modify, and delete projects and members.</span
                  >
                </v-tooltip>
              </v-radio-group>
            </v-flex>
            <v-flex xs12>
              <span class="subtitle-2">Settings</span>
            </v-flex>
            <v-flex xs12>
              <v-list-item>
                <v-list-item-content>
                  <project-combobox v-model="defaultProjects" label="Default Projects" />
                </v-list-item-content>
              </v-list-item>
            </v-flex>
          </v-layout>
        </v-container>
      </v-card-text>
    </v-card>
  </v-navigation-drawer>
</template>

<script>
import { map } from "lodash"

import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

import ProjectCombobox from "@/project/ProjectCombobox.vue"

export default {
  name: "MemberEditSheet",

  components: {
    ProjectCombobox,
  },

  computed: {
    ...mapFields("auth", [
      "selected.email",
      "selected.projects",
      "selected.role",
      "selected.id",
      "selected.loading",
      "dialogs.showEdit",
    ]),

    defaultProjects: {
      get() {
        let d = null
        if (this.projects) {
          let d = this.projects.filter((v) => v.default === true)
          return d.map((v) => v.project)
        }
        return d
      },
      set(value) {
        let wrapped = map(value, function (item) {
          return { project: item, default: true }
        })
        this.projects = wrapped
        this.$emit("input", wrapped)
      },
    },
  },

  methods: {
    ...mapActions("auth", ["save", "closeEdit"]),
  },
}
</script>
