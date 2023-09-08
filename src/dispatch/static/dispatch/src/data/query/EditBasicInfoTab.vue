<template>
  <v-container grid-list-md>
    <v-layout wrap>
      <v-flex xs12>
        <v-text-field
          v-model="name"
          label="Name"
          hint="Name of query."
          clearable
          required
          name="Name"
          :rules="[rules.required]"
        />
      </v-flex>
      <v-flex xs12>
        <v-textarea
          v-model="description"
          label="Description"
          hint="Description of query."
          clearable
          required
          name="Description"
          :rules="[rules.required]"
        />
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
import { required } from "@/util/form"
import { mapFields } from "vuex-map-fields"

import TagFilterAutoComplete from "@/tag/TagFilterAutoComplete.vue"
import ProjectSelect from "@/project/ProjectSelect.vue"
import SourceSelect from "@/data/source/SourceSelect.vue"

export default {
  setup() {
    return {
      rules: { required },
    }
  },
  name: "QueryDetailsTab",

  components: {
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
