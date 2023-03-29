<template>
  <v-container>
    <v-row no-gutter>
      <span class="subtitle-2">Workflow Parameters</span>
      <v-spacer />
      <v-tooltip bottom>
        <template v-slot:activator="{ on }">
          <v-btn small icon @click="addItem()" v-on="on">
            <v-icon>add</v-icon>
          </v-btn>
        </template>
        <span>Add Parameters</span>
      </v-tooltip>
    </v-row>
    <span v-for="(param, idx) in parameters" :key="idx">
      <v-row align="center" dense>
        <v-col cols="12" sm="1">
          <v-tooltip bottom>
            <template v-slot:activator="{ on }">
              <v-btn small icon @click="removeItem(idx)" v-on="on"><v-icon>remove</v-icon></v-btn>
            </template>
            <span>Remove Item</span>
          </v-tooltip>
        </v-col>
        <v-col cols="12" sm="5">
          <v-text-field
            label="Key"
            :value="param.key"
            @input="updateItemKey(idx, $event)"
            type="text"
          />
        </v-col>
        <v-col cols="12" sm="6">
          <entity-type-select
            v-model="param.value"
            :project="project"
            @input="updateItemValue(idx, $event)"
            :signalDefinition="selected"
          ></entity-type-select>
        </v-col>
      </v-row>
    </span>
  </v-container>
</template>

<script>
import { cloneDeep } from "lodash"
import EntityTypeSelect from "@/entity_type/EntityTypeSelect.vue"

export default {
  name: "WorkflowParametersEntityInput",

  components: { EntityTypeSelect },

  props: {
    value: {
      type: Array,
      default: function () {
        return []
      },
    },
  },

  computed: {
    parameters: {
      get() {
        return cloneDeep(this.value)
      },
    },
  },

  methods: {
    addItem() {
      this.parameters.push({ key: null, value: null })
      this.$emit("input", this.parameters)
    },
    removeItem(idx) {
      this.parameters.splice(idx, 1)
      this.$emit("input", this.parameters)
    },
    updateItemKey(idx, event) {
      this.parameters[idx]["key"] = event
      this.$emit("input", this.parameters)
    },
    updateItemValue(idx, event) {
      this.parameters[idx]["value"] = event["name"]
      this.$emit("input", this.parameters)
    },
  },
}
</script>
