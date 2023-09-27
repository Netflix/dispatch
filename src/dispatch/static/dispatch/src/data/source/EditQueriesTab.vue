<template>
  <v-container>
    <query-select v-model="selectedQuery" :project="project" />
    <v-list>
      <v-list-item v-for="(i, idx) in value" :key="i.id">
        <v-list-item-title>
          {{ i.name }}
        </v-list-item-title>
        <v-list-item-subtitle>
          {{ i.description }}
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
import { mapFields } from "vuex-map-fields"
import QuerySelect from "@/data/query/QuerySelect.vue"
import { cloneDeep } from "lodash"

export default {
  name: "SourceEditQueriesTab",

  components: {
    QuerySelect,
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

  computed: {
    ...mapFields("source", ["selected.queries", "selected.loading"]),
  },

  methods: {
    add() {
      const value = cloneDeep(this.modelValue)
      value.push(this.selectedQuery)
      this.selectedQuery = null
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
      (vm) => [vm.selectedQuery],
      () => {
        if (!this.selectedQuery) return
        this.add()
      }
    )
  },

  data() {
    return {
      selectedQuery: null,
    }
  },
}
</script>
