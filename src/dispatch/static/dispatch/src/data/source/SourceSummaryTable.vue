<template>
  <v-data-table :headers="headers" :items="items">
    <template #item.name="{ value }">
      <router-link
        :to="{
          name: 'SourceDetail',
          params: { name: value, tab: 'details' },
        }"
      >
        <b>{{ value }}</b>
      </router-link>
    </template>
    <template #item.project.name="{ item, value }">
      <v-chip size="small" :color="item.project.color">
        {{ value }}
      </v-chip>
    </template>
    <template #item.source_environment.name="{ item, value }">
      <v-chip v-if="item.source_environment" size="small" :color="item.source_environment.color">
        {{ value }}
      </v-chip>
    </template>
    <template #item.source_status="{ value }">
      <v-badge v-if="value" bordered color="warning" dot location="left" offset-x="-16">
        {{ value.name }}
      </v-badge>
    </template>
    <template #item.source_data_format="{ value }">
      <v-chip v-if="value" size="small">
        {{ value.name }}
      </v-chip>
    </template>
    <template #item.source_type="{ value }">
      <v-chip v-if="value" size="small">
        {{ value.name }}
      </v-chip>
    </template>
    <template #item.owner="{ value }">
      <service-popover v-if="value" :service="value" />
    </template>
    <template #item.data_last_loaded_at="{ value }">
      {{ formatRelativeDate(value) }}
    </template>
    <template #item.data-table-actions="{ item }">
      <v-menu location="right" origin="overlap">
        <template #activator="{ props }">
          <v-btn icon="mdi-dots-vertical" variant="text" v-bind="props" />
        </template>
        <v-list>
          <v-list-item :to="{ name: 'SourceTableEdit', params: { name: item.name } }">
            <v-list-item-title>View / Edit</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </template>
  </v-data-table>
</template>

<script>
import { mapActions } from "vuex"
import { formatRelativeDate } from "@/filters"

export default {
  name: "SourceSummaryTable",

  data() {
    return {
      headers: [
        { title: "Name", key: "name", sortable: true },
        { title: "Project", key: "project.name", sortable: false },
        { title: "Environment", key: "source_environment.name", sortable: true },
        { title: "Owner", key: "owner" },
        { title: "Status", key: "source_status", sortable: true },
        { title: "Type", key: "source_type", sortable: true },
        { title: "Last Loaded", key: "data_last_loaded_at", sortable: true },
        {
          title: "",
          key: "data-table-actions",
          sortable: false,
          align: "end",
        },
      ],
    }
  },

  setup() {
    return { formatRelativeDate }
  },

  props: {
    items: {
      default: function () {
        return []
      },
      type: Array,
    },
    loading: {
      default: function () {
        return false
      },
      type: [String, Boolean],
    },
  },

  methods: {
    ...mapActions("source", ["createEditShow", "removeShow"]),
  },
}
</script>
