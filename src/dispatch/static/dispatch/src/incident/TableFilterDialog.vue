<template>
  <v-dialog v-model="display" max-width="600px">
    <template v-slot:activator="{ on }">
      <v-badge :value="numFilters" bordered overlap :content="numFilters">
        <v-btn color="secondary" dark v-on="on">Filter Columns</v-btn>
      </v-badge>
    </template>
    <v-card>
      <v-card-title>
        <span class="headline">Column Filters</span>
      </v-card-title>
      <v-list dense>
        <!--
          <v-list-item>
            <v-list-item-content>
              <individual-combobox v-model="commander" label="Commanders"></individual-combobox>
            </v-list-item-content>
          </v-list-item>
          <v-list-item>
            <v-list-item-content>
              <individual-combobox v-model="reporter" label="Reporters"></individual-combobox>
            </v-list-item-content>
          </v-list-item>
          -->
        <v-list-item>
          <v-list-item-content>
            <tag-filter-combobox v-model="tag" label="Tags" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <incident-type-combobox v-model="incident_type" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <incident-priority-combobox v-model="incident_priority" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <incident-status-multi-select v-model="status" />
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-card>
  </v-dialog>
</template>

<script>
import { sum } from "lodash"
import { mapFields } from "vuex-map-fields"
import IncidentStatusMultiSelect from "@/incident/IncidentStatusMultiSelect.vue"
// import IndividualCombobox from "@/individual/IndividualCombobox.vue"
import TagFilterCombobox from "@/tag/TagFilterCombobox.vue"
import IncidentTypeCombobox from "@/incident_type/IncidentTypeCombobox.vue"
import IncidentPriorityCombobox from "@/incident_priority/IncidentPriorityCombobox.vue"

export default {
  name: "IncidentTableFilterDialog",

  components: {
    // IndividualCombobox,
    TagFilterCombobox,
    IncidentTypeCombobox,
    IncidentPriorityCombobox,
    IncidentStatusMultiSelect
  },

  data() {
    return {
      display: false
    }
  },

  computed: {
    ...mapFields("incident", [
      "table.options.filters.commander",
      "table.options.filters.reporter",
      "table.options.filters.incident_type",
      "table.options.filters.incident_priority",
      "table.options.filters.status",
      "table.options.filters.tag"
    ]),
    numFilters: function() {
      return sum([
        this.reporter.length,
        this.commander.length,
        this.incident_type.length,
        this.incident_priority.length,
        this.tag.length,
        this.status.length
      ])
    }
  }
}
</script>
