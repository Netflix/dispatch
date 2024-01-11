<template>
  <v-container fluid>
    <new-edit-sheet />
    <new-template-sheet @new-document-created="addItem($event)" />
    <v-row no-gutters>
      <v-col>
        <v-alert closable icon="mdi-school" prominent text type="info">
          Types categorize cases. Dispatch allows for configuration on a per-case type basis.
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
            <template #item.oncall_service.name="{ item }">
              <v-chip v-if="item.oncall_service" size="small" color="info">
                {{ item.oncall_service.name }}
              </v-chip>
            </template>
            <template #item.incident_type.name="{ item }">
              <v-chip v-if="item.incident_type" size="small" color="info">
                {{ item.incident_type.name }}
              </v-chip>
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
  </v-container>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

import SettingsBreadcrumbs from "@/components/SettingsBreadcrumbs.vue"
import NewEditSheet from "@/case/type/NewEditSheet.vue"
import NewTemplateSheet from "@/document/template/TemplateNewEditSheet.vue"

export default {
  name: "CaseTypeTable",

  components: {
    NewEditSheet,
    SettingsBreadcrumbs,
    NewTemplateSheet,
  },

  data() {
    return {
      headers: [
        { title: "Name", value: "name", sortable: true },
        { title: "Description", value: "description", sortable: false },
        { title: "Visibility", value: "visibility", sortable: false },
        { title: "Oncall Service", value: "oncall_service.name", sortable: false },
        { title: "Incident Type", value: "incident_type.name", sortable: false },
        { title: "Default", value: "default", sortable: true },
        { title: "Enabled", value: "enabled", sortable: true },
        { title: "", key: "data-table-actions", sortable: false, align: "end" },
      ],
    }
  },

  computed: {
    ...mapFields("case_type", [
      "table.options.q",
      "table.options.page",
      "table.options.itemsPerPage",
      "table.options.sortBy",
      "table.options.descending",
      "table.options.filters.project",
      "table.loading",
      "table.rows.items",
      "table.rows.total",
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
    ...mapActions("case_type", ["getAll", "createEditShow", "removeShow"]),
  },
}
</script>

<style>
.mdi-school {
  color: white !important;
}
</style>
