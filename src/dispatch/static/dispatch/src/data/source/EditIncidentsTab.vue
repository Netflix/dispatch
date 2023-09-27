<template>
  <v-container>
    <incident-select v-model="selectedIncident" :project="project" />
    <v-list>
      <v-list-item v-for="(i, idx) in value" :key="i.id">
        <v-list-item-title>
          {{ i.name }}
        </v-list-item-title>
        <v-list-item-subtitle>
          {{ i.title }}
        </v-list-item-subtitle>

        <template #append>
          <v-btn icon variant="text" @click="remove(idx)">
            <v-icon>mdi-delete</v-icon>
          </v-btn>
        </template>
      </v-list-item>
    </v-list>
  </v-container>
</template>

<script>
import IncidentSelect from "@/incident/IncidentSelect.vue"
import { cloneDeep } from "lodash"

export default {
  name: "SourceEditIncidentsTab",

  components: {
    IncidentSelect,
  },

  props: {
    modelValue: {
      type: Array,
      default: function () {
        return []
      },
    },
    project: {
      type: Object,
      default: null,
    },
  },

  data() {
    return {
      selectedIncident: null,
    }
  },

  methods: {
    add() {
      const value = cloneDeep(this.modelValue)
      value.push(this.selectedIncident)
      this.selectedIncident = null
      this.$emit("update:modelValue", value)
    },
    remove(idx) {
      const value = cloneDeep(this.modelValue)
      value.splice(idx, 1)
      this.$emit("update:modelValue", value)
    },
  },

  created() {
    this.$watch(
      (vm) => [vm.selectedIncident],
      () => {
        if (!this.selectedIncident) return
        this.add()
      }
    )
  },
}
</script>
