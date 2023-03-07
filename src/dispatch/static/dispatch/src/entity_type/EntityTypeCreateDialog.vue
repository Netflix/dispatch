<template>
  <v-dialog v-model="showCreateEdit" max-width="1000px" persistent>
    <template v-slot:activator="{ on }">
      <v-btn @click="createEditShow(signalDefinition)" v-on="on" icon><v-icon>add</v-icon></v-btn>
    </template>
    <v-card>
      <v-card-title>Create Entity Type </v-card-title>
      <v-stepper v-model="step">
        <v-stepper-header>
          <v-stepper-step :complete="step > 1" step="1" editable> Define Filter </v-stepper-step>
          <v-divider />
          <v-stepper-step step="2" editable> Save </v-stepper-step>
        </v-stepper-header>
        <v-stepper-items>
          <v-stepper-content step="1">
            <v-card flat height="100%">
              <v-card-text>
                Entity types are used to extract useful metadata out of signals. Define either a
                RegEx or JSON Path expression to pull entities out of a signals raw json.
                <v-radio-group label="Type" v-model="type" row>
                  <v-radio label="Regular Expression" value="regex"></v-radio>
                  <v-radio label="JSON Path" value="json"></v-radio>
                </v-radio-group>
                <v-text-field
                  v-if="type === 'regex'"
                  v-model="regular_expression"
                  label="Regular Expression"
                  hint="A regular expression pattern for your entity type. The first capture group will be used."
                >
                  <template v-slot:append-outer>
                    <v-btn
                      icon
                      href="https://cheatography.com/davechild/cheat-sheets/regular-expressions/"
                      target="_blank"
                    >
                      <v-icon> mdi-help-circle-outline </v-icon>
                    </v-btn>
                  </template>
                </v-text-field>
                <v-text-field
                  v-if="type === 'json'"
                  v-model="jpath"
                  label="JSON Path"
                  hint="The field where the entity will be present. Supports JSON Path expressions."
                >
                  <template v-slot:append-outer>
                    <v-btn
                      icon
                      href="https://github.com/json-path/JsonPath#path-examples"
                      target="_blank"
                    >
                      <v-icon> mdi-help-circle-outline </v-icon>
                    </v-btn>
                  </template>
                </v-text-field>
                Example signals:
                <v-row>
                  <v-col cols="4">
                    <v-list>
                      <template
                        v-for="(instance, index) in signalInstances"
                        v-if="signalInstances.length"
                      >
                        <v-list-item>
                          <v-list-item-content>
                            <v-list-item-title>{{ instance.id }}</v-list-item-title>
                          </v-list-item-content>
                          <v-list-item-action>
                            <v-btn icon @click="updateEditorValue(instance.raw)">
                              <v-icon>mdi-arrow-right</v-icon>
                            </v-btn>
                          </v-list-item-action>
                        </v-list-item>
                        <v-divider v-if="index < signalInstances.length - 1"></v-divider>
                      </template>
                      <template v-else>
                        No signals are currently available for this definition.
                      </template>
                    </v-list>
                  </v-col>
                  <v-col cols="8">
                    <playground-text-box :text="editorValue" />
                  </v-col>
                </v-row>
              </v-card-text>
              <v-card-actions>
                <v-spacer />
                <v-btn @click="closeCreateEditDialog()" text> Cancel </v-btn>
                <v-btn color="info" @click="step = 2" :loading="loading"> Continue </v-btn>
              </v-card-actions>
            </v-card>
          </v-stepper-content>
          <v-stepper-content step="2">
            <ValidationObserver disabled v-slot="{ invalid, validated }">
              <v-card>
                <v-card-text>
                  <v-card-text>
                    Provide a name and a description for your entity type:
                  </v-card-text>
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
                  <ValidationProvider name="Description" immediate>
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
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn @click="closeCreateEditDialog()" text> Cancel </v-btn>
                  <v-btn
                    color="info"
                    @click="saveEntityType()"
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
import { mapActions, mapMutations } from "vuex"
import { mapFields } from "vuex-map-fields"
import { required } from "vee-validate/dist/rules"
import { ValidationObserver, ValidationProvider, extend } from "vee-validate"
import PlaygroundTextBox from "@/entity_type/playground/PlaygroundTextBox.vue"
import SearchUtils from "@/search/utils"
import SignalApi from "@/signal/api"
import SignalDefinitionCombobox from "@/signal/SignalDefinitionCombobox.vue"
import { isValidJsonPath, isValidRegex } from "@/entity_type/utils.js"

