<template>
  <v-container grid-list-md>
    <v-layout wrap>
      <v-flex xs12>
        <ValidationProvider name="Name" rules="required" immediate>
          <v-text-field
            v-model="source.name"
            slot-scope="{ errors, valid }"
            :error-messages="errors"
            :success="valid"
            label="Name"
            hint="Name of data source."
            clearable
            required
          />
        </ValidationProvider>
      </v-flex>
      <v-flex xs12>
        <ValidationProvider name="Description" rules="required" immediate>
          <v-textarea
            v-model="source.description"
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
      <v-flex xs6>
        <status-select v-model="source.status" />
      </v-flex>
      <v-flex xs6>
        <project-select v-model="source.project" />
      </v-flex>
      <v-flex xs6>
        <environment-select v-model="source.environment" />
      </v-flex>
      <v-flex xs6> <service-select label="Owner" v-model="source.owner" /> </v-flex>
      <!--
      <v-flex xs6>
        <source-type-select v-model="source.source_type" />
      </v-flex>
      <v-flex xs6>
        <transport-select v-model="source.transport" />
      </v-flex>
      <v-flex xs6>
        <data-format-select v-model="source.data_format" />
      </v-flex>
      -->
      <v-flex xs6>
        <v-text-field
          v-model.number="source.sampling_rate"
          label="Sampling Rate"
          hint="The data source's sample rate (as a percentage) as a rate between 1 and 100 (100 representing no sampling)"
        />
      </v-flex>
      <v-flex xs6>
        <v-text-field
          v-model.number="source.retention"
          label="Retention"
          hint="The data source's current retention in days."
        />
      </v-flex>
      <v-flex xs6>
        <v-text-field
          v-model.number="source.delay"
          label="Delay"
          hint="The delay better event time and when the data is available in source (in minutes)."
        />
      </v-flex>
      <v-flex xs6>
        <v-text-field
          v-model.number="source.size"
          label="Size"
          hint="The data source's current size."
        />
      </v-flex>
      <v-flex xs6>
        <v-text-field
          v-model.number="source.external_id"
          label="External ID"
          hint="The data source's external ID, this will be used to fetch data about the source automatically."
        />
      </v-flex>
      <v-flex xs6>
        <v-checkbox
          v-model="source.aggregated"
          label="Aggregated"
          hint="If the data source is an aggregation of many data sources."
        />
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { ValidationProvider, extend } from "vee-validate"
import { required } from "vee-validate/dist/rules"

import ServiceSelect from "@/service/ServiceSelect.vue"
import ProjectSelect from "@/project/ProjectSelect.vue"
//import StatusSelect from "@/data/source/StatusSelect.vue"
//import SourceTypeSelect from "@/data/source/SourceTypeSelect.vue"
//import TransportSelect from "@/data/source/TransportSelect.vue"
//import DataFormatSelect from "@/data/source/DataFormatSelect.vue"
import EnvironmentSelect from "@/data/source/environment/Select.vue"

extend("required", {
  ...required,
  message: "This field is required",
})

export default {
  name: "SourceDetailsTab",

  components: {
    ValidationProvider,
    ServiceSelect,
    ProjectSelect,
    //StatusSelect,
    //SourceTypeSelect,
    //TransportSelect,
    //DataFormatSelect,
    EnvironmentSelect,
  },

  computed: {
    ...mapFields("source", ["selected.source", "selected.loading"]),
  },

  data() {
    return {}
  },
}
</script>
