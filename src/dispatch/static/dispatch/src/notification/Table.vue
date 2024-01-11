<template>
  <v-container fluid>
    <new-edit-sheet />
    <delete-dialog />
    <v-row align="center" justify="space-between" no-gutters>
      <v-col cols="8">
        <settings-breadcrumbs v-model="project" />
      </v-col>
      <v-col class="text-right">
        <v-btn color="info" class="mr-2" @click="createEditShow()"> New </v-btn>
      </v-col>
    </v-row>
    <v-row no-gutters>
      <div class="text-body-1 ml-4 mt-3">Notification channels</div>
    </v-row>
    <v-row no-gutters>
      <v-col>
        <v-card variant="flat">
          <v-card-title>
            <v-text-field
              v-model="q"
              append-inner-icon="mdi-magnify"
              label="Search"
              single-line
              hide-details
              clearable
            />
          </v-card-title>
          <v-data-table-server
            :headers="headers"
            :items="items"
            :items-length="total || 0"
            v-model:page="page"
            v-model:items-per-page="itemsPerPage"
            v-model:sort-by="sortBy"
            v-model:sort-desc="descending"
            :loading="loading"
            loading-text="Loading... Please wait"
          >
            <template #item.filters="{ item }">
              <search-filter v-for="filter in item.filters" :key="filter.id" :filter="filter" />
            </template>
            <template #item.enabled="{ value }">
              <v-checkbox-btn :model-value="value" disabled />
            </template>
            <template #item.created_at="{ value }">
              <v-tooltip location="bottom">
                <template #activator="{ props }">
                  <span v-bind="props">{{ formatRelativeDate(value) }}</span>
                </template>
                <span>{{ formatDate(value) }}</span>
              </v-tooltip>
            </template>
            <template #item.data-table-actions="{ item }">
              <v-menu location="right" origin="overlap">
                <template #activator="{ props }">
                  <v-btn icon variant="text" v-bind="props">
                    <v-icon>mdi-dots-vertical</v-icon>
                  </v-btn>
                </template>
                <v-list>
                  <v-list-item @click="createEditShow(item)">
                    <v-list-item-title>Edit</v-list-item-title>
                  </v-list-item>
                  <v-list-item @click="removeShow(item)">
                    <v-list-item-title>Delete</v-list-item-title>
                  </v-list-item>
                </v-list>
              </v-menu>
            </template>
          </v-data-table-server>
        </v-card>
      </v-col>
    </v-row>
    <v-divider />
    <v-row no-gutters>
      <v-col>
        <div class="text-body-1 ml-4 mt-6">Notification settings</div>
        <v-row align="start" no-gutters>
          <v-col class="d-flex justify-start">
            <v-checkbox
              class="ml-10 mr-5"
              v-model="dailyReports"
              label="Send Daily Incident Report"
              @update:model-value="updateDailyReports"
              :disabled="dailyReports == null"
            />
            <v-tooltip max-width="500px" open-delay="50" location="bottom">
              <template #activator="{ props }">
                <v-icon v-bind="props"> mdi-information </v-icon>
              </template>
              <span>
                If activated, Dispatch will send a daily report of incidents that are currently
                active and incidents that have been marked as stable or closed in the last 24 hours.
              </span>
            </v-tooltip>
          </v-col>
        </v-row>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import { formatRelativeDate, formatDate } from "@/filters"

import SettingsBreadcrumbs from "@/components/SettingsBreadcrumbs.vue"
import DeleteDialog from "@/notification/DeleteDialog.vue"
import NewEditSheet from "@/notification/NewEditSheet.vue"
import SearchFilter from "@/search/SearchFilter.vue"

export default {
  name: "NotificationTable",

  components: {
    DeleteDialog,
    NewEditSheet,
    SearchFilter,
    SettingsBreadcrumbs,
  },
  data() {
    return {
      headers: [
        { title: "Name", value: "name", sortable: false },
        { title: "Description", value: "description", sortable: false },
        { title: "Type", value: "type", sortable: false },
        { title: "Target", value: "target", sortable: false },
        { title: "Filters", value: "filters", sortable: false },
        { title: "Enabled", value: "enabled", sortable: false },
        { title: "Created At", value: "created_at", sortable: true },
        { title: "", key: "data-table-actions", sortable: false, align: "end" },
      ],
    }
  },

  setup() {
    return { formatRelativeDate, formatDate }
  },

  computed: {
    ...mapFields("notification", [
      "table.options.q",
      "table.options.page",
      "table.options.itemsPerPage",
      "table.options.sortBy",
      "table.options.descending",
      "table.options.filters.project",
      "table.loading",
      "table.rows.items",
      "table.rows.total",
      "dailyReports",
    ]),
  },

  created() {
    this.project = [{ name: this.$route.query.project }]

    this.getAll()

    this.$watch(
      (vm) => [vm.page],
      () => {
        this.getAll()
      }
    )

    this.$watch(
      (vm) => [vm.q, vm.itemsPerPage, vm.sortBy, vm.descending, vm.project],
      () => {
        this.page = 1
        this.$router.push({ query: { project: this.project[0].name } })
        this.getAll()
      }
    )
  },

  methods: {
    ...mapActions("notification", ["getAll", "createEditShow", "removeShow", "updateDailyReports"]),
  },
}
</script>
