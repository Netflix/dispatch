<template>
  <v-layout wrap>
    <template-new-edit-sheet />
    <delete-dialog />
    <v-container>
      <v-row align="center" justify="space-between">
        <v-col class="grow">
          <settings-breadcrumbs v-model="project" />
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <v-card
            outlined
            elevation="0"
            @click.stop="createEditShow({ resource_type: resourceTypes.incident })"
          >
            <div class="d-flex flex-no-wrap justify-space-between">
              <div>
                <v-card-title class="text-h5">Incident</v-card-title>
                <v-card-subtitle>Create a new incident template</v-card-subtitle>
              </div>
              <v-avatar class="ma-3" tile>
                <v-icon x-large>mdi-file-document-edit-outline</v-icon>
              </v-avatar>
            </div>
          </v-card>
        </v-col>
        <v-col>
          <v-card
            outlined
            elevation="0"
            @click.stop="createEditShow({ resource_type: resourceTypes.tracking })"
          >
            <div class="d-flex flex-no-wrap justify-space-between">
              <div>
                <v-card-title class="text-h5">Tracking</v-card-title>
                <v-card-subtitle>Create a new tracking template</v-card-subtitle>
              </div>
              <v-avatar class="ma-3" tile>
                <v-icon x-large>mdi-file-document-multiple-outline</v-icon>
              </v-avatar>
            </div>
          </v-card>
        </v-col>
        <v-col>
          <v-card
            outlined
            elevation="0"
            @click.stop="createEditShow({ resourceType: resourceTypes.executive })"
          >
            <div class="d-flex flex-no-wrap justify-space-between">
              <div>
                <v-card-title class="text-h5">Executive</v-card-title>
                <v-card-subtitle>Create a new executive report template</v-card-subtitle>
              </div>
              <v-avatar class="ma-3" tile>
                <v-icon x-large>mdi-text-box-check-outline</v-icon>
              </v-avatar>
            </div>
          </v-card>
        </v-col>
        <v-col>
          <v-card
            outlined
            elevation="0"
            @click.stop="createEditShow({ resource_type: resourceTypes.review })"
          >
            <div class="d-flex flex-no-wrap justify-space-between">
              <div>
                <v-card-title class="text-h5">Review</v-card-title>
                <v-card-subtitle>Create a new incident review template</v-card-subtitle>
              </div>
              <v-avatar class="ma-3" tile>
                <v-icon x-large>mdi-text-box-search-outline</v-icon>
              </v-avatar>
            </div>
          </v-card>
        </v-col>
      </v-row>
      <v-card elevation="0">
        <v-card-title>
          <v-text-field
            v-model="q"
            append-icon="search"
            label="Search"
            single-line
            hide-details
            clearable
          />
        </v-card-title>
        <v-data-table
          :headers="headers"
          :items="items"
          :server-items-length="total"
          :page.sync="page"
          :items-per-page.sync="itemsPerPage"
          :sort-by.sync="sortBy"
          :sort-desc.sync="descending"
          :loading="loading"
          loading-text="Loading... Please wait"
        >
          <template v-slot:item.evergreen="{ item }">
            <v-simple-checkbox v-model="item.evergreen" disabled />
          </template>
          <template v-slot:item.resource_type="{ item }">
            <span v-if="item.resource_type === resourceTypes.tracking"> Tracking </span>
            <span v-else-if="item.resource_type === resourceTypes.incident"> Incident </span>
            <span v-else-if="item.resource_type === resourceTypes.executive"> Executive </span>
            <span v-else-if="item.resource_type === resourceTypes.review"> Review </span>
            <span v-else-if="item.resource_type === resourceTypes.report"> Report </span>
          </template>
          <template v-slot:item.description="{ item }">
            {{ item.description }}
          </template>
          <template v-slot:item.name="{ item }">
            <a :href="item.weblink" target="_blank" style="text-decoration: none">
              {{ item.name }}
              <v-icon small>open_in_new</v-icon>
            </a>
          </template>
          <template v-slot:item.data-table-actions="{ item }">
            <v-menu bottom left>
              <template v-slot:activator="{ on }">
                <v-btn icon v-on="on">
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
        </v-data-table>
      </v-card>
    </v-container>
  </v-layout>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

import { debounce } from "lodash"

import DocumentApi from "@/document/api"

import SettingsBreadcrumbs from "@/components/SettingsBreadcrumbs.vue"
import TemplateNewEditSheet from "@/document/template/TemplateNewEditSheet.vue"
import DeleteDialog from "@/document/template/DeleteDialog.vue"

export default {
  name: "TemplateConfiguration",

  components: {
    SettingsBreadcrumbs,
    TemplateNewEditSheet,
    DeleteDialog,
  },
  data() {
    return {
      resourceTypes: {
        incident: "dispatch-incident-document-template",
        executive: "dispatch-executive-report-document-template",
        review: "dispatch-incident-review-document-template",
        tracking: "dispatch-incident-tracking-template",
      },
      headers: [
        { text: "Name", value: "name", sortable: true },
        { text: "Description", value: "description", sortable: false },
        { text: "Type", value: "resource_type", sortable: true },
        { text: "Evergreen", value: "evergreen", sortable: true, width: "10%", align: "center" },
        { text: "", value: "data-table-actions", sortable: false, align: "end" },
      ],
    }
  },
  computed: {
    ...mapFields("template", [
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
    ...mapFields("route", ["query"]),
  },
  created() {
    this.project = [{ name: this.query.project }]

    this.fetchData()

    this.$watch(
      (vm) => [vm.page],
      () => {
        this.fetchData()
      }
    )

    this.$watch(
      (vm) => [vm.q, vm.itemsPerPage, vm.sortBy, vm.descending, vm.project],
      () => {
        this.page = 1
        this.$router.push({ query: { project: this.project[0].name } })
        this.fetchData()
      }
    )
  },

  methods: {
    ...mapActions("template", ["createEditShow", "removeShow"]),
    fetchData() {
      this.error = null
      this.loading = "error"

      let filterOptions = {
        q: this.search,
        sortBy: ["resource_type"],
        itemsPerPage: this.itemsPerPage,
        filter: JSON.stringify({
          or: [
            {
              model: "Document",
              field: "resource_type",
              op: "==",
              value: this.resourceTypes.incident,
            },
            {
              model: "Document",
              field: "resource_type",
              op: "==",
              value: this.resourceTypes.executive,
            },
            {
              model: "Document",
              field: "resource_type",
              op: "==",
              value: this.resourceTypes.review,
            },
            {
              model: "Document",
              field: "resource_type",
              op: "==",
              value: this.resourceTypes.tracking,
            },
          ],
          and: [
            {
              model: "Project",
              field: "name",
              op: "==",
              value: this.project.name,
            },
          ],
        }),
      }

      DocumentApi.getAll(filterOptions).then((response) => {
        this.items = response.data.items
        this.total = response.data.total

        if (this.items.length < this.total) {
          this.more = true
        } else {
          this.more = false
        }

        this.loading = false
      })
    },
    getFilteredData: debounce(function (options) {
      this.fetchData(options)
    }, 500),
  },
}
</script>
