<template>
  <div>
    <v-data-table :headers="headers" :items="items">
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
      <template #item.project.name="{ item }">
        <v-chip small :color="item.project.color" text-color="white">
          {{ item.project.name }}
        </v-chip>
      </template>
      <template #item.source_environment.name="{ item }">
        <v-chip
          v-if="item.source_environment"
          small
          :color="item.source_environment.color"
          text-color="white"
        >
          {{ item.source_environment.name }}
        </v-chip>
      </template>
      <template #item.source_status="{ item }">
        <v-badge
          v-if="item.source_status"
          bordered
          color="warning"
          slot="activator"
          dot
          location="left"
          offset-x="-10"
          offset-y="12"
        >
          {{ item.source_status.name }}
        </v-badge>
      </template>
      <template #item.source_data_format="{ item }">
        <v-chip v-if="item.source_data_format" small dark>
          {{ item.source_data_format.name }}
        </v-chip>
      </template>
      <template #item.source_type="{ item }">
        <v-chip v-if="item.source_type" small dark>
          {{ item.source_type.name }}
        </v-chip>
      </template>
      <template #item.owner="{ item }">
        <service-popover v-if="item.owner" :service="item.owner" />
      </template>
      <template #item.data_last_loaded_at="{ item }">
        {{ item.data_last_loaded_at | formatRelativeDate }}
      </template>
      <template #item.data-table-actions="{ item }">
        <v-menu location="bottom left">
          <template #activator="{ on }">
            <v-btn icon variant="text" v-on="on">
              <v-icon>mdi-dots-vertical</v-icon>
            </v-btn>
          </template>
          <v-list>
            <v-list-item :to="{ name: 'SourceTableEdit', params: { name: item.name } }">
              <v-list-item-title>View / Edit</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>
      </template>
    </v-data-table>
  </div>
</template>

<script>
import { mapActions } from "vuex"
export default {
  name: "SourceSummaryTable",

  components: {},
  data() {
    return {
      headers: [
        { text: "Name", value: "name", sortable: true },
        { text: "Project", value: "project.name", sortable: false },
        { text: "Environment", value: "source_environment.name", sortable: true },
        { text: "Owner", value: "owner" },
        { text: "Status", value: "source_status", sortable: true },
        { text: "Type", value: "source_type", sortable: true },
        { text: "Last Loaded", value: "data_last_loaded_at", sortable: true },
        {
          text: "",
          value: "data-table-actions",
          sortable: false,
          align: "end",
        },
      ],
    }
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
