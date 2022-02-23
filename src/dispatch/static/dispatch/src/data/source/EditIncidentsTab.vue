<template>
  <v-container grid-list-md>
    <incident-select v-model="selectedIncident" :project="project" />
    <v-list>
      <v-list-item v-for="(i, idx) in value" :key="i.id">
        <v-list-item-content>
          <v-list-item-title>
            {{ i.name }}
          </v-list-item-title>
          <v-list-item-subtitle>
            {{ i.title }}
          </v-list-item-subtitle>
        </v-list-item-content>
        <v-list-item-action>
          <v-btn icon @click="remove(idx)">
            <v-icon> mdi-delete </v-icon>
          </v-btn>
        </v-list-item-action>
      </v-list-item>
    </v-list>
  </v-container>
</template>

<script>
import IncidentSelect from "@/incident/IncidentSelect.vue"

export default {
  name: "SourceEditIncidentsTab",

  components: {
    IncidentSelect,
  },

  props: {
    value: {
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
      this.value.push(this.selectedIncident)
      this.selectedIncident = null
    },
    remove(idx) {
      this.value.splice(idx, 1)
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
