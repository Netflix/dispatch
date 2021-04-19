<template>
  <v-container grid-list-md>
    <v-layout wrap>
      <v-flex xs12>
        <ValidationProvider name="Title" rules="required" immediate>
          <v-text-field
            v-model="title"
            slot-scope="{ errors, valid }"
            :error-messages="errors"
            :success="valid"
            label="Title"
            hint="Title of incident."
            clearable
            required
          />
        </ValidationProvider>
      </v-flex>
      <v-flex xs12>
        <ValidationProvider name="Description" rules="required" immediate>
          <v-textarea
            v-model="description"
            slot-scope="{ errors, valid }"
            :error-messages="errors"
            :success="valid"
            label="Description"
            hint="Description of incident."
            clearable
            required
          />
        </ValidationProvider>
      </v-flex>
      <v-flex xs12>
        <project-select v-model="project" />
      </v-flex>
      <v-flex xs6>
        <v-select
          v-model="status"
          label="Status"
          :items="statuses"
          hint="The incident's current status"
        />
      </v-flex>
      <v-flex xs6>
        <v-select
          v-model="visibility"
          label="Visibility"
          :items="visibilities"
          hint="The incident's current's visibilty"
        />
      </v-flex>
      <v-flex xs6>
        <incident-type-select v-model="incident_type" :project="project" />
      </v-flex>
      <v-flex xs6>
        <incident-priority-select v-model="incident_priority" :project="project" />
      </v-flex>
      <v-flex xs6>
        <ValidationProvider name="Commander" rules="required" immediate>
          <participant-select
            v-model="commander"
            slot-scope="{ errors, valid }"
            label="Commander"
            :error-messages="errors"
            :success="valid"
            hint="The participant acting as incident commander."
            clearable
            required
            :project="project"
          />
        </ValidationProvider>
      </v-flex>
      <v-flex xs6>
        <ValidationProvider name="Reporter" rules="required" immediate>
          <participant-select
            v-model="reporter"
            slot-scope="{ errors, valid }"
            label="Reporter"
            :error-messages="errors"
            :success="valid"
            hint="The participant who reported the incident."
            clearable
            required
            :project="project"
          />
        </ValidationProvider>
      </v-flex>
      <v-flex xs12>
        <span class="subtitle-2">Reported At</span>
      </v-flex>
      <v-flex xs12>
        <v-row>
          <v-col cols="6">
            <date-picker-menu v-model="reported_at" />
          </v-col>
          <v-col cols="6">
            <time-picker-menu v-model="reported_at" />
          </v-col>
        </v-row>
      </v-flex>
      <v-flex xs12>
        <span class="subtitle-2">Stable At</span>
      </v-flex>
      <v-flex xs12>
        <v-row>
          <v-col cols="6">
            <date-picker-menu v-model="stable_at" />
          </v-col>
          <v-col cols="6">
            <time-picker-menu v-model="stable_at" />
          </v-col>
        </v-row>
      </v-flex>
      <v-flex xs12>
        <tag-filter-combobox label="Tags" v-model="tags" model="incident" :model-id="id" />
      </v-flex>
      <v-flex xs12>
        <incident-filter-combobox label="Duplicates" v-model="duplicates" :project="project" />
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { ValidationProvider, extend } from "vee-validate"
import { required } from "vee-validate/dist/rules"
import ProjectSelect from "@/project/ProjectSelect.vue"
import IncidentPrioritySelect from "@/incident_priority/IncidentPrioritySelect.vue"
import IncidentTypeSelect from "@/incident_type/IncidentTypeSelect.vue"
import DatePickerMenu from "@/components/DatePickerMenu.vue"
import TimePickerMenu from "@/components/TimePickerMenu.vue"
import TagFilterCombobox from "@/tag/TagFilterCombobox.vue"
import IncidentFilterCombobox from "@/incident/IncidentFilterCombobox.vue"
import ParticipantSelect from "@/incident/ParticipantSelect.vue"

extend("required", {
  ...required,
  message: "This field is required",
})

export default {
  name: "IncidentDetailsTab",

  components: {
    ValidationProvider,
    IncidentPrioritySelect,
    IncidentTypeSelect,
    ParticipantSelect,
    TagFilterCombobox,
    IncidentFilterCombobox,
    ProjectSelect,
    TimePickerMenu,
    DatePickerMenu,
  },

  data() {
    return {
      statuses: ["Active", "Stable", "Closed"],
      visibilities: ["Open", "Restricted"],
    }
  },

  computed: {
    ...mapFields("incident", [
      "selected.id",
      "selected.name",
      "selected.title",
      "selected.description",
      "selected.commander",
      "selected.reporter",
      "selected.created_at",
      "selected.stable_at",
      "selected.reported_at",
      "selected.status",
      "selected.terms",
      "selected.tags",
      "selected.project",
      "selected.incident_priority",
      "selected.incident_type",
      "selected.duplicates",
      "selected.visibility",
    ]),
  },
}
</script>
