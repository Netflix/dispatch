<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-text-field
          v-model="title"
          label="Title"
          hint="Title of the case."
          clearable
          required
          name="Title"
          :rules="[rules.required]"
        />
      </v-col>
      <v-col cols="12">
        <v-textarea
          v-model="description"
          label="Description"
          hint="Description of the case."
          clearable
          required
          name="Description"
          :rules="[rules.required]"
        />
      </v-col>
      <v-col cols="12">
        <v-select
          v-model="resolution_reason"
          label="Resolution Reason"
          :items="$store.state.case_management.resolutionReasons"
          hint="The general reason why a given case was resolved."
          :menu-props="{ contentClass: 'resolution-menu' }"
        >
          <template #item="{ item, props }">
            <v-list-item v-bind="props">
              <template #title>
                <div class="d-flex align-center justify-space-between">
                  {{ item.title }}
                  <v-tooltip location="right">
                    <template #activator="{ props: tooltipProps }">
                      <v-icon
                        v-bind="tooltipProps"
                        icon="mdi-information"
                        size="small"
                        class="ml-2"
                      />
                    </template>
                    <span>{{ $store.state.case_management.resolutionTooltips[item.title] }}</span>
                  </v-tooltip>
                </div>
              </template>
            </v-list-item>
          </template>
        </v-select>
      </v-col>
      <v-col cols="12">
        <v-textarea
          v-model="resolution"
          label="Resolution"
          hint="Description of the actions taken to resolve the case."
          clearable
        />
      </v-col>
      <v-col cols="12">
        <participant-select
          v-model="assignee"
          label="Assignee"
          hint="The organization member to which the case is assigned."
          clearable
          :project="project"
          name="Assignee"
          :rules="[only_one]"
        />
      </v-col>
      <v-col cols="12">
        <participant-select
          v-model="reporter"
          label="Reporter"
          hint="The organization member who reported the case."
          clearable
          :project="project"
          name="Reporter"
          :rules="[only_one]"
        />
      </v-col>
      <v-col cols="6">
        <project-select v-model="project" :disabled="project_disabled" />
      </v-col>
      <v-col cols="6">
        <case-type-select v-model="case_type" :project="project" />
      </v-col>
      <v-col cols="6">
        <case-severity-select v-model="case_severity" :project="project" />
      </v-col>
      <v-col cols="6">
        <case-priority-select v-model="case_priority" :project="project" />
      </v-col>
      <v-col cols="6">
        <v-select
          v-model="status"
          label="Status"
          :items="statuses"
          item-title="title"
          item-value="value"
          hint="The status of the case."
        >
          <template #item="{ item, props }">
            <div class="d-flex align-center" style="width: 100%">
              <v-list-item
                v-bind="props"
                :disabled="item.raw.value === 'Escalated'"
                style="flex-grow: 1"
              />
              <v-tooltip
                v-if="item.raw.value === 'Escalated'"
                text="Escalation is only supported on the case page or in Slack with the `/dispatch-escalate-case` command."
              >
                <template #activator="{ props: tooltipProps }">
                  <v-icon
                    v-bind="tooltipProps"
                    color="black"
                    size="small"
                    class="mr-6 flex-shrink-0"
                    style="pointer-events: auto"
                  >
                    mdi-information
                  </v-icon>
                </template>
              </v-tooltip>
            </div>
          </template>
        </v-select>
      </v-col>
      <v-col cols="6">
        <v-select
          v-model="visibility"
          label="Visibility"
          :items="visibilities"
          hint="The visibility of the case."
        />
      </v-col>
      <v-col cols="12">
        <v-row>
          <v-col cols="6">
            <date-time-picker-menu label="Reported At" v-model="reported_at" />
          </v-col>
          <v-col cols="6">
            <date-time-picker-menu label="Triage At" v-model="triage_at" />
          </v-col>
        </v-row>
      </v-col>
      <v-col cols="12">
        <v-row>
          <v-col cols="6">
            <date-time-picker-menu label="Stable At" v-model="stable_at" />
          </v-col>
          <v-col cols="6">
            <date-time-picker-menu label="Escalated At" v-model="escalated_at" />
          </v-col>
        </v-row>
      </v-col>
      <v-col cols="12">
        <v-row>
          <v-col cols="6">
            <date-time-picker-menu label="Closed At" v-model="closed_at" />
          </v-col>
        </v-row>
      </v-col>
      <v-col cols="12">
        <tag-filter-auto-complete
          label="Tags"
          v-model="tags"
          model="case"
          :model-id="id"
          :project="project"
          show-copy
          :showGenAISuggestions="true"
          modelType="case"
        />
      </v-col>
      <v-col cols="12">
        <case-filter-combobox label="Related" v-model="related" :project="project" />
      </v-col>
      <v-col cols="12">
        <case-filter-combobox label="Duplicates" v-model="duplicates" :project="project" />
      </v-col>
      <v-col cols="12">
        <incident-filter-combobox label="Incidents" v-model="incidents" :project="project" />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { required } from "@/util/form"
