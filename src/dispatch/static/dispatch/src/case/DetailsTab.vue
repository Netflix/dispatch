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
            hint="Title of the case."
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
            hint="Description of the case."
            clearable
            required
          />
        </ValidationProvider>
      </v-flex>
      <v-flex xs12>
        <v-textarea
          v-model="resolution"
          label="Resolution"
          hint="Description of the actions taken to resolve the case."
          clearable
        />
      </v-flex>
      <v-flex xs6>
        <v-select
          v-model="status"
          label="Status"
          :items="statuses"
          hint="The status of the case."
        />
      </v-flex>
      <v-flex xs6>
        <v-select
          v-model="visibility"
          label="Visibility"
          :items="visibilities"
          hint="The visibilty of the case."
        />
      </v-flex>
      <v-flex xs6>
        <project-select v-model="project" />
      </v-flex>
      <v-flex xs6>
        <source-select v-model="source" :project="project" />
      </v-flex>
      <v-flex xs12>
        <ValidationProvider name="Assignee" rules="required" immediate>
          <organization-member-combobox
            v-model="assignee"
            slot-scope="{ errors, valid }"
            label="Assignee"
            :error-messages="errors"
            :success="valid"
            hint="The organization member to which the case is assigned."
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
        <tag-filter-auto-complete label="Tags" v-model="tags" model="case" :model-id="id" />
      </v-flex>
      <v-flex xs12>
        <case-filter-combobox label="Duplicates" v-model="duplicates" :project="project" />
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { ValidationProvider, extend } from "vee-validate"
import { required } from "vee-validate/dist/rules"

import CaseFilterCombobox from "@/case/CaseFilterCombobox.vue"
import DateTimePickerMenu from "@/components/DateTimePickerMenu.vue"
import OrganizationMemberCombobox from "@/organization/OrganizationMemberCombobox.vue"
import ProjectSelect from "@/project/ProjectSelect.vue"
import SourceSelect from "@/data/source/SourceSelect.vue"
import TagFilterAutoComplete from "@/tag/TagFilterAutoComplete.vue"

extend("required", {
  ...required,
  message: "This field is required",
})

export default {
  name: "CaseDetailsTab",

  components: {
    CaseFilterCombobox,
    DateTimePickerMenu,
    OrganizationMemberCombobox,
    ProjectSelect,
    SourceSelect,
    TagFilterAutoComplete,
    ValidationProvider,
  },

  data() {
    return {
      statuses: ["Active", "Stable", "Closed"],
      visibilities: ["Open", "Restricted"],
    }
  },

  computed: {
    ...mapFields("case_management", [
      "selected.id",
      "selected.name",
      "selected.title",
      "selected.description",
      "selected.resolution",
      "selected.assignee",
      "selected.source",
      "selected.created_at",
      "selected.stable_at",
      "selected.reported_at",
      "selected.status",
      "selected.tags",
      "selected.project",
      "selected.duplicates",
      "selected.visibility",
    ]),
  },
}
</script>
