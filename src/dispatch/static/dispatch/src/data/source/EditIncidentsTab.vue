<template>
  <v-container grid-list-md>
    <incident-select v-model="selectedIncident" />
    <incident-summary-table :items="incidents" />
  </v-container>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import IncidentSelect from "@/incident/IncidentSelect.vue"
import IncidentSummaryTable from "@/incident/IncidentSummaryTable.vue"

export default {
  name: "SourceEditIncidentsTab",

  components: {
    IncidentSummaryTable,
    IncidentSelect,
  },

  computed: {
    ...mapFields("source", ["selected.source.incidents", "selected.loading"]),
  },

  data() {
    return {
      selectedIncident: null,
    }
  },
}
</script>
