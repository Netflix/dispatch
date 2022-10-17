<template>
  <ValidationObserver v-slot="{}">
    <v-form>
      <v-container grid-list-md>
        <v-layout wrap>
          <v-flex xs12>
            <ValidationProvider name="Title" rules="required" immediate>
              <v-textarea
                v-model="title"
                slot-scope="{ errors, valid }"
                :error-messages="errors"
                :success="valid"
                label="Title"
                hint="A brief explanatory title. You can change this later."
                clearable
                auto-grow
                rows="2"
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
                hint="A summary of what you know so far. It's all right if this is incomplete."
                clearable
                auto-grow
                rows="3"
                required
              />
            </ValidationProvider>
          </v-flex>
          <v-flex xs12>
            <project-select v-model="project" />
          </v-flex>
          <v-flex xs12>
            <incident-type-select :project="project" v-model="incident_type" />
          </v-flex>
          <v-flex xs12>
            <incident-priority-select :project="project" v-model="incident_priority" />
          </v-flex>
          <v-flex xs12>
            <tag-filter-auto-complete :project="project" v-model="tags" label="Tags" />
          </v-flex>
        </v-layout>
      </v-container>
    </v-form>
  </ValidationObserver>
</template>

<script>
import { ValidationObserver, ValidationProvider, extend } from "vee-validate"
import { mapFields } from "vuex-map-fields"
import { required } from "vee-validate/dist/rules"

import IncidentPrioritySelect from "@/incident/priority/IncidentPrioritySelect.vue"
import IncidentTypeSelect from "@/incident/type/IncidentTypeSelect.vue"
import ProjectSelect from "@/project/ProjectSelect.vue"
import TagFilterAutoComplete from "@/tag/TagFilterAutoComplete.vue"

extend("required", {
  ...required,
  message: "This field is required",
})

export default {
  name: "ReportSubmissionForm",

  components: {
    ValidationProvider,
    ValidationObserver,
    IncidentTypeSelect,
    IncidentPrioritySelect,
    ProjectSelect,
    TagFilterAutoComplete,
  },

  data() {
    return {
      isSubmitted: false,
    }
  },

  computed: {
    ...mapFields("incident", [
      "selected.incident_priority",
      "selected.incident_type",
      "selected.commander",
      "selected.title",
      "selected.tags",
      "selected.description",
      "selected.conversation",
      "selected.conference",
      "selected.visibility",
      "selected.storage",
      "selected.documents",
      "selected.loading",
      "selected.ticket",
      "selected.project",
      "selected.id",
    ]),
    ...mapFields("route", ["query"]),
  },
}
</script>
