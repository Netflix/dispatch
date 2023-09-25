<template>
  <v-data-table :headers="headers" :items="items">
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
          <v-list-item :to="{ name: 'QueryTableEdit', params: { name: item.name } }">
            <v-list-item-title>View / Edit</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </template>
  </v-data-table>
</template>

<script>
import { mapActions } from "vuex"
export default {
  name: "QuerySummaryTable",

  data() {
    return {
      headers: [
        { title: "Name", key: "name", sortable: true },
        { title: "Project", key: "project.name", sortable: false },
        { title: "Description", key: "description", sortable: false },
        { title: "Language", key: "language", sortable: true },
        {
          title: "",
          key: "data-table-actions",
          sortable: false,
          align: "end",
        },
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
    ...mapActions("query", ["removeShow"]),
  },
}
</script>
