<template>
  <v-container>
    <v-row no-gutter>
      <span class="subtitle-2">Workflow Parameters</span>
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
          ></v-text-field>
        </v-col>
        <v-col cols="12" sm="6">
          <v-text-field
            label="Default Value"
            :value="param.value"
            @input="updateItemValue(idx, $event)"
            type="text"
          ></v-text-field>
        </v-col>
      </v-row>
    </span>
    <v-row align="center" dense>
      <v-col cols="12" sm="12">
        <v-btn @click="addItem()">Add Parameter</v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { cloneDeep } from "lodash"

export default {
  name: "WorkflowParameterInput",

  components: {},

  props: {
    value: {
      type: Array,
      default: function() {
        return []
      }
    }
  },

  computed: {
    parameters: {
      get() {
        return cloneDeep(this.value)
      }
    }
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
      this.parameters[idx]["value"] = event
      this.$emit("input", this.parameters)
    }
  }
}
</script>
