<template>
  <v-container>
    <template-new-edit-sheet />
    <delete-dialog />
    <v-row align="center" justify="space-between" no-gutters>
      <v-col cols="8">
        <settings-breadcrumbs v-model="project" />
      </v-col>
    </v-row>
    <v-row no-gutters class="justify-space-between">
      <v-col v-for="document in templateDocumentTypes" :key="document.resource_type">
        <v-card
          @click.stop="createEditShow({ resource_type: document.resource_type })"
          variant="outlined"
          elevation="0"
          style="border: 1px solid rgb(var(--v-borderline))"
        >
          <div>
            <div>
              <v-card-title class="text-h5">
                {{ document.title }}
                <v-avatar class="ma-3" tile>
                  <v-icon>{{ document.icon }}</v-icon>
                </v-avatar>
              </v-card-title>
              <v-card-subtitle class="wrap-text mb-2">{{ document.description }}</v-card-subtitle>
            </div>
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

import DeleteDialog from "@/document/template/DeleteDialog.vue"
import SettingsBreadcrumbs from "@/components/SettingsBreadcrumbs.vue"
import TemplateNewEditSheet from "@/document/template/TemplateNewEditSheet.vue"
import { templateDocumentTypes } from "@/document/template/store.js"

export default {
  name: "TemplateConfiguration",

  components: {
    DeleteDialog,
    SettingsBreadcrumbs,
    TemplateNewEditSheet,
  },

  data() {
    return {
      templateDocumentTypes: templateDocumentTypes,
      headers: [
        { title: "Name", value: "name", sortable: true },
        { title: "Description", value: "description", sortable: false },
        { title: "Type", value: "resource_type", sortable: true },
        { title: "Evergreen", value: "evergreen", sortable: true, width: "10%", align: "center" },
        { title: "", key: "data-table-actions", sortable: false, align: "end" },
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
      const found = templateDocumentTypes.find((item) => {
        return item.resource_type === resource_type
      })
      return found ? found.title : ""
    },
    ...mapActions("template", ["getAll", "createEditShow", "removeShow"]),
  },
}
</script>

<style scoped lang="css">
.wrap-text {
  white-space: normal;
}
</style>
