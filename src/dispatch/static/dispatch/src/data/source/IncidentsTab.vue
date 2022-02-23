<template>
  <v-container fluid>
    <v-row>
      <v-col>
        <incident-type-bar-chart-card v-model="groupedItems" :loading="loading" />
      </v-col>
      <v-col>
        <incident-priority-bar-chart-card v-model="groupedItems" :loading="loading" />
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <v-card>
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
import { groupBy } from "lodash"
import { parseISO } from "date-fns"

import IncidentPriorityBarChartCard from "@/incident/IncidentPriorityBarChartCard.vue"
import IncidentTypeBarChartCard from "@/incident/IncidentTypeBarChartCard.vue"
import IncidentSummaryTable from "@/incident/IncidentSummaryTable.vue"

export default {
  name: "SourceDetailsTab",

  components: {
    IncidentPriorityBarChartCard,
    IncidentTypeBarChartCard,
    IncidentSummaryTable,
  },

  computed: {
    ...mapFields("source", ["selected.incidents", "selected.loading"]),
    incidentsByMonth() {
      return groupBy(this.incidents, function (item) {
        return parseISO(item.reported_at).toLocaleString("default", { month: "short" })
      })
    },
    groupedItems() {
      return this.incidentsByMonth
    },
  },

  data() {
    return {}
  },
}
</script>
