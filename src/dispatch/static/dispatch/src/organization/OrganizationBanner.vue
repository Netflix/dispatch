<template>
  <v-system-bar
    v-if="currentOrganization.banner_enabled"
    :color="currentOrganization.banner_color"
    height="64px"
    app
  >
    <v-icon color="white" size="36"> mdi-information-outline </v-icon>
    <span class="white--text">{{ currentOrganization.banner_text }}</span>
  </v-system-bar>
</template>
<script>
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
