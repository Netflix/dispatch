<template>
  <v-dialog v-model="showExport" persistent max-width="800px">
    <template v-slot:activator="{ on }">
      <v-btn color="secondary" class="ml-2" v-on="on"> Export </v-btn>
    </template>
    <v-card>
      <v-card-title>
        <span class="headline">Export Signal Instances</span>
      </v-card-title>
      <v-stepper v-model="e1">
        <v-stepper-header>
          <v-stepper-step :complete="e1 > 1" step="1" editable> Filter Data </v-stepper-step>
          <v-divider />
          <v-stepper-step :complete="e1 > 2" step="2" editable> Select Fields </v-stepper-step>
          <v-divider />
          <v-stepper-step step="3" editable> Preview </v-stepper-step>
        </v-stepper-header>
        <v-stepper-items>
          <v-stepper-content step="1">
            <v-list dense>
              <v-list-item>
                <v-list-item-content>
                  <date-window-input v-model="created_at" label="Created At" />
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <project-combobox v-model="project" label="Projects" />
                </v-list-item-content>
              </v-list-item>
            </v-list>
            <v-spacer />
            <v-btn @click="closeExport()" text> Cancel </v-btn>
            <v-btn color="info" @click="e1 = 2"> Continue </v-btn>
          </v-stepper-content>
          <v-stepper-content step="2">
            <v-autocomplete
              v-model="selectedFields"
              :items="allFields"
              label="Fields"
              multiple
              chips
              return-object
            />
            <v-spacer />
            <v-btn @click="closeExport()" text> Cancel </v-btn>
            <v-btn color="info" @click="e1 = 3"> Continue </v-btn>
          </v-stepper-content>
          <v-stepper-content step="3">
            <v-data-table
              hide-default-footer
              :headers="selectedFields"
              :items="items"
              :loading="previewRowsLoading"
            >
            </v-data-table>
            <v-spacer />
            <v-btn @click="closeExport()" text> Cancel </v-btn>
            <v-badge :value="total" overlap color="info" bordered :content="total">
              <v-btn color="info" @click="exportToCSV()" :loading="exportLoading"> Export </v-btn>
            </v-badge>
          </v-stepper-content>
        </v-stepper-items>
      </v-stepper>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

import SearchUtils from "@/search/utils"
import Util from "@/util"

import DateWindowInput from "@/components/DateWindowInput.vue"
import SignalApi from "@/signal/api"
import ProjectCombobox from "@/project/ProjectCombobox.vue"

export default {
  name: "SignalTableExportDialog",

  components: {
    DateWindowInput,
    ProjectCombobox,
  },

  data() {
    return {
      e1: 1,
      selectedFields: [
        { text: "Name", value: "name", sortable: false },
        { text: "Source", value: "source", sortable: false },
      ],
      allFields: [
        { text: "Name", value: "name", sortable: false },
        { text: "Source", value: "source", sortable: false },
        { text: "Created At", value: "created_at", sortable: false },
      ],
      previewRowsLoading: false,
      exportLoading: false,
    }
  },

  computed: {
    ...mapFields("signalInstance", [
      "table.options.filters.project",
      "table.options.filters.status",
      "table.options.filters.created_at",
      "table.options",
      "table.rows.items",
      "table.rows.total",
      "dialogs.showExport",
    ]),
  },

  methods: {
    ...mapActions("signalInstance", ["getAll", "closeExport"]),

    getPreviewData() {
      this.previewRowsLoading = "error"
      this.getAll({ itemsPerPage: 10 })
      this.previewRowsLoading = false
    },

    exportToCSV() {
      let params = SearchUtils.createParametersFromTableOptions({ ...this.options })

      params["itemsPerPage"] = -1
      params["include"] = this.selectedFields.map((item) => item.value)

      this.exportLoading = true

      return SignalApi.getAllInstances(params)
        .then((response) => {
          let items = response.data.items
          Util.exportCSV(items, "signal-details-export.csv")
          this.exportLoading = false
          this.closeExport()
        })
        .catch(() => {
          this.exportLoading = false
          this.closeExport()
        })
    },
  },

  created() {
    this.$watch(
      (vm) => [vm.project, vm.created_at],
      () => {
        this.getPreviewData()
      }
    )
  },
}
</script>
