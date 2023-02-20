<template>
  <ValidationObserver ref="observer">
    <v-dialog v-model="showCreateEdit" persistent max-width="1080px">
      <template v-slot:activator="{ on }">
        <v-btn elevation="1" v-on="on" small><v-icon>add</v-icon>Add entity type</v-btn>
      </template>
      <v-card>
        <v-window v-model="step">
          <v-window-item :value="1">
            <v-card class="px-6" color="grey lighten-5">
              <v-card-title class="text-h6 font-weight-regular justify-space-between">
                <span>New entity type</span>
                <v-spacer></v-spacer>
                <v-btn icon @click="closeCreateEditDialog()">
                  <v-icon>close</v-icon>
                </v-btn>
              </v-card-title>
              <v-row>
                <v-col cols="4">
                  <ValidationProvider rules="regexp" name="Regular Expression" immediate>
                    <v-textarea
                      v-model="regular_expression"
                      background-color="white"
                      color="black"
                      slot-scope="{ errors }"
                      label="Regular Expression"
                      hint="A regular expression pattern for your entity type. The first capture group will be used."
                      :error-messages="errors"
                      outlined
                    />
                  </ValidationProvider>
                  <ValidationProvider rules="jpath" name="Field" immediate>
                    <v-textarea
                      v-model="jpath"
                      background-color="white"
                      color="black"
                      slot-scope="{ errors }"
                      label="JSON Path"
                      hint="The field where the entity will be present. Supports JSON Path expressions."
                      :error-messages="errors"
                      outlined
                    />
                  </ValidationProvider>
                </v-col>
                <v-col cols="8">
                  <PlaygroundTextBox :text="editorValue" />
                </v-col>
              </v-row>
              <v-card-actions class="pt-6">
                <v-btn icon fab @click="show_signals = !show_signals">
                  <v-icon>{{ show_signals ? "mdi-chevron-up" : "mdi-chevron-down" }}</v-icon>
                </v-btn>
                <v-hover v-slot="{ hover }">
                  <v-chip
                    class="ma-2"
                    :color="chipColor"
                    :class="{ 'on-hover': hover }"
                    @click="show_signals = !show_signals"
                    outlined
                  >
                    <v-icon left>{{ chipIcon }}</v-icon>
                    <span>
                      <animated-number :number="totalEntities" /> entities in
                      <animated-number :number="matchedSignals.total" /> signals
                    </span>
                  </v-chip>
                </v-hover>
                <v-spacer />
                <v-btn color="info" @click="step = 2"> Continue </v-btn>
              </v-card-actions>
              <v-expand-transition>
                <div v-show="show_signals" style="height: 620px">
                  <v-divider></v-divider>
                  <v-spacer></v-spacer>
                  <v-card class="mt-3" outlined rounded="xl">
                    <v-data-table
                      style="height: 570px"
                      :headers="previewFields"
                      :items="matchedSignals.items"
                      item-key="id"
                      :loading="previewRowsLoading"
                      id="signal-table"
                      :footer-props="{ 'disable-items-per-page': true }"
                    >
                      <template id="sortable-row" v-slot:item.data-table-actions="{ item }">
                        <raw-signal-viewer v-model="item.signal.raw" />
                        <v-tooltip bottom>
                          <template v-slot:activator="{ on, attrs }">
                            <v-icon v-bind="attrs" v-on="on" class="mr-2"> mdi-fingerprint </v-icon>
                          </template>
                          <span>{{ item.signal.fingerprint }}</span>
                        </v-tooltip>
                      </template>
                    </v-data-table>
                    <v-card-actions> </v-card-actions>
                  </v-card>
                </div>
              </v-expand-transition>
            </v-card>
          </v-window-item>

          <v-window-item :value="2">
            <ValidationObserver disabled v-slot="{ invalid, validated }">
              <v-card>
                <v-card-title class="text-h6 font-weight-regular justify-space-between">
                  <span>New entity type</span>
                  <v-spacer></v-spacer>
                  <v-btn icon @click="closeCreateEditDialog()">
                    <v-icon>close</v-icon>
                  </v-btn>
                </v-card-title>
                <v-card-text>
                  <v-spacer></v-spacer>
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
                  <signal-definition-combobox></signal-definition-combobox>
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn :disabled="step === 1" text @click="step--"> Back </v-btn>
                  <v-btn
                    color="info"
                    @click="saveEntityType(selected.project)"
                    :loading="loading"
                    :disabled="invalid || !validated"
                  >
                    Save
                  </v-btn>
                </v-card-actions>
              </v-card>
            </ValidationObserver>
          </v-window-item>
        </v-window>
      </v-card>
    </v-dialog>
  </ValidationObserver>
</template>

<script>
import jsonpath from "jsonpath"
import { mapActions, mapMutations } from "vuex"
import { mapFields } from "vuex-map-fields"
import { required } from "vee-validate/dist/rules"
import { ValidationObserver, ValidationProvider, extend } from "vee-validate"
import draggable from "vuedraggable"
import { Sortable } from "sortablejs"

