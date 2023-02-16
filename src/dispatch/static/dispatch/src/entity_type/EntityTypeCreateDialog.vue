<template>
    <v-dialog v-model="showCreateEdit" persistent max-width="800px">
      <template v-slot:activator="{ on }">
        <v-btn icon v-on="on">
          <v-icon>add</v-icon>
        </v-btn>
      </template>
      <v-card>
        <v-card-title>
          <span class="headline">Create New Entity Type</span>
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
                    <ValidationProvider rules="regexp" name="Regular Expression" immediate>
                        <v-textarea
                            v-model="regular_expression"
                            slot-scope="{ errors, valid }"
                            label="Regular Expression"
                            :error-messages="errors"
                            :success="valid"
                            hint="A regular expression pattern for your entity type. The first capture group will be used."
                            clearable
                        />
                    </ValidationProvider>
                    <v-flex xs12>
                        <ValidationProvider name="Field" immediate>
                            <v-text-field
                                v-model="field"
                                slot-scope="{ errors, valid }"
                                :error-messages="errors"
                                :success="valid"
                                label="Field"
                                hint="The field where the entity will be present. Support JSON Path expressions."
                                clearable
                            />
                        </ValidationProvider>
                    </v-flex>
                    <regex-box></regex-box>
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
                        required
                      />
                    </ValidationProvider>
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

  import RegexBox from "@/entity_type/regexplayground/RegexBox.vue"
  import SignalApi from "@/signal/api"
  import RawSignalViewer from "@/signal/RawSignalViewer.vue"

  extend("required", {
    ...required,
    message: "This field is required",
  })

  extend('regexp', {
    validate(value) {
        try {
            new RegExp(value);
            return true;
        } catch (e) {
            return false;
        }
    },
    message: 'Must be a valid regular expression pattern.'
  });

  export default {
    name: "SignalFilterCreateDialog",
    props: {
      value: {
        type: Object,
        default: null,
      },
    },
    data() {
    return {
      editorOptions: {
        automaticLayout: true,
        renderValidationDecorations: "on",
      },
      step: 1,
      previewFields: [
        { text: "Name", value: "signal.name", sortable: false },
        { text: "Case", value: "case.name", sortable: false },
        { text: "", value: "data-table-actions", sortable: false, align: "end" },
      ],
      previewRows: {
        items: [],
        total: null,
      },
      previewRowsLoading: false,
    };
  },
    components: {
      ValidationObserver,
      ValidationProvider,
      RawSignalViewer,
      RegexBox,
    },
    computed: {
      ...mapFields("entity_type", [
        "selected",
        "selected.description",
        "selected.regular_expression",
        "selected.field",
        "selected.name",
        "selected.project",
        "loading",
        "dialogs.showCreateEdit",
      ]),
      ...mapFields("route", ["query"]),
    },
    methods: {
      ...mapActions("entity_type", ["closeCreateEditDialog", "save"]),
      saveFilter() {
        this.save().then((filter) => {
          this.$emit("input", filter)
        })
      },
      getPreviewData() {
        // pass
        const expression = {
        and: [
            {
            join: {
                model: "SignalInstance",
                field: "id",
                on: "signal_instance.signal_id = signal.id"
            }
            },
            {
            match: {
                "SignalInstance.entities": {
                regular_expression: this.selected.regular_expression,
                field: `$..${this.selected.field}`,
                },
            },
            },
        ],
        };
        const params = { filter: expression };
        this.previewRowsLoading = true;
        return SignalApi.getAllInstances(params).then((response) => {
            this.previewRows = response.data;
            this.previewRowsLoading = false;
        });
    },
  },
  watch: {
        "selected.regular_expression": function() {
            this.getPreviewData();
        },
        "selected.field": function() {
            this.getPreviewData();
        },
    },
  }
  </script>