extend("required", {
  ...required,
  message: "This field is required",
})
extend("regexp", {
  validate(value) {
    return isValidRegex(value)
  },
  message: "Must be a valid regular expression pattern.",
})
extend("jpath", {
  validate(value) {
    return isValidJsonPath(value)
  },
  message: "Must be a valid JSON path expression.",
})
export default {
  name: "EntityTypeCreateDialog",
  props: {
    project: {
      type: Object,
      required: true,
    },
    signalDefinition: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      type: "json",
      signalInstances: [],
      filters: {
        signal: [],
      },
      editorValue: JSON.stringify(
        {
          name: "process_events",
          hostIdentifier: "host1",
          calendarTime: "2022-10-19T10:35:01Z",
          time: 1618698901,
          columns: {
            pid: 888,
            path: "/bin/process",
            cmdline: "/bin/process -arg1 value1 -arg2 value2",
            state: "running",
            parent: 555,
            created_at: 1918698901,
            updated_at: 2118698901,
          },
        },
        null,
        2
      ),
      step: 1,
    }
  },
  components: {
    PlaygroundTextBox,
    SignalDefinitionCombobox,
    ValidationObserver,
    ValidationProvider,
  },
  computed: {
    ...mapFields("entity_type", [
      "dialogs.showCreateEdit",
      "selected",
      "selected.description",
      "selected.regular_expression",
      "selected.jpath",
      "selected.signal",
      "selected.working_signal",
      "selected.name",
      "loading",
    ]),
    ...mapFields("route", ["query"]),
  },
  methods: {
    ...mapMutations("playground", ["updatePattern", "updateJsonPath"]),
    ...mapActions("entity_type", ["createEditShow", "closeCreateEditDialog", "save"]),
    saveEntityType() {
      this.save().then((entityType) => {
        this.$emit("input", entityType)
      })
    },
    isValidRegex,
    isValidJsonPath,
    getSignalData(definition) {
      if (definition) {
        this.filters.signal = [definition]
      }

      const expression = SearchUtils.createFilterExpression(this.filters)
      if (!expression) return

      const params = { filter: JSON.stringify(expression), itemsPerPage: 5 }

      return SignalApi.getAllInstances(params)
        .then((response) => {
          this.signalInstances = response.data.items
        })
        .catch((error) => {
          console.error(error)
        })
    },
    onSelectedChange(selector, newVal, oldVal) {
      this.$nextTick(() => {
        if (newVal !== oldVal) {
          if (selector === "regular_expression") {
            if (!newVal) {
              // Ensures we reset the pattern
              this.updatePattern(newVal)
            }
            if (!this.isValidRegex(newVal)) return
            this.updatePattern(newVal)
          }
          if (selector === "jpath") {
            if (!newVal) {
              // Ensures we reset the jsonpath
              this.updateJsonPath(newVal)
            }
            if (!this.isValidJsonPath(newVal)) return
            this.updateJsonPath(newVal)
          }
          let entityType = {
            regular_expression: this.selected.regular_expression,
            jpath: this.selected.jpath,
          }
          entityType[selector] = newVal
        }
      })
    },
    /**
     * This function sets up the draggable feature for the signal table and the playground editor.
     * Updates the editor value with the selected signal raw JSON when dragging ends.
     */
    updateEditorValue(newValue) {
      this.editorValue = JSON.stringify(newValue, null, 2)
    },
  },
  created() {
    if (this.project) {
      this.selected.project = this.project
    }
  },
  watch: {
    "selected.regular_expression": function (newVal, oldVal) {
      this.onSelectedChange("regular_expression", newVal, oldVal)
    },
    "selected.jpath": function (newVal, oldVal) {
      this.onSelectedChange("jpath", newVal, oldVal)
    },
    "selected.working_signal": function (newVal) {
      this.getSignalData(newVal)
    },
  },
}
</script>
