<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-text-field
          v-model="name"
          label="Name"
          hint="Name of query."
          clearable
          required
          name="Name"
          :rules="[rules.required]"
        />
      </v-col>
      <v-col cols="12">
        <v-textarea
          v-model="description"
          label="Description"
          hint="Description of query."
          clearable
          required
          name="Description"
          :rules="[rules.required]"
        />
      </v-col>
      <v-col cols="12">
        <project-select v-model="project" />
      </v-col>
      <v-col cols="12">
        <source-select v-model="source" :project="project" />
      </v-col>
      <v-col cols="12">
        <tag-filter-auto-complete
          label="Tags"
          v-model="tags"
          :project="project"
          model="query"
          :model-id="id"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { required } from "@/util/form"
import { mapFields } from "vuex-map-fields"

import TagFilterAutoComplete from "@/tag/TagPicker.vue"
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
