<template>
  <v-container>
    <new-edit-modal />
    <v-row align="center" justify="space-between" no-gutters>
      <delete-dialog />
      <v-col>
        <div class="headline">Sources</div>
      </v-col>
      <v-col cols="1">
        <v-btn color="info" class="mr-2" @click="createEditShow()"> New </v-btn>
      </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col>
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
            <template v-slot:item.name="{ item }">
              <router-link
                :to="{
                  name: 'SourceDetail',
                  params: { name: item.name, tab: 'details' },
                }"
                ><b>{{ item.name }}</b></router-link
              >
            </template>
            <template v-slot:item.samplingRate="{ item }">
              <v-chip :color="getSamplingRateColor(item.sampling_rate)" dark>
                {{ item.sampling_rate }}
              </v-chip>
            </template>
            <template v-slot:item.lastRefreshed="{ item }">
              {{ item.last_refreshed | formatRelativeDate }}
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
                    <v-list-item-title>Edit</v-list-item-title>
                  </v-list-item>
                  <v-list-item @click="removeShow(item)">
                    <v-list-item-title>Delete</v-list-item-title>
                  </v-list-item>
                </v-list>
              </v-menu>
            </template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

import DeleteDialog from "@/data/source/DeleteDialog.vue"
import NewEditModal from "@/data/source/NewEditModal.vue"

export default {
  name: "SourceTable",

  components: {
    DeleteDialog,
    NewEditModal,
  },
  data() {
    return {
      headers: [
        { text: "Name", value: "name", sortable: true },
        { text: "Environment", value: "environment", sortable: true },
        { text: "Status", value: "status", sortable: true },
        { text: "Sampling Rate", value: "sampling_rate", sortable: true },
        { text: "Transport", value: "transport", sortable: true },
        { text: "Format", value: "data_format", sortable: true },
        { text: "Type", value: "source_type", sortable: true },
        { text: "Last Refreshed", value: "last_refreshed", sortable: true },
        {
          text: "",
          value: "data-table-actions",
          sortable: false,
          align: "end",
        },
      ],
    }
  },

  computed: {
    ...mapFields("source", [
      "table.options.q",
      "table.options.page",
      "table.options.itemsPerPage",
      "table.options.sortBy",
      "table.options.descending",
      "table.loading",
      "table.rows.items",
      "table.rows.total",
    ]),
  },

  created() {
    this.getAll()

    this.$watch(
      (vm) => [vm.page],
      () => {
        this.getAll()
      }
    )

    this.$watch(
      (vm) => [vm.q, vm.itemsPerPage, vm.sortBy, vm.descending],
      () => {
        this.page = 1
        this.getAll()
      }
    )
  },

  methods: {
    ...mapActions("source", ["getAll", "createEditShow", "removeShow"]),
    getSamplingRateColor(rate) {
      if (rate > 40) return "red"
      else if (rate < 80) return "orange"
      else return "green"
    },
  },
}
</script>
