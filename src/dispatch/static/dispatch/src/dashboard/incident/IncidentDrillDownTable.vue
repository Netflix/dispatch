<template>
  <div>
    <v-card>
      <v-card-title>
        <v-text-field
          v-model="search"
          append-inner-icon="mdi-magnify"
          label="Search"
          single-line
          hide-details
          clearable
        />
      </v-card-title>
    </v-card>
    <v-data-table :headers="headers" :items="items" :loading="loading" :search="search">
      <template #item.project.name="{ item, value }">
        <v-chip size="small" :color="item.project.color">
          {{ value }}
        </v-chip>
      </template>
      <template #item.data-table-actions="{ item }">
        <v-menu location="right" origin="overlap">
          <template #activator="{ props }">
            <v-btn icon variant="text" v-bind="props">
              <v-icon>mdi-dots-vertical</v-icon>
            </v-btn>
          </template>
          <v-list>
            <v-list-item :to="{ name: 'IncidentTableEdit', params: { name: item.name } }">
              <v-list-item-title>View / Edit</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>
      </template>
    </v-data-table>
  </div>
</template>
<script>
export default {
  name: "IncidentSummaryTable",

  data() {
    return {
      search: "",
      headers: [
        { title: "Name", key: "name", align: "left", width: "10%" },
        { title: "Title", key: "title", sortable: false },
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
}
</script>
