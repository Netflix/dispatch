<template>
  <v-form @submit.prevent v-slot="{ isValid }">
    <v-navigation-drawer v-model="showCreateEdit" location="right" width="500">
      <template #prepend>
        <v-list-item lines="two">
          <v-list-item-title v-if="id" class="text-h6"> Edit </v-list-item-title>
          <v-list-item-title v-else class="text-h6"> New </v-list-item-title>
          <v-list-item-subtitle>Member</v-list-item-subtitle>

          <template #append>
            <v-btn
              icon
              variant="text"
              color="info"
              :loading="loading"
              :disabled="!isValid.value"
              @click="save()"
            >
              <v-icon>mdi-content-save</v-icon>
            </v-btn>
            <v-btn icon variant="text" color="secondary" @click="closeCreateEdit">
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </template>
        </v-list-item>
      </template>
      <v-card>
        <v-card-text>
          <v-container>
            <v-row>
              <v-col cols="12">
                <span class="text-subtitle-2">Details</span>
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="email"
                  :disabled="id !== null"
                  label="Email"
                  hint="Member's email."
                  name="Email"
                  :rules="[rules.required]"
                />
              </v-col>
              <v-col v-if="!id" cols="12">
                <v-text-field
                  v-model="password"
                  type="password"
                  label="Password"
                  name="Password"
                  :rules="[rules.required]"
                />
              </v-col>
              <v-col cols="12">
                <span class="text-subtitle-2">Role</span>
              </v-col>
              <v-col cols="12">
                <v-radio-group v-model="role">
                  <v-tooltip max-width="250px" location="left">
                    <template #activator="{ props }">
                      <v-radio v-bind="props" label="Member" value="Member" />
                    </template>
                    <span>
                      Members can view and act on incidents, as well as view most other data within
                      the organization.
                    </span>
                  </v-tooltip>
                  <v-tooltip max-width="250px" location="left">
                    <template #activator="{ props }">
                      <v-radio v-bind="props" label="Admin" value="Admin" />
                    </template>
                    <span>
                      Admin privileges on any teams of which they're a member. They can create new
                      teams and projects, as well as remove teams and projects which they already
                      hold membership on (or all teams, if open membership is on). Additionally,
                      they can manage memberships of teams that they are members of.
                    </span>
                  </v-tooltip>
                  <v-tooltip max-width="250px" location="left">
                    <template #activator="{ props }">
                      <v-radio v-bind="props" label="Manager" value="Manager" />
                    </template>
                    <span>
                      Gains admin access on all teams as well as the ability to add and remove
                      members.
                    </span>
                  </v-tooltip>
                  <v-tooltip max-width="250px" location="left">
                    <template #activator="{ props }">
                      <v-radio v-bind="props" label="Owner" value="Owner" />
                    </template>
                    <span
                      >Unrestricted access to the organization, its data, and its settings. Can add,
                      modify, and delete projects and members.</span
                    >
                  </v-tooltip>
                </v-radio-group>
              </v-col>
              <v-col cols="12">
                <span class="text-subtitle-2">Settings</span>
              </v-col>
              <v-col cols="12">
                <v-list-item>
                  <project-combobox v-model="defaultProjects" label="Default Projects" />
                </v-list-item>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
      </v-card>
    </v-navigation-drawer>
  </v-form>
</template>

<script>
import { required } from "@/util/form"
import { map } from "lodash"

import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

import ProjectCombobox from "@/project/ProjectCombobox.vue"

export default {
  setup() {
    return {
      rules: { required },
    }
  },
  name: "MemberEditSheet",

  components: {
    ProjectCombobox,
  },

  computed: {
    ...mapFields("auth", [
      "selected.email",
      "selected.projects",
      "selected.password",
      "selected.role",
      "selected.id",
      "selected.loading",
      "dialogs.showCreateEdit",
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
      },
    },
  },

  methods: {
    ...mapActions("auth", ["save", "closeCreateEdit"]),
  },
}
</script>
