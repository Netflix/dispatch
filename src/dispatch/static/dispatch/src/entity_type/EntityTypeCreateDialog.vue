<template>
  <ValidationObserver ref="observer">
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
            <v-stepper-step :complete="step > 1" step="1" editable> Build </v-stepper-step>
            <v-divider />
            <v-stepper-step step="2" editable> Save </v-stepper-step>
          </v-stepper-header>

          <v-stepper-items>
            <v-stepper-content step="1">
              <v-card v-model="isFormVisible">
                <v-card-text>
                  <ValidationObserver>
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
                    <ValidationProvider name="Field" immediate>
                      <v-text-field
                        v-model="jpath"
                        slot-scope="{ errors, valid }"
                        :error-messages="errors"
                        :success="valid"
                        label="JSON Path"
                        hint="The field where the entity will be present. Support JSON Path expressions."
                        clearable
                      />
                    </ValidationProvider>
                    <PlaygroundTextBox ref="playgroundTextBox" v-model="text" />
                  </ValidationObserver>
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-chip class="ma-2" :color="chipColor" outlined>
                    <v-icon left>{{ chipIcon }}</v-icon>
                    <span>
                      <animated-number :number="matchCount" /> entities in
                      <animated-number :number="matchedSignals.total" /> signals
                    </span>
                  </v-chip>
                  <v-btn icon @click="show_signals = !show_signals">
                    <v-icon>{{ show_signals ? "mdi-chevron-up" : "mdi-chevron-down" }}</v-icon>
                  </v-btn>
                  <v-btn @click="closeCreateEditDialog()" text> Cancel </v-btn>
                  <v-btn color="info" @click="step = 2"> Continue </v-btn>
                </v-card-actions>
                <v-expand-transition>
                  <div v-show="show_signals">
                    <v-divider></v-divider>
                    <v-spacer></v-spacer>
                    <v-card class="mt-3" color="red lighten-5" outlined rounded="xl">
                      <v-data-table
                        v-sortable-data-table
                        hide-default-footer
                        :headers="previewFields"
                        :items="matchedSignals.items"
                        item-key="id"
                        :loading="previewRowsLoading"
                      >
                        <draggable :list="matchedSignals.items"></draggable>
                        <template v-slot:item.data-table-actions="{ item }">
                          <raw-signal-viewer v-model="item.signal.raw" />
                          <v-tooltip bottom>
                            <template v-slot:activator="{ on, attrs }">
                              <v-icon v-bind="attrs" v-on="on" class="mr-2">
                                mdi-fingerprint
                              </v-icon>
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
            </v-stepper-content>
            <v-stepper-content step="2">
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
  </ValidationObserver>
</template>

<script>
import jsonpath from "jsonpath"
import { mapActions, mapMutations } from "vuex"
import { mapFields } from "vuex-map-fields"
import { required } from "vee-validate/dist/rules"
import { ValidationObserver, ValidationProvider, extend } from "vee-validate"
import draggable from "vuedraggable"

import AnimatedNumber from "@/components/AnimatedNumber.vue"
import PlaygroundTextBox from "@/entity_type/playground/PlaygroundTextBox.vue"
import SearchUtils from "@/search/utils"
import SignalApi from "@/signal/api"
import RawSignalViewer from "@/signal/RawSignalViewer.vue"
import { isValidRegex } from "@/entity_type/utils.js"
import { Sortable } from "sortablejs"

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
export default {
  name: "EntityTypeCreateDialog",
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
      $validator: null, // set a default value for $validator
      step: 1,
      show_signals: false,
      show_playground: false,
      text: "",
      isFormVisible: false,
      matchCount: 0,
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
      matchedSignals: {
        items: [],
        fingerprints: [],
        total: 0,
      },
      signalSample: {
        items: [],
        total: null,
      },
      filters: {
        created_at: [],
      },
      previewRowsLoading: false,
    }
  },
  components: {
    AnimatedNumber,
    draggable,
    PlaygroundTextBox,
    ValidationObserver,
    ValidationProvider,
    RawSignalViewer,
  },
  computed: {
    ...mapFields("entity_type", [
      "selected",
      "selected.description",
      "selected.regular_expression",
      "selected.jpath",
      "selected.name",
      "selected.project",
      "loading",
      "dialogs.showCreateEdit",
    ]),
    ...mapFields("route", ["query"]),
    chipColor() {
      return this.matchCount === 0 ? "grey lighten-1" : "red darken-3"
    },
    chipIcon() {
      return this.matchCount === 0 ? "mdi-information" : "mdi-fire"
    },
  },
  methods: {
    ...mapMutations("playground", ["updatePattern"]),
    ...mapActions("entity_type", ["closeCreateEditDialog", "save"]),
    saveFilter() {
      this.save().then((filter) => {
        this.$emit("input", filter)
      })
    },
    isValidRegex,
    resetTotalFound() {
      this.matchCount = 0
      this.matchedSignals.total = 0
      this.matchedSignals.items = []
    },
    getPreviewData() {
      const startDate = new Date()
      startDate.setDate(startDate.getDate() - 30)
      const startDateString = startDate.toISOString().replace("T", " ").replace("Z", "")

      const endDate = new Date()
      const endDateString = endDate.toISOString().replace("T", " ").replace("Z", "")

      this.filters.created_at = { start: startDateString, end: endDateString }

      const expression = SearchUtils.createFilterExpression(this.filters, "SignalInstance")
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
     * Finds entities in the given `signalInstance` that match the `entityType` definition.
     *
     * @param {object} signalInstance - An object representing a signal instance.
     * @param {object} entityType - An object containing the definition of the entity type to match against.
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
        this.matchCount += entityResults.size
        const fingerprint = signalInstance.fingerprint
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
            if (!this.isValidRegex(newVal)) {
              return
            }
            this.updatePattern(newVal)
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
              this.matchCount += matchedSignal.entities.length
            }
          })
        }
      })
    },
  },
  async mounted() {
    this.$nextTick(() => {
      const playgroundTextBoxEl = this.$el.querySelector(".playground-text-box")

      // Initialize Sortable
      Sortable.create(this.$el.querySelector("tbody"), {
        onMove: (evt) => {
          const playgroundTextBoxRect = playgroundTextBoxEl.getBoundingClientRect()
          const el = evt.dragged
          const elRect = el.getBoundingClientRect()
          const pointerX = evt.clientX
          const pointerY = evt.clientY

          // Check if mouse pointer is over PlaygroundTextBox component
          if (
            pointerX >= playgroundTextBoxRect.left &&
            pointerX <= playgroundTextBoxRect.right &&
            pointerY >= playgroundTextBoxRect.top &&
            pointerY <= playgroundTextBoxRect.bottom
          ) {
            const item = this.items[evt.oldIndex]
            this.text += item.signal.raw
          }
        },
      })
    })
  },
  created() {
    this.getPreviewData()
  },
  watch: {
    "selected.regular_expression": function (newVal, oldVal) {
      this.onSelectedChange("regular_expression", newVal, oldVal)
    },
    "selected.jpath": function (newVal, oldVal) {
      this.onSelectedChange("jpath", newVal, oldVal)
    },
  },
}
</script>