import AnimatedNumber from "@/components/AnimatedNumber.vue"
import PlaygroundTextBox from "@/entity_type/playground/PlaygroundTextBox.vue"
import SearchUtils from "@/search/utils"
import SignalApi from "@/signal/api"
import SignalDefinitionCombobox from "@/signal/SignalDefinitionCombobox.vue"
import RawSignalViewer from "@/signal/RawSignalViewer.vue"
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
  },
  data() {
    return {
      show_signals: false,
      show_playground: false,
      text: "",
      editorValue: "",
      previewFields: [
        { text: "Signal", value: "signal.signal.name", sortable: false },
        { text: "Case", value: "signal.case.name", sortable: false },
        {
          text: "",
          value: "data-table-actions",
          sortable: false,
          align: "end",
        },
      ],
      totalEntities: 0,
      matchedSignals: {
        items: [],
        fingerprints: [],
        total: 0,
      },
      signalSample: {
        items: [],
        total: null,
      },
      sampleFilter: {
        created_at: [],
      },
      previewRowsLoading: false,
      step: 1,
    }
  },
  components: {
    AnimatedNumber,
    draggable,
    PlaygroundTextBox,
    RawSignalViewer,
    SignalDefinitionCombobox,
    ValidationObserver,
    ValidationProvider,
  },
  computed: {
    ...mapFields("entity_type", [
      "selected",
      "selected.description",
      "selected.regular_expression",
      "selected.jpath",
      "selected.name",
      "loading",
      "dialogs.showCreateEdit",
    ]),
    ...mapFields("route", ["query"]),
    /**
     * Returns the color for the chip based on the total number of entities
     * @return {string} the color class to use for the chip
     */
    chipColor() {
      return this.totalEntities === 0 ? "grey lighten-1" : "red darken-3"
    },

    /**
     * Returns the icon for the chip based on the total number of entities
     * @return {string} the icon class to use for the chip
     */
    chipIcon() {
      return this.totalEntities === 0 ? "mdi-information" : "mdi-fire"
    },
  },
  methods: {
    ...mapMutations("playground", ["updatePattern", "updateJsonPath"]),
    ...mapActions("entity_type", ["closeCreateEditDialog", "save"]),
    saveEntityType() {
      this.save().then((entityType) => {
        this.$emit("input", entityType)
      })
    },
    isValidRegex,
    isValidJsonPath,
    resetTotalFound() {
      this.totalEntities = 0
      this.matchedSignals.total = 0
      this.matchedSignals.items = []
    },
    getPreviewData() {
      const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
      const today = new Date()

      this.sampleFilter.created_at = {
        start: this.dateToStringISO(thirtyDaysAgo),
        end: this.dateToStringISO(today),
      }

      const expression = SearchUtils.createFilterExpression(this.sampleFilter, "SignalInstance")
      if (!expression) return

      const params = { filter: JSON.stringify(expression), itemsPerPage: 100 }
      this.previewRowsLoading = "error"

      return SignalApi.getAllInstances(params)
        .then((response) => {
          this.signalSample = response.data
        })
        .catch((error) => {
          console.error(error)
        })
        .finally(() => {
          this.previewRowsLoading = false
        })
    },
    /**
     * Convert a date to a string in ISO format
     * @param {Date} date
     */
    dateToStringISO(date) {
      return date.toISOString().replace("T", " ").replace("Z", "")
    },
    /**
     * Finds entities in the given `signalInstance` that match the `entityType` definition.
     *
     * @param {object} signalInstance - An object representing a signal instance.
     * @param {object} entityType - An object containing the definition of the entity type to match against.
     *
     * @returns {array} - An array of unique entity objects that match the given `entityType` definition.
     */
    async findEntities(signalInstance, entityType) {
      // Initialize variables
      let signalHadEntity = false
      const entityResults = new Set()

      // Loop through each entity type pair
      const { entity_type, entity_regex, jpath } = {
        entity_regex: entityType.regular_expression
          ? new RegExp(entityType.regular_expression)
          : null,
        jpath: entityType.jpath,
      }

      const fingerprint = signalInstance.fingerprint

      // Check if the jpath is present in the signalInstance
      if (jpath) {
        const jpathValue = jsonpath.query(signalInstance.raw, jpath)[0]
        if (typeof jpathValue === "string") {
          if (!entity_regex) {
            entityResults.add({
              entity: jpathValue,
              entity_type: entity_type,
              signal: signalInstance,
            })
            signalHadEntity = true
          } else {
            const matchResult = entity_regex.exec(jpathValue)
            if (matchResult) {
              entityResults.add({
                entity: matchResult[0],
                entity_type: entity_type,
                signal: signalInstance,
              })
              signalHadEntity = true
            }
          }
        }
      } else {
        // Recursively search the signalInstance for matches using the entity regex
        function findEntitiesByRegex(val) {
          if (typeof val === "object" && val !== null) {
            for (const key in val) {
              if (Object.prototype.hasOwnProperty.call(val, key)) {
                findEntitiesByRegex(val[key])
              }
            }
          } else if (Array.isArray(val)) {
            for (const item of val) {
              findEntitiesByRegex(item)
            }
          } else if (typeof val === "string") {
            if (entity_regex) {
              const matchResult = entity_regex.exec(val)
              if (matchResult) {
                entityResults.add({
                  entity: matchResult[0],
                  entity_type: entity_type,
                  signal: signalInstance,
                })
                signalHadEntity = true
              }
            }
          }
        }

        // Loop through each key in the signalInstance and search for matches using the entity regex
        for (const key in signalInstance.raw) {
          if (Object.prototype.hasOwnProperty.call(signalInstance.raw, key)) {
            findEntitiesByRegex(signalInstance.raw[key])
          }
        }
      }

      if (signalHadEntity) {
        this.matchedSignals.total += 1
        this.totalEntities += entityResults.size
        if (!this.matchedSignals.items.find((s) => s.fingerprint === fingerprint)) {
          this.matchedSignals.fingerprints.push(fingerprint)
          this.matchedSignals.items.push({
            signal: signalInstance,
            entities: Array.from(entityResults),
          })
        }
      }
    },
    onSelectedChange(selector, newVal, oldVal) {
      this.$nextTick(() => {
        if (newVal !== oldVal) {
          if (selector === "regular_expression") {
            if (!this.isValidRegex(newVal)) return
            this.updatePattern(newVal)
          }
          if (selector === "jpath") {
            if (!this.isValidJsonPath(newVal)) return
            this.updateJsonPath(newVal)
          }
          let entityType = {
            regular_expression: this.selected.regular_expression,
            jpath: this.selected.jpath,
          }
          entityType[selector] = newVal

          this.resetTotalFound()

          // Keep track of already matched signals to avoid duplicates
          const matchedFingerprints = new Set(this.matchedSignals.items.map((s) => s.fingerprint))

          // Loop through signalSample items and find matching entities
          this.signalSample.items.forEach((signal) => {
            if (!matchedFingerprints.has(signal.fingerprint)) {
              this.findEntities(signal, entityType)
            } else {
              // If the signal has already been matched, increment match count
              this.matchedSignals.total += 1
              this.matchedSignals.items.push(signal)
              const matchedSignal = this.matchedSignals.items.find(
                (signal) => signal.signal.fingerprint === signalFingerprint
              )
              this.totalEntities += matchedSignal.entities.length
            }
          })
        }
      })
    },
    /**
     * This function sets up the draggable feature for the signal table and the playground editor.
     * Updates the editor value with the selected signal raw JSON when dragging ends.
     */
    setupDraggable() {
      this.$nextTick(() => {
        const playgroundEditorEl = document.getElementById("playground-editor")
        const signalTable = document.getElementById("signal-table")

        if (!playgroundEditorEl || !signalTable) {
          return
        }

        const tableBody = signalTable.getElementsByTagName("tbody")[0]

        const sortableOptions = {
          animation: 150,
          onEnd: (event) => {
            // DOM location of the playground editor element
            const playgroundTextBoxRect = playgroundEditorEl.getBoundingClientRect()
            // Location of the mouse cursor
            const mouseX = event.originalEvent.clientX
            const mouseY = event.originalEvent.clientY
            // If the mouse cursor is over the playground box
            if (
              mouseX >= playgroundTextBoxRect.left &&
              mouseX <= playgroundTextBoxRect.right &&
              mouseY >= playgroundTextBoxRect.top &&
              mouseY <= playgroundTextBoxRect.bottom
            ) {
              // Update the editor value to the raw signal data of the dragged row
              const item = this.signalSample.items[event.oldIndex]
              const stringSignal = JSON.stringify(item.raw, null, 2)
              this.updateEditorValue(stringSignal)
            }
          },
        }
        Sortable.create(tableBody, sortableOptions)
      })
    },
    updateEditorValue(newValue) {
      this.editorValue = newValue
    },
  },
  created() {
    if (this.project) {
      this.selected.project = this.project
    }
    this.getPreviewData()
  },
  watch: {
    "selected.regular_expression": function (newVal, oldVal) {
      if (!this.signalSample.items.length) return
      this.onSelectedChange("regular_expression", newVal, oldVal)
    },
    "selected.jpath": function (newVal, oldVal) {
      if (!this.signalSample.items.length) return
      this.onSelectedChange("jpath", newVal, oldVal)
    },
    matchedSignals: {
      handler(newVal) {
        // We need the table to have rows to setup draggable
        if (newVal.items.length > 1) {
          this.setupDraggable()
        }
      },
      deep: true,
    },
  },
}
</script>

<style scoped>
.v-chip {
  transition: opacity 0.4s ease-in-out;
}

.v-chip.on-hover {
  opacity: 1;
  transform: translateY(-2px);
  box-shadow: 0 5px 8px rgba(0, 0, 0, 0.3);
  transition: all 0.4s ease-in-out;
}

.v-chip:not(.on-hover) {
  opacity: 0.8;
}
</style>
