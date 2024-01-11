<template>
  <v-container>
    <reference-new-edit-sheet />
    <delete-dialog />
    <v-row align="center" justify="space-between" no-gutters>
      <v-col cols="8">
        <settings-breadcrumbs v-model="project" />
      </v-col>
    </v-row>
    <v-row>
      <v-col v-for="document in referenceDocumentTypes" :key="document.resource_type">
        <v-card @click.stop="createEditShow({ resource_type: document.resource_type })">
          <div class="d-flex flex-no-wrap justify-space-between">
            <div>
              <v-card-title class="text-h5">{{ document.title }}</v-card-title>
              <v-card-subtitle>{{ document.description }}</v-card-subtitle>
            </div>
            <v-avatar class="ma-3" tile>
              <v-icon size="x-large">{{ document.icon }}</v-icon>
            </v-avatar>
          </div>
        </v-card>
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
            <template #item.evergreen="{ value }">
              <v-checkbox-btn :model-value="value" disabled />
            </template>
            <template #item.resource_type="{ value }">
              {{ getResourceTitle(value) }}
            </template>
            <template #item.name="{ item }">
              <a :href="item.weblink" target="_blank" style="text-decoration: none">
                {{ item.name }}
                <v-icon size="small">mdi-open-in-new</v-icon>
              </a>
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
  </v-container>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

import SettingsBreadcrumbs from "@/components/SettingsBreadcrumbs.vue"
import ReferenceNewEditSheet from "@/document/reference/ReferenceNewEditSheet.vue"
import DeleteDialog from "@/document/reference/DeleteDialog.vue"
import { referenceDocumentTypes } from "@/document/reference/store.js"

export default {
  name: "ReferenceConfiguration",

  components: {
    SettingsBreadcrumbs,
    ReferenceNewEditSheet,
    DeleteDialog,
  },
  data() {
    return {
      referenceDocumentTypes: referenceDocumentTypes,
      headers: [
        { title: "Name", key: "name", sortable: true },
        { title: "Description", key: "description", sortable: false },
        { title: "Type", key: "resource_type", sortable: true },
        { title: "Evergreen", key: "evergreen", sortable: true, width: "10%", align: "center" },
        { title: "", key: "data-table-actions", sortable: false, align: "end" },
      ],
    }
  },
  computed: {
    ...mapFields("reference", [
      "table.options.q",
      "table.options.page",
      "table.options.itemsPerPage",
      "table.options.sortBy",
      "table.options.descending",
      "table.options.filters.project",
      "table.loading",
      "table.rows.items",
      "table.rows.total",
      "resourceTypes",
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
    getResourceTitle(resource_type) {
      const found = referenceDocumentTypes.find((item) => {
        return item.resource_type === resource_type
      })
      return found ? found.title : ""
    },
    ...mapActions("reference", ["getAll", "createEditShow", "removeShow"]),
  },
}
</script>
