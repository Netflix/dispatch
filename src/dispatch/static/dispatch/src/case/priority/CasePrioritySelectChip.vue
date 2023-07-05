<template>
  <v-menu offset-y>
    <template v-slot:activator="{ on, attrs }">
      <v-chip
        v-bind="attrs"
        v-on="on"
        small
        class="mr-2 hover-outline"
        :text-color="getPriorityMetaColor(_case.case_priority)"
        :color="getPriorityColor(_case.case_priority)"
      >
        <v-icon dense small class="pr-2" :color="getPriorityMetaColor(_case.case_priority)">
          mdi-alert-plus-outline
        </v-icon>
        <b>{{ _case.case_priority.name }}</b>
      </v-chip>
    </template>
    <v-list>
      <v-list-item
        v-for="(priority, index) in priorities"
        :key="index"
        @click="changePriority(priority)"
      >
        {{ priority }}
      </v-list-item>
    </v-list>
  </v-menu>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

export default {
  name: "CasePrioritySelectChip",

  props: {
    _case: {
      type: Object,
      required: false,
      default: () => ({}), // returns an empty object if _case is not provided
    },
  },

  data() {
    return {
      priorities: ["High", "Medium", "Low"],
    }
  },

  methods: {
    ...mapActions("case_management", ["save_page"]),
    changePriority(priority) {
      this._case.case_priority.name = priority // Update the selected priority.
      this.save_page()
      // Here, you may want to call an API to update the priority in the backend.
      // this.updateCasePriority(this.selected.case_priority);
    },
    getPriorityColor(priority) {
      if (priority) {
        switch (priority.name) {
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
    getPriorityMetaColor(priority) {
      console.log("Got priority %O", priority.name)

      if (priority) {
        switch (priority.name) {
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
