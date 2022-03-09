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
            hint="Title of the incident."
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
            hint="Description of the incident."
            clearable
            required
          />
        </ValidationProvider>
      </v-flex>
      <v-flex xs12>
        <v-textarea
          v-model="resolution"
          label="Resolution"
          hint="Description of the actions taken to resolve the incident."
          clearable
        />
      </v-flex>
      <v-flex xs12>
        <project-select v-model="project" />
      </v-flex>
      <v-flex xs6>
        <v-select
          v-model="status"
          label="Status"
          :items="statuses"
          hint="The status of the incident."
        />
      </v-flex>
      <v-flex xs6>
        <v-select
          v-model="visibility"
          label="Visibility"
          :items="visibilities"
          hint="The visibilty of the incident."
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
        <v-row>
          <v-col cols="6">
            <date-time-picker-menu label="Reported At" v-model="reported_at" />
          </v-col>
          <v-col cols="6">
            <date-time-picker-menu label="Stable At" v-model="stable_at" />
          </v-col>
        </v-row>
      </v-flex>
      <v-flex xs12>
        <tag-filter-auto-complete label="Tags" v-model="tags" model="incident" :model-id="id" />
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
import DateTimePickerMenu from "@/components/DateTimePickerMenu.vue"
import TagFilterAutoComplete from "@/tag/TagFilterAutoComplete.vue"
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
    TagFilterAutoComplete,
    IncidentFilterCombobox,
    ProjectSelect,
    DateTimePickerMenu,
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
      "selected.resolution",
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
