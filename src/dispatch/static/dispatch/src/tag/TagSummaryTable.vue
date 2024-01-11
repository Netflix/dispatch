<template>
  <new-edit-sheet />
  <v-data-table :headers="headers" :items="items">
    <template #item.discoverable="{ value }">
      <v-checkbox-btn :model-value="value" disabled />
    </template>
    <template #item.project.name="{ item, value }">
      <v-chip size="small" :color="item.project.color">
        {{ value }}
      </v-chip>
    </template>
    <template #item.data-table-actions="{ item }">
      <v-menu location="right" origin="overlap">
        <template #activator="{ props }">
          <v-btn icon="mdi-dots-vertical" variant="text" v-bind="props" />
        </template>
        <v-list>
          <v-list-item @click="createEditShow(item)">
            <v-list-item-title>View / Edit</v-list-item-title>
          </v-list-item>
          <v-list-item @click="removeShow(item)">
            <v-list-item-title>Delete</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </template>
  </v-data-table>
</template>

<script>
import { mapActions } from "vuex"
import NewEditSheet from "@/tag/NewEditSheet.vue"

export default {
  name: "TagSummaryTable",

  components: {
    NewEditSheet,
  },

  data() {
    return {
      headers: [
        { title: "Name", value: "name", sortable: true },
        { title: "Description", value: "description", sortable: false },
        { title: "Type", value: "tag_type.name", sortable: true },
        { title: "Source", value: "source", sortable: true },
        { title: "Project", value: "project.name", sortable: true },
        { title: "Discoverable", value: "discoverable", sortable: true },
        { title: "", key: "data-table-actions", sortable: false, align: "end" },
      ],
    }
  },

  props: {
    items: {
      default: function () {
        return []
      },
      type: Array,
    },
    loading: {
      default: function () {
        return false
      },
      type: [String, Boolean],
    },
  },

  methods: {
    ...mapActions("tag", ["createEditShow", "removeShow"]),
  },
}
</script>
