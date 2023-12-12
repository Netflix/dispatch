<template>
  <v-container fluid>
    <new-edit-sheet />
    <v-row no-gutters>
      <v-col>
        <v-alert closable icon="mdi-school" prominent text type="info">
          Priorities adds another dimension to Dispatch's incident categorization. They also allow
          for some configurability (e.g. only page a command for 'high' priority incidents).
        </v-alert>
      </v-col>
    </v-row>
    <v-row align="center" justify="space-between" no-gutters>
      <v-col cols="8">
        <settings-breadcrumbs v-model="project" />
      </v-col>
      <v-col class="text-right">
        <v-btn color="info" class="mr-2" @click="createEditShow()"> New </v-btn>
      </v-col>
    </v-row>
    <v-row no-gutters>
      <div class="text-body-1 ml-4 mt-3">Incident priority types</div>
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
            <template #item.page_commander="{ value }">
              <v-checkbox-btn :model-value="value" disabled />
            </template>
            <template #item.default="{ value }">
              <v-checkbox-btn :model-value="value" disabled />
            </template>
            <template #item.enabled="{ value }">
              <v-checkbox-btn :model-value="value" disabled />
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
                    <v-list-item-title>View / Edit</v-list-item-title>
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
        <div class="text-body-1 ml-4 mt-6">Incident priority settings</div>
        <v-row align="start" no-gutters>
          <div class="d-flex justify-content-start">
            <v-col cols="10" class="mt-2">
              <v-checkbox
                class="ml-10 mr-5"
                v-model="restrictStable"
                label="Restrict Stable status to this priority:"
                @update:model-value="updateStablePriority"
              />
            </v-col>
            <v-col class="mt-5">
              <v-tooltip max-width="500px" open-delay="50" location="bottom">
                <template #activator="{ props }">
                  <v-icon v-bind="props">mdi-information</v-icon>
                </template>
                <span>
                  If activated, Dispatch will automatically change Stable incidents to this
                  priority. Also, users will not be permitted to change the priority on Stable
                  incidents.
                </span>
              </v-tooltip>
            </v-col>
            <v-col cols="6">
              <incident-priority-select
                class="ml-4"
                width="400px"
                v-model="stablePriority"
                :project="project[0]"
              />
            </v-col>
          </div>
        </v-row>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

import NewEditSheet from "@/incident/priority/NewEditSheet.vue"
import SettingsBreadcrumbs from "@/components/SettingsBreadcrumbs.vue"
import IncidentPrioritySelect from "@/incident/priority/IncidentPrioritySelect.vue"

export default {
  name: "IncidentPriorityTable",

  components: {
    NewEditSheet,
    SettingsBreadcrumbs,
    IncidentPrioritySelect,
  },
  data() {
    return {
      headers: [
        { title: "Name", value: "name", sortable: true },
        { title: "Description", value: "description", sortable: false },
        { title: "Page Commander", value: "page_commander", sortable: true },
        { title: "Default", value: "default", sortable: true },
        { title: "Enabled", value: "enabled", sortable: true },
        { title: "Tactical Report Reminder", value: "tactical_report_reminder", sortable: true },
        { title: "Executive Report Reminder", value: "executive_report_reminder", sortable: true },
        { title: "View Order", value: "view_order", sortable: true },
        { title: "", key: "data-table-actions", sortable: false, align: "end" },
      ],
      restrictStable: false,
    }
  },

  computed: {
    ...mapFields("incident_priority", [
      "table.options.q",
      "table.options.page",
      "table.options.itemsPerPage",
      "table.options.sortBy",
      "table.options.descending",
      "table.options.filters.project",
      "table.loading",
      "table.rows.items",
      "table.rows.total",
      "stablePriority",
    ]),
  },

  created() {
    this.project = [{ name: this.$route.query.project }]

    this.getAll()
    this.restrictStable = this.stablePriority != null

    this.$watch(
      (vm) => [vm.q, vm.itemsPerPage, vm.sortBy, vm.descending, vm.project],
      () => {
        this.page = 1
        this.$router.push({ query: { project: this.project[0].name } })
        this.getAll()
        this.restrictStable = this.stablePriority != null
      }
    )

    this.$watch(
      (vm) => [vm.stablePriority],
      () => {
        this.restrictStable = this.stablePriority != null
        this.updateStablePriority(this.restrictStable)
      }
    )
  },

  methods: {
    ...mapActions("incident_priority", [
      "getAll",
      "createEditShow",
      "removeShow",
      "updateStablePriority",
    ]),
  },
}
</script>

<style>
.mdi-school {
  color: white !important;
}
</style>
