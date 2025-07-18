<template>
  <v-container fluid>
    <new-edit-sheet />
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
            <template #item.data-table-actions="slotProps">
              <v-menu location="right" origin="overlap">
                <template #activator="menuProps">
                  <v-btn icon variant="text" v-bind="menuProps.props">
                    <v-icon>mdi-dots-vertical</v-icon>
                  </v-btn>
                </template>
                <v-list>
                  <v-list-item @click="createEditShow(slotProps.item)">
                    <v-list-item-title>View / Edit</v-list-item-title>
                  </v-list-item>
                </v-list>
              </v-menu>
            </template>
            <template #item.discoverability="slotProps">
              <span>{{ combine(slotProps.item) }}</span>
            </template>
            <template #item.required="slotProps">
              <v-checkbox-btn :model-value="slotProps.value" disabled />
            </template>
            <template #item.exclusive="slotProps">
              <v-checkbox-btn :model-value="slotProps.value" disabled />
            </template>
            <template #item.genai_suggestions="slotProps">
              <v-checkbox-btn :model-value="slotProps.value" disabled />
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
import NewEditSheet from "@/tag_type/NewEditSheet.vue"

const attribute_to_text = {
  discoverable_case: "Cases",
  discoverable_incident: "Incidents",
  discoverable_query: "Queries",
  discoverable_signal: "Signals",
  discoverable_source: "Sources",
  discoverable_document: "Documents",
}

export default {
  name: "TagTypeTable",

  components: {
    NewEditSheet,
    SettingsBreadcrumbs,
  },
  data() {
    return {
      headers: [
        { title: "Name", value: "name", sortable: true },
        { title: "Description", value: "description", sortable: false },
        { title: "Discoverability", value: "discoverability", sortable: false },
        { title: "Required", value: "required", sortable: false },
        { title: "Exclusive", value: "exclusive", sortable: false },
        { title: "GenAI Suggestions", value: "genai_suggestions", sortable: false },
        { title: "", key: "data-table-actions", sortable: false, align: "end" },
      ],
    }
  },

  computed: {
    ...mapFields("tag_type", [
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
    ...mapActions("tag_type", ["getAll", "createEditShow", "removeShow"]),
    combine(item) {
      let result = Object.keys(attribute_to_text).reduce((acc, key) => {
        if (item[key]) {
          acc.push(attribute_to_text[key])
        }
        return acc
      }, [])
      return result.join(", ")
    },
  },
}
</script>
