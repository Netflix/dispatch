<template>
  <v-app>
    <v-main>
      <organization-banner />
      <v-app-bar app flat class="v-bar--underline" color="background0">
        <router-link :to="{ name: 'CaseOverview' }" style="text-decoration: none">
          <span class="button font-weight-bold">D I S P A T C H</span>
        </router-link>
        <v-spacer />
        <v-btn small color="primary" :to="{ name: 'caseReport' }"> Report Issue </v-btn>
      </v-app-bar>
      <v-container fluid>
        <v-row>
          <v-col>
            <v-card class="mx-auto ma-4" flat outlined>
              <v-card-text>
                <case-summary-table :items="items" :loading="loading" />
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
import CaseApi from "@/case/api"
import CaseSummaryTable from "@/case/CaseSummaryTable.vue"
import OrganizationBanner from "@/organization/OrganizationBanner.vue"

export default {
  name: "CaseStatus",

  components: {
    CaseSummaryTable,
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
      CaseApi.getAll({
        filter: JSON.stringify({
          and: [
            {
              model: "Case",
              field: "status",
              op: "==",
              value: "New",
            },
          ],
        }),
        sortBy: ["reported_at"],
        descending: [true],
        itemsPerPage: -1,
      }).then((response) => {
        this.items = response.data.items
        this.loading = false
      })
    },
  },
}
</script>
