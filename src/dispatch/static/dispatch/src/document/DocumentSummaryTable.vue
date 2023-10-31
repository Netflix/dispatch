<template>
  <v-data-table :headers="headers" :items="items">
    <template #item.name="{ item, value }">
      <a :href="item.weblink" target="_blank" style="text-decoration: none">
        {{ value }}
        <v-icon size="small">mdi-open-in-new</v-icon>
      </a>
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
export default {
  name: "DocumentSummaryTable",

  data() {
    return {
      headers: [
        { title: "Name", key: "name", sortable: false },
        { title: "Description", key: "description", sortable: false },
        { title: "Project", key: "project.name", sortable: true },
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
    ...mapActions("document", ["createEditShow", "removeShow"]),
  },
}
</script>
