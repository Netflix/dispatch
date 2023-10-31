<template>
  <v-container>
    <v-row no-gutter>
      <span class="text-subtitle-2">Workflow Parameters</span>
      <v-spacer />
      <v-tooltip location="bottom">
        <template #activator="{ props }">
          <v-btn size="small" icon variant="text" @click="addItem()" v-bind="props">
            <v-icon>mdi-plus</v-icon>
          </v-btn>
        </template>
        <span>Add Parameters</span>
      </v-tooltip>
    </v-row>
    <span v-for="(param, idx) in parameters" :key="idx">
      <v-row align="center" dense>
        <v-col cols="12" sm="1">
          <v-tooltip location="bottom">
            <template #activator="{ props }">
              <v-btn size="small" icon variant="text" @click="removeItem(idx)" v-bind="props">
                <v-icon>mdi-minus</v-icon>
              </v-btn>
            </template>
            <span>Remove Item</span>
          </v-tooltip>
        </v-col>
        <v-col cols="12" sm="5">
          <v-text-field
            label="Key"
            :model-value="param.key"
            @update:model-value="updateItemKey(idx, $event)"
            type="text"
          />
        </v-col>
        <v-col cols="12" sm="6">
          <entity-type-select
            :model-value="param.value"
            @update:model-value="updateItemValue(idx, $event)"
            :project="project"
            :signalDefinition="selected"
          />
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
    modelValue: {
      type: Array,
      default: function () {
        return []
      },
    },
  },

  computed: {
    parameters: {
      get() {
        return cloneDeep(this.modelValue)
      },
    },
  },

  methods: {
    addItem() {
      this.parameters.push({ key: null, value: null })
      this.$emit("update:modelValue", this.parameters)
    },
    removeItem(idx) {
      this.parameters.splice(idx, 1)
      this.$emit("update:modelValue", this.parameters)
    },
    updateItemKey(idx, event) {
      this.parameters[idx]["key"] = event
      this.$emit("update:modelValue", this.parameters)
    },
    updateItemValue(idx, event) {
      this.parameters[idx]["value"] = event["name"]
      this.$emit("update:modelValue", this.parameters)
    },
  },
}
</script>
