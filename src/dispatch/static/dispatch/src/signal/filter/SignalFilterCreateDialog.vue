<template>
  <v-dialog v-model="showCreateEdit" persistent max-width="800px">
    <template v-slot:activator="{ on }">
      <v-btn icon v-on="on">
        <v-icon>add</v-icon>
      </v-btn>
    </template>
    <v-card>
      <v-card-title>
        <span class="headline">Create Signal Filter</span>
        <v-spacer></v-spacer>
      </v-card-title>
      <v-stepper v-model="step">
        <v-stepper-header>
          <v-stepper-step :complete="step > 1" step="1" editable> Filter </v-stepper-step>
          <v-divider />

          <v-stepper-step :complete="step > 2" step="2" editable> Preview </v-stepper-step>
          <v-divider />

          <v-stepper-step step="3" editable> Save </v-stepper-step>
        </v-stepper-header>

        <v-stepper-items>
          <v-stepper-content step="1">
            <v-card>
              <v-card-text>
                Define the entity and entity types that will be used to match with existing signal
                instances.
                <v-tabs color="primary" right>
                  <v-tab>Basic</v-tab>
                  <v-tab>Advanced</v-tab>
                  <v-tab-item>
                    <v-list dense>
                      <v-list-item>
                        <v-list-item-content>
                          <entity-filter-combobox
                            :project="project"
                            v-model="filters.entity"
                            label="Entities"
                          />
                        </v-list-item-content>
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content>
                          <entity-type-filter-combobox
                            :project="project"
                            :signalDefinition="signalDefinition"
                            v-model="filters.entity_type"
                            label="Entity Types"
                          />
                        </v-list-item-content>
                      </v-list-item>
                    </v-list>
                  </v-tab-item>
                  <v-tab-item>
                    <div style="height: 400px">
                      <MonacoEditor
                        v-model="expression_str"
                        :options="editorOptions"
                        language="json"
                      ></MonacoEditor>
                    </div>
                  </v-tab-item>
                </v-tabs>
              </v-card-text>
              <v-card-actions>
                <v-spacer />
                <v-btn @click="closeCreateEditDialog()" text> Cancel </v-btn>
                <v-btn color="info" @click="step = 2"> Continue </v-btn>
              </v-card-actions>
            </v-card>
          </v-stepper-content>

          <v-stepper-content step="2">
            <v-card>
              <v-card-text>
                Examples matching your filter:
                <v-data-table
                  hide-default-footer
                  :headers="previewFields"
                  :items="previewRows.items"
                  :loading="previewRowsLoading"
                >
                  <template v-slot:item.data-table-actions="{ item }">
                    <raw-signal-viewer v-model="item.raw" />
                    <v-tooltip bottom>
                      <template v-slot:activator="{ on, attrs }">
                        <v-icon v-bind="attrs" v-on="on" class="mr-2"> mdi-fingerprint </v-icon>
                      </template>
                      <span>{{ item.fingerprint }}</span>
                    </v-tooltip>
                  </template>
                </v-data-table>
              </v-card-text>
              <v-card-actions>
                <v-spacer />
                <v-btn @click="closeCreateEditDialog()" text> Cancel </v-btn>
                <v-btn color="info" @click="step = 3" :loading="loading"> Continue </v-btn>
              </v-card-actions>
            </v-card>
          </v-stepper-content>
          <v-stepper-content step="3">
            <ValidationObserver disabled v-slot="{ invalid, validated }">
              <v-card>
                <v-card-text>
                  Provide a name and description for your filter.
                  <ValidationProvider name="Name" rules="required" immediate>
                    <v-text-field
                      v-model="name"
                      label="Name"
                      hint="A name for your saved search."
                      slot-scope="{ errors, valid }"
                      :error-messages="errors"
                      :success="valid"
                      clearable
                      required
                    />
                  </ValidationProvider>
                  <ValidationProvider name="Description" rules="required" immediate>
                    <v-textarea
                      v-model="description"
                      label="Description"
                      hint="A short description."
                      slot-scope="{ errors, valid }"
                      :error-messages="errors"
                      :success="valid"
                      clearable
                      auto-grow
                    />
                  </ValidationProvider>
                  <ValidationProvider name="Action" rules="required" immediate>
                    <v-radio-group label="Action" v-model="action" class="justify-right">
                      <v-radio label="Snooze" value="snooze"></v-radio>
                      <v-radio label="Deduplicate" value="deduplicate"></v-radio>
                    </v-radio-group>
                  </ValidationProvider>
                  <v-select
                    v-if="action === 'deduplicate'"
                    persistent-hint
                    label="Window (minutes)"
                    :items="windows"
                    v-model="window"
                  ></v-select>
                  <expiration-input
                    v-if="action == 'snooze'"
                    persistent-hint
                    v-model="expiration"
                  ></expiration-input>
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn @click="closeCreateEditDialog()" text> Cancel </v-btn>
                  <v-btn
                    color="info"
                    @click="saveFilter()"
                    :loading="loading"
                    :disabled="invalid || !validated"
                  >
                    Save
                  </v-btn>
                </v-card-actions>
              </v-card>
            </ValidationObserver>
          </v-stepper-content>
        </v-stepper-items>
      </v-stepper>
    </v-card>
  </v-dialog>
</template>

<script>
import { ValidationObserver, ValidationProvider, extend } from "vee-validate"
import { mapActions } from "vuex"
import { mapFields } from "vuex-map-fields"
import { required } from "vee-validate/dist/rules"
import SearchUtils from "@/search/utils"
import SignalApi from "@/signal/api"
import EntityTypeFilterCombobox from "@/entity_type/EntityTypeFilterCombobox.vue"
import EntityFilterCombobox from "@/entity/EntityFilterCombobox.vue"
import RawSignalViewer from "@/signal/RawSignalViewer.vue"

import ExpirationInput from "@/signal/filter/ExpirationInput.vue"

extend("required", {
  ...required,
  message: "This field is required",
})
export default {
  name: "SignalFilterCreateDialog",
  props: {
    value: {
      type: Object,
      default: null,
    },
    signalDefinition: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
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
    ValidationObserver,
    ValidationProvider,
    RawSignalViewer,
    ExpirationInput,
    MonacoEditor: () => import("monaco-editor-vue"),
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
    ...mapFields("route", ["query"]),
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
        this.$emit("input", filter)
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
    if (this.query.project) {
      this.project = { name: this.query.project }
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
