<template>
  <v-form @submit.prevent v-slot="{ isValid }">
    <v-navigation-drawer v-model="showCreateEdit" location="right" width="1000">
      <template #prepend>
        <v-list-item lines="two">
          <v-list-item-title v-if="id" class="text-h6"> Edit </v-list-item-title>
          <v-list-item-title v-else class="text-h6"> New </v-list-item-title>
          <v-list-item-subtitle>Entity Type</v-list-item-subtitle>

          <template #append>
            <v-btn
              icon
              variant="text"
              color="info"
              :loading="loading"
              :disabled="!isValid.value"
              @click="save()"
            >
              <v-icon>mdi-content-save</v-icon>
            </v-btn>
            <v-btn icon variant="text" color="secondary" @click="closeCreateEdit()">
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </template>
        </v-list-item>
      </template>
      <v-card flat rounded="0">
        <v-toolbar color="transparent">
          <v-toolbar-title class="text-subtitle-2"> Details </v-toolbar-title>
        </v-toolbar>
        <v-card-text>
          <v-text-field
            v-model="name"
            label="Name"
            hint="A name for your entity type."
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
          />
          <v-radio-group v-model="scope" label="Scope" inline>
            <v-tooltip max-width="250px" location="left">
              <template #activator="{ props }">
                <v-radio v-bind="props" label="Multiple" value="multiple" />
              </template>
              <span>
                An entity type with a definition scope of 'multiple' can be associated with one or
                more entities, use this scope if you think that the entity type is useful across
                multiple definitions.
              </span>
            </v-tooltip>
            <v-tooltip max-width="250px" location="left">
              <template #activator="{ props }">
                <v-radio v-bind="props" label="All" value="all" />
              </template>
              <span>
                An entity type with a definition scope of 'all' will be associated with all current
                and future definitions. This is most useful or extracting common information across
                your defintions.
              </span>
            </v-tooltip>
          </v-radio-group>
          <signal-definition-combobox
            v-model="signals"
            label="Signal Definitions"
            hint="The signal definitions that will be associated with your entity type."
            :project="project"
            v-if="scope === 'multiple'"
          />
        </v-card-text>
      </v-card>
      <v-card flat rounded="0">
        <v-toolbar color="transparent">
          <v-toolbar-title class="text-subtitle-2"> Expression Configuration </v-toolbar-title>
        </v-toolbar>
        <v-card-text>
          Entity types are used to extract useful metadata out of signals. Define either a RegEx or
          JSON Path expression to pull entities out of a signals raw json.
          <v-radio-group label="Type" v-model="type" inline>
            <v-radio label="Regular Expression" value="regex" />
            <v-radio label="JSON Path" value="json" />
          </v-radio-group>
          <v-text-field
            v-if="type === 'regex'"
            v-model="regular_expression"
            label="Regular Expression"
            hint="A regular expression pattern for your entity type. The first capture group will be used."
          >
            <template #append>
              <v-btn
                icon
                variant="text"
                href="https://cheatography.com/davechild/cheat-sheets/regular-expressions/"
                target="_blank"
              >
                <v-icon>mdi-help-circle-outline</v-icon>
              </v-btn>
            </template>
          </v-text-field>
          <v-text-field
            v-if="type === 'json'"
            v-model="jpath"
            label="JSON Path"
            hint="The field where the entity will be present. Supports JSON Path expressions."
          >
            <template #append>
              <v-btn
                icon
                variant="text"
                href="https://github.com/json-path/JsonPath#path-examples"
                target="_blank"
              >
                <v-icon>mdi-help-circle-outline</v-icon>
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
                <template
                  v-else
                  v-for="(instance, index) in signalInstances"
                  :key="`item-${index}`"
                >
                  <v-list-item>
                    <v-list-item-title>{{ instance.id }}</v-list-item-title>

                    <template #append>
                      <v-btn icon variant="text" @click="updateEditorValue(instance.raw)">
                        <v-icon>mdi-arrow-right</v-icon>
                      </v-btn>
                    </template>
                  </v-list-item>
                  <v-divider v-if="index < signalInstances.length - 1" />
                </template>
              </v-list>
            </v-col>
            <v-col cols="8">
              <playground-text-box :text="editorValue" />
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </v-navigation-drawer>
  </v-form>
</template>

<script>
import { required } from "@/util/form"
import { mapActions, mapMutations } from "vuex"
import { mapFields } from "vuex-map-fields"

import PlaygroundTextBox from "@/entity_type/playground/PlaygroundTextBox.vue"
import SearchUtils from "@/search/utils"
import SignalApi from "@/signal/api"
import SignalDefinitionCombobox from "@/signal/SignalDefinitionCombobox.vue"
import { isValidJsonPath, isValidRegex } from "@/entity_type/utils.js"

export default {
  setup() {
    return {
      rules: { required },
    }
  },
  name: "EntityTypeCreateSheet",
  data() {
    return {
      type: "json",
      componentKey: 0,
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
    }
  },
  components: {
    PlaygroundTextBox,
    SignalDefinitionCombobox,
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
      "selected.loading",
    ]),
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
            regular_expression: this.regular_expression,
            jpath: this.jpath,
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
    if (this.$route.query.project) {
      this.project = { name: this.$route.query.project }
    }
  },
  watch: {
    regular_expression(newVal, oldVal) {
      this.onSelectedChange("regular_expression", newVal, oldVal)
    },
    jpath(newVal, oldVal) {
      this.onSelectedChange("jpath", newVal, oldVal)
    },
    signals(newVal) {
      this.getSignalData(newVal)
    },
  },
}
</script>
