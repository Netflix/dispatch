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
            <template #item.genai_type="{ value }">
              {{ getGenaiTypeNameSync(value) }}
            </template>
            <template #item.genai_prompt="{ value }">
              <div class="text-truncate" style="max-width: 300px" :title="value">
                {{ value }}
              </div>
            </template>
            <template #item.genai_system_message="{ value }">
              <div class="text-truncate" style="max-width: 300px" :title="value">
                {{ value }}
              </div>
            </template>
            <template #item.enabled="{ value }">
              <v-checkbox-btn :model-value="value" disabled />
            </template>
            <template #item.created_at="{ value }">
              {{ formatDate(value) }}
            </template>
            <template #item.updated_at="{ value }">
              {{ formatDate(value) }}
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
import DeleteDialog from "@/prompt/DeleteDialog.vue"
import NewEditSheet from "@/prompt/NewEditSheet.vue"

export default {
  name: "PromptTable",

  components: {
    DeleteDialog,
    NewEditSheet,
    SettingsBreadcrumbs,
  },
  data() {
    return {
      headers: [
        { title: "Type", value: "genai_type", sortable: true },
        { title: "Prompt", value: "genai_prompt", sortable: true },
        { title: "System Message", value: "genai_system_message", sortable: true },
        { title: "Enabled", value: "enabled", sortable: true },
        { title: "Created", value: "created_at", sortable: true },
        { title: "Updated", value: "updated_at", sortable: true },
        { title: "", key: "data-table-actions", sortable: false, align: "end" },
      ],
      genaiTypeNames: {}, // Cache for type names
    }
  },

  computed: {
    ...mapFields("prompt", [
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

  async created() {
    if (this.$route.query.project) {
      this.project = [{ name: this.$route.query.project }]
    }

    await this.loadGenaiTypeNames()
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
    ...mapActions("prompt", ["getAll", "createEditShow", "removeShow"]),
    async loadGenaiTypeNames() {
      try {
        // Get all types dynamically from the store
        const types = await this.$store.dispatch("prompt/getGenaiTypes")
        // Cache the names for each type
        for (const type of types) {
          this.genaiTypeNames[type.id] = type.name
        }
      } catch (error) {
        console.error("Error loading GenAI type names:", error)
      }
    },
    getGenaiTypeNameSync(typeId) {
      return this.genaiTypeNames[typeId] || `Type ${typeId}`
    },
    formatDate(dateString) {
      if (!dateString) return ""
      return new Date(dateString).toLocaleDateString()
    },
  },
}
</script>
