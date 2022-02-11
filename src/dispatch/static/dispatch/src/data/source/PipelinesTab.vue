<template>
  <v-container fluid>
    <v-row>
      <v-col>
        <v-card>
          <v-sheet color="blue">
            <v-sparkline
              :labels="labels"
              :value="value"
              color="white"
              line-width="1"
              height="50"
            ></v-sparkline>
          </v-sheet>
          <v-card-text class="pt-0">
            <div class="text-h6 font-weight-light mb-2">Related Incidents</div>
            <incident-summary-table :items="incidents" />
            <v-divider class="my-2"></v-divider>
            <v-icon class="mr-2" small> mdi-clock </v-icon>
            <span class="text-caption grey--text font-weight-light">last incident 10min ago</span>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import IncidentSummaryTable from "@/incident/IncidentSummaryTable.vue"

export default {
  name: "SourceDetailsTab",

  components: {
    IncidentSummaryTable,
  },

  computed: {
    ...mapFields("source", ["selected.source.incidents", "selected.loading"]),
  },

  data() {
    return {
      labels: ["Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun"],
      value: [200, 675, 410, 390, 310, 460, 250, 240],
    }
  },
}
</script>
