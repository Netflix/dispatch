<template>
  <v-card :loading="loading" outlined elevation="0">
    <v-card-title>Top 5 Cost</v-card-title>
    <v-data-table
      :headers="headers"
      :items="sources"
      disable-pagination
      hide-default-footer
      disable-filtering
    >
      <template v-slot:item.name="{ item }">
        <router-link
          :to="{
            name: 'SourceDetail',
            params: { name: item.name, tab: 'details' },
          }"
          ><b>{{ item.name }}</b></router-link
        >
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
import { sortBy } from "lodash"
export default {
  name: "SourceTop5CostTableCard",

  props: {
    value: {
      type: Array,
      default: function () {
        return []
      },
    },
    loading: {
      type: [String, Boolean],
      default: function () {
        return false
      },
    },
  },

  components: {},

  data() {
    return {
      headers: [
        {
          text: "Name",
          align: "start",
          sortable: true,
          value: "name",
        },
        { text: "Cost", value: "cost" },
      ],
    }
  },

  computed: {
    sources() {
      return sortBy(this.value, ["cost"]).slice(0, 5)
    },
  },
}
</script>
