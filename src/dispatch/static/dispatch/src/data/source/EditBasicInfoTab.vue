<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-text-field
          v-model="name"
          label="Name"
          hint="Name of data source."
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
          hint="Description of data source."
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
        <status-select v-model="source_status" :project="project" />
      </v-col>
      <v-col cols="12">
        <service-select label="Owner" v-model="owner" :project="project" />
      </v-col>
      <v-col cols="12">
        <environment-select v-model="source_environment" :project="project" />
      </v-col>
      <v-col cols="12">
        <transport-select v-model="source_transport" :project="project" />
      </v-col>
      <v-col cols="12">
        <type-select v-model="source_type" :project="project" />
      </v-col>
      <v-col cols="12">
        <data-format-select v-model="source_data_format" :project="project" />
      </v-col>
      <v-col cols="12">
        <v-text-field
          v-model.number="sampling_rate"
          label="Sampling Rate"
          hint="The data source's sample rate (as a percentage) as a rate between 1 and 100 (100 representing no sampling)"
        />
      </v-col>
      <v-col cols="12">
        <v-text-field
          v-model.number="retention"
          label="Retention"
          hint="The data source's current retention in days."
        />
      </v-col>
      <v-col cols="12">
        <v-text-field
          v-model.number="delay"
          label="Delay"
          hint="The delay better event time and when the data is available in source (in minutes)."
        />
      </v-col>
      <v-col cols="12">
        <v-text-field v-model.number="size" label="Size" hint="The data source's current size." />
      </v-col>
      <v-col cols="12">
        <v-text-field
          v-model.number="external_id"
          label="External ID"
          hint="The data source's external ID, this will be used to fetch data about the source automatically."
        />
      </v-col>
      <v-col cols="12">
        <tag-filter-auto-complete
          label="Tags"
          v-model="tags"
          model="source"
          :project="project"
          :model-id="id"
        />
      </v-col>
      <v-col cols="12">
        <v-checkbox
          v-model="aggregated"
          label="Aggregated"
          hint="If the data source is an aggregation of many data sources."
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { required } from "@/util/form"
import { mapFields } from "vuex-map-fields"

import ServiceSelect from "@/service/ServiceSelect.vue"
import TagFilterAutoComplete from "@/tag/TagPicker.vue"
import ProjectSelect from "@/project/ProjectSelect.vue"
import EnvironmentSelect from "@/data/source/environment/EnvironmentSelect.vue"
import StatusSelect from "@/data/source/status/StatusSelect.vue"
import DataFormatSelect from "@/data/source/dataFormat/DataFormatSelect.vue"
import TransportSelect from "@/data/source/transport/TransportSelect.vue"
import TypeSelect from "@/data/source/type/TypeSelect.vue"

export default {
  setup() {
    return {
      rules: { required },
    }
  },
  name: "SourceDetailsTab",

  components: {
    ServiceSelect,
    TagFilterAutoComplete,
    ProjectSelect,
    EnvironmentSelect,
    StatusSelect,
    DataFormatSelect,
    TransportSelect,
    TypeSelect,
  },

  computed: {
    ...mapFields("source", [
      "selected.id",
      "selected.name",
      "selected.description",
      "selected.size",
      "selected.delay",
      "selected.owner",
      "selected.retention",
      "selected.external_id",
      "selected.aggregated",
      "selected.sampling_rate",
      "selected.project",
      "selected.tags",
      "selected.source_environment",
      "selected.source_status",
      "selected.source_transport",
      "selected.source_data_format",
      "selected.source_type",
      "selected.loading",
    ]),
  },

  data() {
    return {}
  },
}
</script>
