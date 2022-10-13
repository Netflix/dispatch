<template>
  <v-dialog v-model="showMemberEditDialog" persistent max-width="600px">
    <v-card>
      <v-card-title>
        <span class="headline">User Settings</span>
      </v-card-title>
      <v-card-text>
        <v-text-field
          v-model="selectedMember.email"
          disabled
          label="Email"
          hint="Member's email."
        />
        <span class="subtitle-2">Organization Settings</span>
        <organization-member-organization-table v-model="selectedMember.organizations" />
        <span class="subtitle-2">Project Settings</span>
        <organization-member-project-table v-model="selectedMember.projects" />
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn text @click="closeMemberEditDialog()"> Cancel </v-btn>
        <v-btn color="info" text @click="updateMember()"> Update </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

import OrganizationMemberProjectTable from "@/organization/OrganizationMemberProjectTable.vue"
import OrganizationMemberOrganizationTable from "@/organization/OrganizationMemberOrganizationTable.vue"

export default {
  name: "OrganizationMemberEditDialog",
  components: {
    OrganizationMemberProjectTable,
    OrganizationMemberOrganizationTable,
  },

  computed: {
    ...mapFields("organization", ["dialogs.showMemberEditDialog", "selectedMember"]),
  },

  methods: {
    ...mapActions("organization", ["updateMember", "closeMemberEditDialog"]),
  },
}
</script>
