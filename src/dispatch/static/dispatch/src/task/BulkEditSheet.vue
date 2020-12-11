<template>
  <v-bottom-sheet v-model="showBulkEdit" hide-overlay persistent>
    <v-card :loading="bulkEditLoading" tile>
      <template slot="progress">
        <v-progress-linear color="error" indeterminate></v-progress-linear>
      </template>
      <v-list>
        <v-list-item>
          <v-list-item-content>
            <v-list-item-subtitle>{{ selected.length }} selected</v-list-item-subtitle>
          </v-list-item-content>

          <v-spacer></v-spacer>

          <v-list-item-icon>
            <v-btn text @click="saveBulk({ status: 'Resolved' })">
              <v-icon>mdi-check</v-icon>
              Mark Resolved
            </v-btn>
          </v-list-item-icon>

          <v-list-item-icon>
            <v-btn text @click="saveBulk({ status: 'Open' })">
              <v-icon>mdi-close</v-icon>
              Mark Open
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
export default {
  name: "TaskBulkEditSheet",

  computed: {
    ...mapFields("task", ["table.rows.selected", "table.bulkEditLoading"]),

    showBulkEdit: function() {
      return this.selected.length ? true : false
    }
  },

  methods: {
    ...mapActions("task", ["saveBulk"])
  }
}
</script>
