<template>
  <v-menu offset-y :close-on-content-click="false">
    <template v-slot:activator="{ on }">
      <v-btn icon large text v-on="on">
        <v-avatar size="30px">
          <v-icon> account_circle </v-icon>
        </v-avatar>
      </v-btn>
    </template>
    <v-card width="400">
      <v-list>
        <v-list-item class="px-2">
          <v-list-item-avatar>
            <v-icon size="30px"> account_circle </v-icon>
          </v-list-item-avatar>
          <v-list-item-content>
            <v-list-item-title class="title" v-text="user.name || user.email"> </v-list-item-title>
            <v-list-item-subtitle> {{ user.email }} </v-list-item-subtitle>
          </v-list-item-content>
          <v-list-item-action>
            <v-tooltip bottom>
              <template v-slot:activator="{ on }">
                <v-btn icon v-on="on" @click="showMemberEditDialog(user)"
                  ><v-icon>edit</v-icon></v-btn
                >
              </template>
              <span>Edit</span>
            </v-tooltip>
          </v-list-item-action>
          <v-list-item-action>
            <v-tooltip bottom>
              <template v-slot:activator="{ on }">
                <v-btn icon v-on="on" @click="logout()"><v-icon>logout</v-icon></v-btn>
              </template>
              <span>Logout</span>
            </v-tooltip>
          </v-list-item-action>
        </v-list-item>
        <v-divider></v-divider>
        <v-subheader>My Organizations</v-subheader>
        <v-list-item v-for="item in user.organizations" :key="item.id">
          <v-list-item-action>
            <v-tooltip bottom>
              <template v-slot:activator="{ on }">
                <v-btn icon v-on="on" @click="setDefault(item)">
                  <v-icon v-if="item.default">mdi-star</v-icon>
                  <v-icon v-else="item.default">mdi-star-outline</v-icon>
                </v-btn>
              </template>
              <span>Mark as Default</span>
            </v-tooltip>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title
              ><router-link :to="{ params: { organization: item.slug }, force: true }">{{
                item.name
              }}</router-link></v-list-item-title
            >
            <v-list-item-subtitle>{{ item.description }}</v-list-item-subtitle>
          </v-list-item-content>
          <v-list-item-action>
            <v-tooltip bottom>
              <template v-slot:activator="{ on }">
                <v-btn icon v-on="on" @click="showCreateEditDialog(item)"
                  ><v-icon>mdi-pencil-outline</v-icon></v-btn
                >
              </template>
              <span>Edit Organization</span>
            </v-tooltip>
          </v-list-item-action>
        </v-list-item>
      </v-list>
      <v-list-item @click="showCreateEditDialog()">
        <v-list-item-avatar>
          <v-icon size="30px">mdi-plus</v-icon>
        </v-list-item-avatar>
        <v-list-item-content>
          <v-list-item-title>Create a new organization</v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </v-card>
  </v-menu>
</template>
<script>
import { mapActions, mapState } from "vuex"

export default {
  name: "OrganizationMenu",
  data: () => ({
    user: null,
  }),
  created() {
    this.user = this.currentUser()
  },
  methods: {
    setDefault(defaultOrganization) {
      user.organizations.forEach(function (organization) {
        if (organization.id === defaultOrganization.id) {
          organization.default = true
        } else {
          organization.default = false
        }
      })
      this.updateMember(user)
    },
    ...mapState("auth", ["currentUser", "userAvatarUrl"]),
    ...mapActions("auth", ["logout"]),
    ...mapActions("organization", ["showCreateEditDialog", "showMemberEditDialog", "updateMember"]),
  },
}
</script>
