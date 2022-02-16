<template>
  <v-container grid-list-md>
    <query-select v-model="selectedQuery" />
    <v-data-table :headers="headers" :items="queries" :items-per-page="5"></v-data-table>
  </v-container>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import QuerySelect from "@/data/query/QuerySelect.vue"

export default {
  name: "SourceEditQueriesTab",

  components: {
    QuerySelect,
  },

  computed: {
    ...mapFields("source", ["selected.queries", "selected.loading"]),
  },

  data() {
    return {
      selectedQuery: null,
      headers: [
        {
          text: "Name",
          align: "start",
          sortable: false,
          value: "name",
        },
        { text: "Description", value: "description" },
      ],
    }
  },
}
</script>
