<template>
  <v-container grid-list-md>
    <v-autocomplete
      v-model="selectedQuery"
      :items="items"
      item-text="Detections"
      item-value="API"
      label="Associate Query"
      placeholder="Start typing to Search"
      prepend-icon="mdi-database-search"
      return-object
    ></v-autocomplete>
    <v-data-table
      :headers="headers"
      :items="queries"
      :items-per-page="5"
      class="elevation-1"
    ></v-data-table>
  </v-container>
</template>

<script>
import { mapFields } from "vuex-map-fields"

export default {
  name: "SourceEditQueriesTab",

  components: {},

  computed: {
    ...mapFields("source", ["selected.source.queries", "selected.loading"]),
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
