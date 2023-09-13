<template>
  <new-edit-sheet />
  <v-data-table :headers="headers" :items="items">
    <template #item.discoverable="{ item }">
      <v-checkbox-btn v-model="item.raw.discoverable" disabled />
    </template>
    <template #item.project.name="{ item }">
      <v-chip size="small" :color="item.project.color">
        {{ item.raw.project.name }}
      </v-chip>
    </template>
    <template #item.tag_type.name="{ item }">
      {{ item.raw.tag_type.name }}
    </template>
    <template #item.data-table-actions="{ item }">
      <v-menu location="right" origin="overlap">
        <template #activator="{ props }">
          <v-btn icon="mdi-dots-vertical" variant="text" v-bind="props" />
        </template>
        <v-list>
          <v-list-item @click="createEditShow(item.raw)">
            <v-list-item-title>View / Edit</v-list-item-title>
          </v-list-item>
          <v-list-item @click="removeShow(item.raw)">
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
        { text: "Name", value: "name", sortable: true },
        { text: "Description", value: "description", sortable: false },
        { text: "Type", value: "tag_type.name", sortable: true },
        { text: "Source", value: "source", sortable: true },
        { text: "Project", value: "project.name", sortable: true },
        { text: "Discoverable", value: "discoverable", sortable: true },
        { text: "", value: "data-table-actions", sortable: false, align: "end" },
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
