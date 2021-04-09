<template>
  <v-navigation-drawer v-model="showEdit" app clipped right width="500">
    <template v-slot:prepend>
      <v-list-item two-line>
        <v-list-item-content>
          <v-list-item-title class="title"> Edit </v-list-item-title>
          <v-list-item-subtitle>User</v-list-item-subtitle>
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
              <span class="subtitle-2">Details</span>
            </v-flex>
            <v-flex xs12>
              <v-text-field v-model="email" disabled label="Email" hint="User's email." />
            </v-flex>
            <v-flex xs12>
              <user-role-combobox
                v-model="projects"
                label="Roles"
                hint="The user's current roles"
              />
            </v-flex>
          </v-layout>
        </v-container>
      </v-card-text>
    </v-card>
  </v-navigation-drawer>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import UserRoleCombobox from "@/auth/UserRoleCombobox.vue"

export default {
  name: "UserEditSheet",

  components: {
    UserRoleCombobox,
  },

  computed: {
    ...mapFields("auth", [
      "selected.email",
      "selected.projects",
      "selected.organizations",
      "selected.id",
      "selected.loading",
      "dialogs.showEdit",
    ]),
  },

  methods: {
    ...mapActions("auth", ["save", "closeEdit"]),
  },
}
</script>
