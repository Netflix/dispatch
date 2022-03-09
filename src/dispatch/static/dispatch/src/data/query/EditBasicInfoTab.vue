<template>
  <v-container grid-list-md>
    <v-layout wrap>
      <v-flex xs12>
        <ValidationProvider name="Name" rules="required" immediate>
          <v-text-field
            v-model="name"
            slot-scope="{ errors, valid }"
            :error-messages="errors"
            :success="valid"
            label="Name"
            hint="Name of query."
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
            hint="Description of query."
            clearable
            required
          />
        </ValidationProvider>
      </v-flex>
      <v-flex xs12>
        <project-select v-model="project" />
      </v-flex>
      <v-flex xs12>
        <source-select v-model="source" :project="project" />
      </v-flex>
      <v-flex xs12>
        <tag-filter-auto-complete
          label="Tags"
          v-model="tags"
          :project="project"
          model="query"
          :model-id="id"
        />
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { ValidationProvider, extend } from "vee-validate"
import { required } from "vee-validate/dist/rules"

import TagFilterAutoComplete from "@/tag/TagFilterAutoComplete.vue"
import ProjectSelect from "@/project/ProjectSelect.vue"
import SourceSelect from "@/data/source/SourceSelect.vue"

extend("required", {
  ...required,
  message: "This field is required",
})

export default {
  name: "QueryDetailsTab",

  components: {
    ValidationProvider,
    TagFilterAutoComplete,
    ProjectSelect,
    SourceSelect,
  },

  computed: {
    ...mapFields("query", [
      "selected.id",
      "selected.name",
      "selected.description",
      "selected.project",
      "selected.source",
      "selected.tags",
      "selected.loading",
    ]),
  },

  data() {
    return {
      editorOptions: {
        automaticLayout: true,
        renderValidationDecorations: "on",
      },
    }
  },
}
</script>