import { mapFields } from "vuex-map-fields"

import CaseFilterCombobox from "@/case/CaseFilterCombobox.vue"
import CasePrioritySelect from "@/case/priority/CasePrioritySelect.vue"
import CaseSeveritySelect from "@/case/severity/CaseSeveritySelect.vue"
import CaseTypeSelect from "@/case/type/CaseTypeSelect.vue"
import DateTimePickerMenu from "@/components/DateTimePickerMenu.vue"
import IncidentFilterCombobox from "@/incident/IncidentFilterCombobox.vue"
import ProjectSelect from "@/project/ProjectSelect.vue"
import ParticipantSelect from "@/components/ParticipantSelect.vue"
import TagFilterAutoComplete from "@/tag/TagPicker.vue"

export default {
  setup() {
    return {
      rules: { required },
    }
  },
  name: "CaseDetailsTab",

  components: {
    CaseFilterCombobox,
    CasePrioritySelect,
    CaseSeveritySelect,
    CaseTypeSelect,
    DateTimePickerMenu,
    IncidentFilterCombobox,
    ParticipantSelect,
    ProjectSelect,
    TagFilterAutoComplete,
  },

  data() {
    return {
      statuses: [
        { title: "New", value: "New" },
        { title: "Triage", value: "Triage" },
        { title: "Stable", value: "Stable" },
        { title: "Escalated", value: "Escalated" },
        { title: "Closed", value: "Closed" },
      ],
      visibilities: ["Open", "Restricted"],
      only_one: (value) => {
        if (value && value.length > 1) {
          return "Only one is allowed"
        }
        return true
      },
    }
  },

  computed: {
    ...mapFields("case_management", [
      "selected.assignee",
      "selected.case_priority",
      "selected.case_severity",
      "selected.case_type",
      "selected.closed_at",
      "selected.description",
      "selected.duplicates",
      "selected.escalated_at",
      "selected.id",
      "selected.incidents",
      "selected.name",
      "selected.project",
      "selected.related",
      "selected.reporter",
      "selected.reported_at",
      "selected.resolution_reason",
      "selected.resolution",
      "selected.signals",
      "selected.stable_at",
      "selected.status",
      "selected.tags",
      "selected.title",
      "selected.triage_at",
      "selected.visibility",
    ]),
    project_disabled(item) {
      return item.id != null
    },
  },
}
</script>

<style scoped>
.v-list-item--disabled {
  opacity: 0.6;
  pointer-events: none;
}

.resolution-item {
  margin-left: 12px;
  margin-bottom: 4px;
  padding: 8px 0;
}

.resolution-menu {
  max-width: 300px;
}

:deep(.v-list-item) {
  padding: 8px 16px;
}

:deep(.v-select__content) {
  max-width: 300px;
}

/* Lighten tooltip info icons */
:deep(.v-tooltip .v-icon) {
  color: #cccccc !important;
}

/* Alternative approach - target the icon directly */
:deep(.mdi-information) {
  color: #b0b0b0 !important;
}
</style>
