<template>
  <v-form @submit.prevent>
    <v-container>
      <v-row>
        <v-col cols="12">
          <v-textarea
            v-model="title"
            label="Title"
            hint="A brief explanatory title. You can change this later."
            clearable
            auto-grow
            rows="2"
            required
            name="Title"
            :rules="[rules.required]"
          />
        </v-col>
        <v-col cols="12">
          <v-textarea
            v-model="description"
            label="Description"
            hint="A summary of what you know so far. It's all right if this is incomplete."
            clearable
            auto-grow
            rows="3"
            required
            name="Description"
            :rules="[rules.required]"
          />
        </v-col>
        <v-col cols="12">
          <project-select v-model="project" />
        </v-col>
        <v-col cols="12">
          <incident-type-select label="Incident Type" :project="project" v-model="incident_type" />
        </v-col>
        <v-col cols="12">
          <incident-priority-select :project="project" v-model="incident_priority" />
        </v-col>
        <v-col cols="12">
          <tag-filter-auto-complete
            :project="project"
            v-model="tags"
            label="Tags"
            model="incident"
          />
        </v-col>
      </v-row>
    </v-container>
  </v-form>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { required } from "@/util/form"

import IncidentPrioritySelect from "@/incident/priority/IncidentPrioritySelect.vue"
import IncidentTypeSelect from "@/incident/type/IncidentTypeSelect.vue"
import ProjectSelect from "@/project/ProjectSelect.vue"
import TagFilterAutoComplete from "@/tag/TagPicker.vue"

export default {
  setup() {
    return {
      rules: { required },
    }
  },
  name: "ReportSubmissionForm",

  components: {
    IncidentPrioritySelect,
    IncidentTypeSelect,
    ProjectSelect,
    TagFilterAutoComplete,
  },

  props: {
    incidentType: {
      type: Object,
      default: function () {
        return {}
      },
    },
  },

  data() {
    return {
      isSubmitted: false,
    }
  },

  computed: {
    ...mapFields("incident", [
      "selected.commander",
      "selected.conference",
      "selected.conversation",
      "selected.description",
      "selected.documents",
      "selected.id",
      "selected.incident_priority",
      "selected.incident_type",
      "selected.loading",
      "selected.project",
      "selected.storage",
      "selected.tags",
      "selected.ticket",
      "selected.title",
      "selected.visibility",
    ]),
  },
}
</script>
