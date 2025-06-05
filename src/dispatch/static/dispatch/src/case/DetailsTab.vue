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
          :items="resolutionReasons"
          hint="The general reason why a given case was resolved."
        />
      </v-col>
      <v-col cols="12">
        <v-label class="mb-2">Resolution</v-label>
        <v-card flat color="grey-lighten-5" class="rounded-lg">
          <RichEditor
            :content="resolution"
            @update:model-value="(newValue) => (resolution = newValue)"
            placeholder="Description of the actions taken to resolve the case..."
            style="min-height: 200px; margin: 10px; font-size: 0.9125rem; font-weight: 400"
          />
        </v-card>
        <v-messages
          :value="['Description of the actions taken to resolve the case.']"
          class="v-messages--hint"
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
            <date-time-picker-menu label="Escalated At" v-model="escalated_at" />
          </v-col>
          <v-col cols="6">
            <date-time-picker-menu label="Closed At" v-model="closed_at" />
          </v-col>
        </v-row>
      </v-col>
      <v-col cols="12">
        <case-filter-combobox v-model="related" label="Related" />
      </v-col>
      <v-col cols="12">
        <case-filter-combobox v-model="duplicates" label="Duplicates" />
      </v-col>
      <v-col cols="12">
        <incident-filter-combobox v-model="incidents" label="Incidents" />
      </v-col>
      <v-col cols="12">
        <tag-filter-auto-complete v-model="tags" label="Tags" model="case" :project="project" />
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
import ParticipantSelect from "@/components/ParticipantSelect.vue"
import ProjectSelect from "@/project/ProjectSelect.vue"
import RichEditor from "@/components/RichEditor.vue"
import TagFilterAutoComplete from "@/tag/TagFilterAutoComplete.vue"

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
    RichEditor,
    TagFilterAutoComplete,
  },

  data() {
    return {
      statuses: [
        { title: "New", value: "New" },
        { title: "Triage", value: "Triage" },
        { title: "Escalated", value: "Escalated" },
        { title: "Closed", value: "Closed" },
      ],
      visibilities: ["Open", "Restricted"],
      resolutionReasons: ["False Positive", "User Acknowledged", "Mitigated", "Escalated"],
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
</style>
