<template>
  <ValidationObserver v-slot="{ invalid, validated }">
    <v-navigation-drawer v-model="showCreateEdit" app clipped right width="500">
      <template v-slot:prepend>
        <v-list-item two-line>
          <v-list-item-content>
            <v-list-item-title v-if="id" class="title"> Edit </v-list-item-title>
            <v-list-item-title v-else class="title"> New </v-list-item-title>
            <v-list-item-subtitle>Case Type</v-list-item-subtitle>
          </v-list-item-content>
          <v-btn
            icon
            color="info"
            :loading="loading"
            :disabled="invalid || !validated"
            @click="save()"
          >
            <v-icon>save</v-icon>
          </v-btn>
          <v-btn icon color="secondary" @click="closeCreateEdit()">
            <v-icon>close</v-icon>
          </v-btn>
        </v-list-item>
      </template>
      <v-card flat>
        <v-card-text>
          <v-container grid-list-md>
            <v-layout wrap>
              <v-flex xs12>
                <span class="subtitle-2">Details</span>
              </v-flex>
              <v-flex xs12>
                <ValidationProvider name="Name" rules="required" immediate>
                  <v-text-field
                    v-model="name"
                    slot-scope="{ errors, valid }"
                    :error-messages="errors"
                    :success="valid"
                    label="Name"
                    hint="A name for your case type."
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
                    label="Description"
                    :error-messages="errors"
                    :success="valid"
                    hint="A description for your case type."
                    clearable
                    required
                  />
                </ValidationProvider>
              </v-flex>
              <v-flex xs12>
                <v-select
                  v-model="visibility"
                  label="Visibility"
                  :items="visibilities"
                  hint="A visibility for your case type"
                  clearable
                />
              </v-flex>
              <v-flex xs12>
                <ValidationObserver disabled>
                  <template-select
                    :project="project"
                    label="Case Template"
                    v-model="case_template_document"
                    resource-type="dispatch-case-document-template"
                  />
                </ValidationObserver>
              </v-flex>
              <v-flex xs12>
                <ValidationObserver disabled>
                  <service-select
                    :project="project"
                    label="Oncall Service"
                    v-model="oncall_service"
                  />
                </ValidationObserver>
              </v-flex>
              <v-flex xs12>
                <ValidationObserver disabled>
                  <incident-type-select label="Incident Type" v-model="incident_type" />
                </ValidationObserver>
              </v-flex>
              <v-flex xs 12>
                <v-checkbox
                  v-model="exclude_from_metrics"
                  label="Exclude From Metrics"
                  hint="Check if this case type should be excluded from all metrics."
                />
              </v-flex>
              <v-flex xs12>
                <v-checkbox
                  v-model="default_case_type"
                  label="Default Case Type"
                  hint="Check this if this case type should be the default."
                />
              </v-flex>
              <v-flex xs12>
                <v-checkbox
                  v-model="enabled"
                  label="Enabled"
                  hint="Determines whether this case type is availible for new cases."
                />
              </v-flex>
              <v-flex xs12>
                <plugin-metadata-input v-model="plugin_metadata" :project="project" />
              </v-flex>
            </v-layout>
          </v-container>
        </v-card-text>
      </v-card>
    </v-navigation-drawer>
  </ValidationObserver>
</template>

<script>
import { ValidationObserver, ValidationProvider, extend } from "vee-validate"
import { mapActions } from "vuex"
import { mapFields } from "vuex-map-fields"
import { required } from "vee-validate/dist/rules"

import IncidentTypeSelect from "@/incident/type/IncidentTypeSelect.vue"
import PluginMetadataInput from "@/plugin/PluginMetadataInput.vue"
import ServiceSelect from "@/service/ServiceSelect.vue"
import TemplateSelect from "@/document/template/TemplateSelect.vue"

extend("required", {
  ...required,
  message: "This field is required",
})

export default {
  name: "CaseTypeNewEditSheet",

  components: {
    IncidentTypeSelect,
    PluginMetadataInput,
    ServiceSelect,
    TemplateSelect,
    ValidationObserver,
    ValidationProvider,
  },

  data() {
    return {
      visibilities: ["Open", "Restricted"],
    }
  },

  computed: {
    ...mapFields("case_type", [
      "dialogs.showCreateEdit",
      "selected.case_template_document",
      "selected.default",
      "selected.description",
      "selected.enabled",
      "selected.exclude_from_metrics",
      "selected.id",
      "selected.incident_type",
      "selected.loading",
      "selected.name",
      "selected.oncall_service",
      "selected.plugin_metadata",
      "selected.project",
      "selected.slug",
      "selected.visibility",
    ]),
    ...mapFields("case_type", {
      default_case_type: "selected.default",
    }),
    ...mapFields("route", ["query"]),
  },

  methods: {
    ...mapActions("case_type", ["save", "closeCreateEdit"]),
  },
  created() {
    if (this.query.project) {
      this.project = { name: this.query.project }
    }
  },
}
</script>
