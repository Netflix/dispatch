<template>
  <v-data-table :headers="headers" :items="items">
    <template #item.name="{ item }">
      <router-link
        :to="{
          name: 'SourceDetail',
          params: { name: item.raw.name, tab: 'details' },
        }"
      >
        <b>{{ item.name }}</b>
      </router-link>
    </template>
    <template #item.project.name="{ item }">
      <v-chip size="small" :color="item.raw.project.color">
        {{ item.raw.project.name }}
      </v-chip>
    </template>
    <template #item.source_environment.name="{ item }">
      <v-chip
        v-if="item.raw.source_environment"
        size="small"
        :color="item.raw.source_environment.color"
      >
        {{ item.source_environment.name }}
      </v-chip>
    </template>
    <template #item.source_status="{ item }">
      <v-badge
        v-if="item.raw.source_status"
        bordered
        color="warning"
        dot
        location="left"
        offset-x="-16"
      >
        {{ item.raw.source_status.name }}
      </v-badge>
    </template>
    <template #item.source_data_format="{ item }">
      <v-chip v-if="item.raw.source_data_format" size="small">
        {{ item.raw.source_data_format.name }}
      </v-chip>
    </template>
    <template #item.source_type="{ item }">
      <v-chip v-if="item.raw.source_type" size="small">
        {{ item.raw.source_type.name }}
      </v-chip>
    </template>
    <template #item.owner="{ item }">
      <service-popover v-if="item.raw.owner" :service="item.raw.owner" />
    </template>
    <template #item.data_last_loaded_at="{ item }">
      {{ formatRelativeDate(item.raw.data_last_loaded_at) }}
    </template>
    <template #item.data-table-actions="{ item }">
      <v-menu location="right" origin="overlap">
        <template #activator="{ props }">
          <v-btn icon="mdi-dots-vertical" variant="text" v-bind="props" />
        </template>
        <v-list>
          <v-list-item :to="{ name: 'SourceTableEdit', params: { name: item.raw.name } }">
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
