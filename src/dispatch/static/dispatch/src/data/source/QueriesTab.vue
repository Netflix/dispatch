<template>
  <v-container fluid>
    <v-row>
      <v-col>
        <v-card>
          <v-card-text class="pt-0">
            <div class="text-h6 font-weight-light mb-2">Releated Queries</div>
            <v-data-table :headers="headers" :items="queries"></v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mapFields } from "vuex-map-fields"

export default {
  name: "SourceDetailsTab",

  components: {},

  computed: {
    ...mapFields("source", ["selected.queries", "selected.loading"]),
  },

  data() {
    return {
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
