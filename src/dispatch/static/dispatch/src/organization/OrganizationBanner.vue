<template>
  <v-banner
    v-if="currentOrganization.banner_enabled"
    class="mb-6"
    :color="currentOrganization.banner_color"
    single-line
  >
    <v-icon slot="icon" color="white" size="36"> mdi-information-outline </v-icon>
    {{ currentOrganization.banner_text }}
  </v-banner>
</template>
<script>
import { mapFields } from "vuex-map-fields"

import SearchUtils from "@/search/utils"
import OrganizationApi from "@/organization/api"

export default {
  data() {
    return {
      currentOrganization: {},
    }
  },

  created() {
    let filterOptions = {
      itemsPerPage: 50,
      sortBy: ["name"],
      descending: [false],
    }

    let nameFilter = [
      {
        model: "Organization",
        field: "name",
        op: "==",
        value: this.$route.params.organization,
      },
    ]

    filterOptions = SearchUtils.createParametersFromTableOptions({ ...filterOptions }, nameFilter)

    OrganizationApi.getAll(filterOptions).then((response) => {
      this.currentOrganization = response.data.items[0]
    })
  },
}
</script>
