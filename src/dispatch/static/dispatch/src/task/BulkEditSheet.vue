<template>
  <v-bottom-sheet v-model="showBulkEdit" hide-overlay persistent>
    <v-card :loading="bulkEditLoading" rounded="0">
      <template #progress>
        <v-progress-linear color="primary" indeterminate />
      </template>
      <v-list>
        <v-list-item>
          <v-list-item-subtitle>{{ selected.length }} selected</v-list-item-subtitle>

          <template #append>
            <v-btn variant="text" @click="saveBulk({ status: 'Resolved' })">
              <v-icon>mdi-check</v-icon>
              Mark Resolved
            </v-btn>

            <v-btn variant="text" @click="saveBulk({ status: 'Open' })">
              <v-icon>mdi-close</v-icon>
              Mark Open
            </v-btn>
          </template>
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

    showBulkEdit: function () {
      return this.selected.length ? true : false
    },
  },

  methods: {
    ...mapActions("task", ["saveBulk"]),
  },
}
</script>
