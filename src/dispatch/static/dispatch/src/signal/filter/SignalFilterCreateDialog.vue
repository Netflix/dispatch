<template>
  <v-dialog v-model="showCreateEdit" persistent max-width="800px">
    <template #activator="{ props }">
      <v-btn icon variant="text" v-bind="props">
        <v-icon>mdi-plus</v-icon>
      </v-btn>
    </template>
    <v-card>
      <v-card-title>
        <span class="text-h5">Create Signal Filter</span>
        <v-spacer />
      </v-card-title>
      <v-stepper v-model="step">
        <v-stepper-header>
          <v-stepper-item :complete="step > 1" :value="1" editable> Filter </v-stepper-item>
          <v-divider />

          <v-stepper-item :complete="step > 2" :value="2" editable> Preview </v-stepper-item>
          <v-divider />

          <v-stepper-item :value="3" editable> Save </v-stepper-item>
        </v-stepper-header>

        <v-stepper-window>
          <v-stepper-window-item :value="1">
            <v-card>
              <v-card-text>
                Define the entity and entity types that will be used to match with existing signal
                instances.
                <v-tabs v-model="activeTab" color="primary" align-tabs="end">
                  <v-tab>Basic</v-tab>
                  <v-tab>Advanced</v-tab>
                </v-tabs>
                <v-window v-model="activeTab">
                  <v-window-item>
                    <v-radio-group
                      label="Action"
                      v-model="action"
                      inline
                      class="justify-right"
                      name="Action"
                      :rules="[rules.required]"
                    >
                      <v-radio label="Snooze" value="snooze" />
                      <v-radio label="Deduplicate" value="deduplicate" />
                    </v-radio-group>
                    <span v-if="action === 'deduplicate'">
                      <entity-type-filter-combobox
                        :project="project"
                        :signalDefinition="signalDefinition"
                        v-model="filters.entity_type"
                        label="Entity Types"
                      />
                      <v-select
                        persistent-hint
                        label="Window (minutes)"
                        :items="windows"
                        v-model="window"
                      />
                    </span>
                    <span v-if="action == 'snooze'">
                      <entity-filter-combobox
                        :project="project"
                        v-model="filters.entity"
                        label="Entities"
                      />
                      <expiration-input persistent-hint v-model="expiration" />
                    </span>
                  </v-window-item>
                  <v-window-item>
                    <div style="height: 400px">
                      <MonacoEditor
                        v-model="expression_str"
                        :options="editorOptions"
                        language="json"
                      />
                    </div>
                  </v-window-item>
                </v-window>
              </v-card-text>
              <v-card-actions>
                <v-spacer />
                <v-btn @click="closeCreateEditDialog()" variant="text"> Cancel </v-btn>
                <v-btn color="info" @click="step = 2"> Continue </v-btn>
              </v-card-actions>
            </v-card>
          </v-stepper-window-item>

          <v-stepper-window-item :value="2">
            <v-card>
              <v-card-text>
                Examples matching your filter:
                <v-data-table
                  hide-default-footer
                  :headers="previewFields"
                  :items="previewRows.items"
                  :loading="previewRowsLoading"
                >
                  <template #item.data-table-actions="{ item }">
                    <raw-signal-viewer :value="item" />
                  </template>
                </v-data-table>
              </v-card-text>
              <v-card-actions>
                <v-spacer />
                <v-btn @click="closeCreateEditDialog()" variant="text"> Cancel </v-btn>
                <v-btn color="info" @click="step = 3" :loading="loading"> Continue </v-btn>
              </v-card-actions>
            </v-card>
          </v-stepper-window-item>
          <v-stepper-window-item :value="3">
            <v-form @submit.prevent v-slot="{ isValid }">
              <v-card>
                <v-card-text>
                  Provide a name and description for your filter.
                  <v-text-field
                    v-model="name"
                    label="Name"
                    hint="A name for your saved search."
                    clearable
                    required
                    name="Name"
                    :rules="[rules.required]"
                  />
                  <v-textarea
                    v-model="description"
                    label="Description"
                    hint="A short description."
                    clearable
                    auto-grow
                    name="Description"
                    :rules="[rules.required]"
                  />
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn @click="closeCreateEditDialog()" variant="text"> Cancel </v-btn>
                  <v-btn
                    color="info"
                    @click="saveFilter()"
                    :loading="loading"
                    :disabled="!isValid.value"
                  >
                    Save
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-form>
          </v-stepper-window-item>
        </v-stepper-window>
      </v-stepper>
    </v-card>
  </v-dialog>
</template>

<script>
import MonacoEditor from "@/components/MonacoEditor.vue"

import { required } from "@/util/form"

import { mapActions } from "vuex"
import { mapFields } from "vuex-map-fields"

import SearchUtils from "@/search/utils"
import SignalApi from "@/signal/api"
import EntityTypeFilterCombobox from "@/entity_type/EntityTypeFilterCombobox.vue"
import EntityFilterCombobox from "@/entity/EntityFilterCombobox.vue"
import RawSignalViewer from "@/signal/RawSignalViewer.vue"

import ExpirationInput from "@/signal/filter/ExpirationInput.vue"
export default {
  setup() {
    return {
      rules: { required },
    }
  },
  name: "SignalFilterCreateDialog",
  props: {
    signalDefinition: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      activeTab: 0,
      editorOptions: {
        automaticLayout: true,
        renderValidationDecorations: "on",
      },
      previewFields: [
        { text: "Name", value: "signal.name", sortable: false },
        { text: "Case", value: "case.name", sortable: false },
        { text: "", value: "data-table-actions", sortable: false, align: "end" },
      ],
      windows: [5, 10, 15, 20, 30],
      step: 1,
      previewRows: {
        items: [],
        total: null,
      },
      previewRowsLoading: false,
      filters: {
        entity: [],
        project: [],
        entity_type: [],
      },
    }
  },
  components: {
    EntityFilterCombobox,
    EntityTypeFilterCombobox,
    RawSignalViewer,
    ExpirationInput,
    MonacoEditor,
  },
  computed: {
    ...mapFields("signalFilter", [
      "selected",
      "selected.description",
      "selected.expression",
      "selected.expiration",
      "selected.window",
      "selected.action",
      "selected.name",
      "selected.project",
      "loading",
      "dialogs.showCreateEdit",
    ]),
    expression_str: {
      get: function () {
        return JSON.stringify(this.expression, null, "\t") || "[]"
      },
      set: function (newValue) {
        this.expression = JSON.parse(newValue)
      },
    },
  },
  methods: {
    ...mapActions("signalFilter", ["closeCreateEditDialog", "save"]),
    saveFilter() {
      // reset local data
      this.save().then((filter) => {
        this.$emit("save", filter)
      })
    },
    resetFilters() {
      this.filters = {
        tag: [],
        project: [],
        tag_type: [],
      }
    },
    getPreviewData() {
      let params = {}
      if (this.expression) {
        params = { filter: JSON.stringify(this.expression) }
        this.previewRowsLoading = "error"
      }
      return SignalApi.getAllInstances(params).then((response) => {
        this.previewRows = response.data
        this.previewRowsLoading = false
      })
    },
  },
  created() {
    if (this.$route.query.project) {
      this.project = { name: this.$route.query.project }
    }
    this.getPreviewData()

    this.$watch(
      (vm) => [vm.filters.entity, vm.filters.entity_type],
      () => {
        this.expression = SearchUtils.createFilterExpression(this.filters)
        this.getPreviewData()
      }
    )
  },
}
</script>
