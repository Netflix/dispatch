<template>
  <v-app>
    <v-main>
      <organization-banner />
      <v-app-bar flat style="border-bottom: 1px solid #d2d2d2 !important" color="background0">
        <template #prepend>
          <router-link :to="{ name: 'CaseOverview' }" style="text-decoration: none">
            <span class="button font-weight-bold">D I S P A T C H</span>
          </router-link>
        </template>
        <template #append>
          <v-btn size="small" color="primary" :to="{ name: 'caseReport' }"> Report Issue </v-btn>
        </template>
      </v-app-bar>
      <v-container fluid>
        <v-row>
          <v-col>
            <v-card class="mx-auto ma-4">
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
import SearchUtils from "@/search/utils"
import RouterUtils from "@/router/utils"

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
      filters: { status: ["New"] },
    }
  },

  created() {
    this.filters = {
      ...this.filters,
      ...RouterUtils.deserializeFilters(this.$route.query),
    }
    this.getActive()
  },

  methods: {
    getActive() {
      this.error = null
      this.loading = "error"
      let filterOptions = {
        sortBy: ["reported_at"],
        descending: [true],
        itemsPerPage: -1,
        filters: { ...this.filters },
      }
      filterOptions = SearchUtils.createParametersFromTableOptions({ ...filterOptions })

      CaseApi.getAll(filterOptions).then((response) => {
        this.items = response.data.items
        this.loading = false
      })
    },
  },
}
</script>
