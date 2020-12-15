<template>
  <v-app>
    <v-content>
      <v-app-bar app flat class="v-bar--underline" color="background0">
        <router-link to="/" tag="span">
          <span class="button font-weight-bold">D I S P A T C H</span>
        </router-link>
        <v-spacer />
        <v-btn small color="primary" to="/incidents/report">
          Report Incident
        </v-btn>
      </v-app-bar>
      <v-card class="mx-auto ma-4" max-width="800" flat outlined>
        <v-card-text>
          <incident-summary-table :items="items" :loading="loading" />
        </v-card-text>
      </v-card>
    </v-content>
  </v-app>
</template>

<script>
import { mapActions } from "vuex"
import IncidentApi from "@/incident/api"
import IncidentSummaryTable from "@/incident/IncidentSummaryTable.vue"

export default {
  name: "IncidentStatus",

  components: {
    IncidentSummaryTable
  },

  data() {
    return {
      items: [],
      loading: false
    }
  },

  mounted() {
    this.getActive()
  },

  methods: {
    getActive() {
      this.loading = "error"
      IncidentApi.getAll({ fields: ["status"], ops: ["=="], values: ["Active"] }).then(response => {
        this.items = response.data.items
        this.loading = false
      })
    },
    ...mapActions("incident", ["joinIncident"])
  }
}
</script>
