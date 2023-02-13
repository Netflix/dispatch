<template>
  <v-bottom-sheet v-model="showBulkEdit" hide-overlay persistent>
    <handoff-dialog />
    <v-card :loading="bulkEditLoading" tile>
      <v-list>
        <v-list-item>
          <v-list-item-content>
            <v-list-item-subtitle>{{ selected.length }} selected</v-list-item-subtitle>
          </v-list-item-content>
          <v-spacer />
          <v-list-item-icon>
            <v-btn text @click="showHandoffDialog()">
              <v-icon>mdi-account-arrow-right</v-icon>
              Handoff
            </v-btn>
          </v-list-item-icon>
          <v-list-item-icon>
            <v-btn text @click="saveBulk({ status: 'New' })">
              <v-icon>mdi-alert-decagram</v-icon>
              Mark New
            </v-btn>
          </v-list-item-icon>
          <v-list-item-icon>
            <v-btn text @click="saveBulk({ status: 'Triage' })">
              <v-icon>mdi-check</v-icon>
              Mark Triage
            </v-btn>
          </v-list-item-icon>
          <v-list-item-icon>
            <v-btn text @click="saveBulk({ status: 'Closed' })">
              <v-icon>mdi-close</v-icon>
              Mark Closed
            </v-btn>
          </v-list-item-icon>
          <v-list-item-icon>
            <v-btn text color="primary" @click="deleteBulk()">
              <v-icon color="primary">mdi-delete</v-icon>
              Delete
            </v-btn>
          </v-list-item-icon>
        </v-list-item>
      </v-list>
    </v-card>
  </v-bottom-sheet>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

import HandoffDialog from "@/case/HandoffDialog.vue"

export default {
  name: "CaseBulkEditSheet",

  components: {
    HandoffDialog,
  },

  computed: {
    ...mapFields("case_management", ["table.rows.selected", "table.bulkEditLoading"]),

    showBulkEdit: function () {
      return this.selected.length ? true : false
    },
  },

  methods: {
    ...mapActions("case_management", ["saveBulk", "deleteBulk", "showHandoffDialog"]),
  },
}
</script>
