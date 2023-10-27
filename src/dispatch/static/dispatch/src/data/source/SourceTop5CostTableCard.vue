<template>
  <v-card :loading="loading">
    <v-card-title>Top 5 Cost</v-card-title>
    <v-data-table
      :headers="headers"
      :items="sources"
      disable-pagination
      hide-default-footer
      disable-filtering
    >
      <template #item.name="{ item }">
        <router-link
          :to="{
            name: 'SourceDetail',
            params: { name: item.name, tab: 'details' },
          }"
        >
          <b>{{ item.name }}</b>
        </router-link>
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
import { sortBy } from "lodash"
export default {
  name: "SourceTop5CostTableCard",

  props: {
    modelValue: {
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

  data() {
    return {
      headers: [
        {
          title: "Name",
          align: "start",
          sortable: true,
          key: "name",
        },
        { title: "Cost", key: "cost" },
      ],
    }
  },

  computed: {
    sources() {
      return sortBy(this.modelValue, ["cost"]).slice(0, 5)
    },
  },
}
</script>
