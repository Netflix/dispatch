<template>
  <v-dialog v-model="display" max-width="600px">
    <template v-slot:activator="{ on }">
      <v-badge :value="numFilters" bordered overlap color="info" :content="numFilters">
        <v-btn color="secondary" v-on="on"> Filter </v-btn>
      </v-badge>
    </template>
    <v-card>
      <v-card-title>
        <span class="headline">Column Filters</span>
      </v-card-title>
      <v-list dense>
        <v-list-item>
          <v-list-item-content>
            <incident-window-input v-model="reported_at" label="Reported At" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <project-combobox v-model="project" label="Projects" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <incident-status-multi-select v-model="status" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <incident-priority-combobox v-model="incident_priority" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <incident-type-combobox v-model="incident_type" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <tag-filter-combobox v-model="tag" label="Tags" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <tag-type-filter-combobox v-model="tag_type" label="Tag Types" />
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
import TagFilterCombobox from "@/tag/TagFilterCombobox.vue"
import IncidentTypeCombobox from "@/incident_type/IncidentTypeCombobox.vue"
import IncidentPriorityCombobox from "@/incident_priority/IncidentPriorityCombobox.vue"
import TagTypeFilterCombobox from "@/tag_type/TagTypeFilterCombobox.vue"
import ProjectCombobox from "@/project/ProjectCombobox.vue"
import IncidentWindowInput from "@/incident/IncidentWindowInput.vue"

export default {
  name: "IncidentTableFilterDialog",

  components: {
    TagFilterCombobox,
    IncidentTypeCombobox,
    IncidentPriorityCombobox,
    TagTypeFilterCombobox,
    ProjectCombobox,
    IncidentStatusMultiSelect,
    IncidentWindowInput,
  },

  data() {
    return {
      display: false,
    }
  },

  computed: {
    ...mapFields("incident", [
      "table.options.filters.commander",
      "table.options.filters.reported_at",
      "table.options.filters.reporter",
      "table.options.filters.incident_type",
      "table.options.filters.incident_priority",
      "table.options.filters.tag_type",
      "table.options.filters.project",
      "table.options.filters.status",
      "table.options.filters.tag",
    ]),
    numFilters: function () {
      return sum([
        this.reporter.length,
        this.commander.length,
        this.incident_type.length,
        this.incident_priority.length,
        this.project.length,
        this.tag.length,
        this.tag_type.length,
        this.status.length,
      ])
    },
  },
}
</script>
