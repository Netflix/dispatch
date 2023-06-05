<template>
  <ValidationObserver v-slot="{ invalid, validated }">
    <v-navigation-drawer v-model="showCreateEdit" app clipped right width="1000">
      <template v-slot:prepend>
        <v-list-item two-line>
          <v-list-item-content>
            <v-list-item-title v-if="id" class="title"> Edit </v-list-item-title>
            <v-list-item-title v-else class="title"> New </v-list-item-title>
            <v-list-item-subtitle>Entity Type</v-list-item-subtitle>
          </v-list-item-content>
          <v-btn
            icon
            color="info"
            :loading="loading"
            :disabled="invalid || !validated"
            @click="save()"
          >
            <v-icon>save</v-icon>
          </v-btn>
          <v-btn icon color="secondary" @click="closeCreateEdit()">
            <v-icon>close</v-icon>
          </v-btn>
        </v-list-item>
      </template>
      <v-card flat tile>
        <v-app-bar color="white" flat>
          <v-toolbar-title class="subtitle-2"> Details </v-toolbar-title>
        </v-app-bar>
        <v-card-text>
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
          <v-radio-group v-model="scope" label="Scope" row>
            <v-tooltip max-width="250px" left>
              <template v-slot:activator="{ on, attrs }">
                <v-radio v-bind="attrs" v-on="on" label="Multiple" value="multiple"></v-radio>
              </template>
              <span>
                An entity type with a definition scope of 'multiple' can be associated with one or
                more entities, use this scope if you think that the entity type is useful across
                multiple definitions.
              </span>
            </v-tooltip>
            <v-tooltip max-width="250px" left>
              <template v-slot:activator="{ on, attrs }">
                <v-radio v-bind="attrs" v-on="on" label="All" value="all"></v-radio>
              </template>
              <span>
                An entity type with a definition scope of 'all' will be associated with all current
                and future definitions. This is most useful or extracting common information across
                your defintions.
              </span>
            </v-tooltip>
          </v-radio-group>
          <signal-definition-combobox
            v-model="localSignals"
            label="Signal Definitions"
            hint="The signal definitions that will be associated with your entity type."
            :project="project"
            v-if="scope === 'multiple'"
          />
        </v-card-text>
      </v-card>
      <v-card flat tile>
        <v-app-bar color="white" flat>
          <v-toolbar-title class="subtitle-2"> Expression Configuration </v-toolbar-title>
          <v-spacer></v-spacer>
        </v-app-bar>
        <v-card-text>
          Entity types are used to extract useful metadata out of signals. Define either a RegEx or
          JSON Path expression to pull entities out of a signals raw json.
          <v-radio-group label="Type" v-model="type" row>
            <v-radio label="Regular Expression" value="regex"></v-radio>
            <v-radio label="JSON Path" value="json"></v-radio>
          </v-radio-group>
          <v-text-field
            v-if="type === 'regex'"
            v-model="localRegularExpression"
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
            v-model="localJpath"
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
                <template v-if="!signalInstances.length">
                  No example signals are currently available for this definition.
                </template>
                <template v-for="(instance, index) in signalInstances" v-else>
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
                <template v-else> </template>
              </v-list>
            </v-col>
            <v-col cols="8">
              <playground-text-box :text="editorValue" />
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </v-navigation-drawer>
  </ValidationObserver>
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
  name: "EntityTypeCreateSheet",
  data() {
    return {
      type: "json",
      componentKey: 0,
      signalInstances: [],
      localSignals: [],
      localJpath: "",
      localRegularExpression: "",
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
      "selected.id",
      "selected.name",
      "selected.scope",
      "selected.description",
      "selected.signals",
      "selected.project",
      "selected.regular_expression",
      "selected.jpath",
      "loading",
    ]),
    ...mapFields("route", ["query"]),
  },
  methods: {
    ...mapMutations("playground", ["updatePattern", "updateJsonPath"]),
    ...mapActions("entity_type", ["createdSignalDefinition", "closeCreateEdit", "save"]),
    isValidRegex,
    isValidJsonPath,
    getSignalData(definitions) {
      if (definitions) {
        this.filters.signal = definitions
      }

      const expression = SearchUtils.createFilterExpression(this.filters)
      if (!expression) return

      const params = { filter: JSON.stringify(expression), itemsPerPage: 5 }

      return SignalApi.getAllInstances(params)
        .then((response) => {
          this.signalInstances = response.data.items
          this.updateEditorValue(this.signalInstances[0].raw)
        })
        .catch((error) => {
          console.error(error)
        })
    },
    onSelectedChange(selector, newVal, oldVal) {
      this.$nextTick(() => {
        if (newVal !== oldVal) {
          if (selector === "localRegularExpression") {
            if (!newVal) {
              // Ensures we reset the pattern
              this.updatePattern(newVal)
            }
            if (!this.isValidRegex(newVal)) return
            this.updatePattern(newVal)
          }
          if (selector === "localJpath") {
            if (!newVal) {
              // Ensures we reset the jsonpath
              this.updateJsonPath(newVal)
            }
            if (!this.isValidJsonPath(newVal)) return
            this.updateJsonPath(newVal)
          }
          let entityType = {
            localRegularExpression: this.localRegularExpression,
            localJpath: this.localJpath,
          }
          entityType[selector] = newVal
        }
      })
    },
    updateEditorValue(newValue) {
      this.editorValue = JSON.stringify(newValue, null, 2)
    },
  },
  created() {
    if (this.query.project) {
      this.project = { name: this.query.project }
    }
  },
  watch: {
    localRegularExpression: function (newVal, oldVal) {
      this.onSelectedChange("localRegularExpression", newVal, oldVal)
      this.regular_expression = newVal
    },
    localJpath: function (newVal, oldVal) {
      this.onSelectedChange("localJpath", newVal, oldVal)
      this.jpath = newVal
    },
    localSignals: function (newVal, oldVal) {
      this.getSignalData(this.newVal)
      this.signals = this.newVal
    },
  },
}
</script>
