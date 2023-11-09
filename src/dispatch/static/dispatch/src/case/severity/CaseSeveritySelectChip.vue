<template>
  <v-menu offset-y>
    <template v-slot:activator="{ on, attrs }">
      <v-chip
        v-bind="attrs"
        v-on="on"
        small
        class="mr-2 hover-outline"
        :text-color="getSeverityMetaColor(_case.case_severity)"
        :color="getSeverityColor(_case.case_severity)"
      >
        <v-icon dense small class="pr-2" :color="getSeverityMetaColor(_case.case_severity)">
          mdi-alert-plus-outline
        </v-icon>
        <b>{{ _case.case_severity.name }}</b>
      </v-chip>
    </template>
    <v-list>
      <v-list-item
        v-for="(severity, index) in severities"
        :key="index"
        @click="changeSeverity(severity)"
      >
        {{ severity }}
      </v-list-item>
    </v-list>
  </v-menu>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
export default {
  name: "CaseSeveritySelectChip",
  props: {
    _case: {
      type: Object,
      required: false,
      default: () => ({}), // returns an empty object if _case is not provided
    },
  },
  data() {
    return {
      severities: ["Critical", "High", "Medium", "Low"],
    }
  },
  methods: {
    ...mapActions("case_management", ["save_page"]),
    changeSeverity(severity) {
      this._case.case_severity.name = severity // Update the selected severity.
      this.save_page()
      // Here, you may want to call an API to update the severity in the backend.
      // this.updateCaseSeverity(this.selected.case_priority);
    },
    getSeverityColor(severity) {
      if (severity) {
        switch (severity.name) {
          case "Low":
            return "green lighten-5"
          case "Medium":
            return "orange lighten-5"
          case "High":
            return "red lighten-5"
          case "Critical":
            return "red lighten-5"
        }
      }
      return "red darken-2"
    },
    getSeverityMetaColor(severity) {
      console.log("Got severity %O", severity.name)
      if (severity) {
        switch (severity.name) {
          case "Low":
            return "green"
          case "Medium":
            return "orange"
          case "High":
            return "red"
          case "Critical":
            return "red"
        }
      }
      return "green"
    },
  },
}
</script>

<style scoped>
.hover-outline:hover {
  border: 1px dashed rgba(148, 148, 148, 0.87) !important;
  border-radius: 20px;
}
</style>
