<template>
  <v-app>
    <v-content>
      <v-card flat>
        <v-toolbar color="gray8" extended flat height="150" />
        <v-card class="mx-auto" max-width="1000" style="margin-top: -64px;">
          <v-card-text>
            <div>D I S P A T C H</div>
            <incident-summary-table :items="items" :loading="loading" />
          </v-card-text>
        </v-card>
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
