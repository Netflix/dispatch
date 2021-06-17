<template>
  <v-app>
    <v-main>
      <organization-banner />
      <v-app-bar app flat class="v-bar--underline" color="background0">
        <router-link :to="{ name: 'IncidentOverview' }" style="text-decoration: none">
          <span class="button font-weight-bold">D I S P A T C H</span>
        </router-link>
        <v-spacer />
        <v-btn small color="primary" :to="{ name: 'report' }"> Report Incident </v-btn>
      </v-app-bar>
      <v-card class="mx-auto ma-4" max-width="1000" flat outlined>
        <v-card-text>
          <incident-summary-table :items="items" :loading="loading" />
        </v-card-text>
      </v-card>
    </v-main>
  </v-app>
</template>

<script>
import IncidentApi from "@/incident/api"
import IncidentSummaryTable from "@/incident/IncidentSummaryTable.vue"
import OrganizationBanner from "@/organization/OrganizationBanner.vue"

export default {
  name: "IncidentStatus",

  components: {
    IncidentSummaryTable,
    OrganizationBanner,
  },

  data() {
    return {
      items: [],
      loading: false,
    }
  },

  created() {
    this.getActive()
  },

  methods: {
    getActive() {
      this.loading = "error"
      IncidentApi.getAll({
        filter: JSON.stringify({
          and: [
            {
              model: "Incident",
              field: "status",
              op: "==",
              value: "Active",
            },
          ],
        }),
      }).then((response) => {
        this.items = response.data.items
        this.loading = false
      })
    },
  },
}
</script>
