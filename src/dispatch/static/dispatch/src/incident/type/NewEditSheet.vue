<template>
  <v-form @submit.prevent v-slot="{ isValid }">
    <v-navigation-drawer v-model="showCreateEdit" location="right" width="500">
      <template #prepend>
        <v-list-item lines="two">
          <v-list-item-title v-if="id" class="text-h6"> Edit </v-list-item-title>
          <v-list-item-title v-else class="text-h6"> New </v-list-item-title>
          <v-list-item-subtitle>Incident Type</v-list-item-subtitle>

          <template #append>
            <v-btn
              icon
              variant="text"
              color="info"
              :loading="loading"
              :disabled="!isValid.value"
              @click="save()"
            >
              <v-icon>mdi-content-save</v-icon>
            </v-btn>
            <v-btn icon variant="text" color="secondary" @click="closeCreateEdit()">
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </template>
        </v-list-item>
      </template>
      <v-card>
        <v-card-text>
          <v-container>
            <v-row>
              <v-col cols="12">
                <span class="text-subtitle-2">Details</span>
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="name"
                  label="Name"
                  hint="A name for your incident type."
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
                  hint="A description for your incident type."
                  clearable
                  required
                  name="Description"
                  :rules="[rules.required]"
                />
              </v-col>
              <v-col cols="12">
                <v-select
                  v-model="visibility"
                  label="Visibility"
                  :items="visibilities"
                  hint="A visibility for your incident type"
                  clearable
                />
              </v-col>
              <v-col cols="12">
                <v-form @submit.prevent>
                  <template-select
                    :project="project"
                    label="Incident Template"
                    v-model="incident_template_document"
                    resource-type="dispatch-incident-document-template"
                  />
                </v-form>
              </v-col>
              <v-col cols="12">
                <v-form @submit.prevent>
                  <template-select
                    :project="project"
                    label="Executive Template"
                    v-model="executive_template_document"
                    resource-type="dispatch-executive-report-document-template"
                  />
                </v-form>
              </v-col>
              <v-col cols="12">
                <v-form @submit.prevent>
                  <template-select
                    :project="project"
                    label="Review Template"
                    v-model="review_template_document"
                    resource-type="dispatch-incident-review-document-template"
                  />
                </v-form>
              </v-col>
              <v-col cols="12">
                <v-form @submit.prevent>
                  <template-select
                    :project="project"
                    label="Tracking Template"
                    v-model="tracking_template_document"
                    resource-type="dispatch-incident-tracking-template"
                  />
                </v-form>
              </v-col>
              <v-col cols="12">
                <cost-model-combobox
                  :project="project"
                  v-model="cost_model"
                  persistent-hint
                  clearable
                  hint="If unassigned, the incident cost calculation defaults to the classic incident cost model."
                />
              </v-col>
              <v-col cols="12">
                <v-checkbox
                  v-model="exclude_from_metrics"
                  label="Exclude From Metrics"
                  hint="Check if this incident type should be excluded from all metrics."
                />
              </v-col>
              <v-col cols="12">
                <v-checkbox
                  v-model="default_incident_type"
                  label="Default Incident Type"
                  hint="Check this if this incident type should be the default."
                />
              </v-col>
              <v-col cols="12">
                <v-checkbox
                  v-model="enabled"
                  label="Enabled"
                  hint="Determines whether this incident type is availible for new incidents."
                />
              </v-col>
              <v-col cols="12">
                <v-textarea
                  v-model="channel_description"
                  label="Channel description"
                  hint="Set this as the description for new incident channels."
                  clearable
                />
              </v-col>
              <v-col cols="12">
                <span class="text-body-1 text-medium-emphasis mt-2">
                  Use {oncall_email} in the description to replace with this oncall email
                  (optional).
                </span>
                <service-select
                  label="Oncall Service"
                  :project="project"
                  v-model="description_service"
                />
              </v-col>
              <v-col cols="12">
                <plugin-metadata-input v-model="plugin_metadata" :project="project" />
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
      </v-card>
    </v-navigation-drawer>
  </v-form>
</template>

<script>
import { required } from "@/util/form"

import { mapActions } from "vuex"
import { mapFields } from "vuex-map-fields"

import CostModelCombobox from "@/cost_model/CostModelCombobox.vue"
import PluginMetadataInput from "@/plugin/PluginMetadataInput.vue"
import TemplateSelect from "@/document/template/TemplateSelect.vue"
import ServiceSelect from "@/service/ServiceSelect.vue"

export default {
  setup() {
    return {
      rules: { required },
    }
  },
  name: "IncidentTypeNewEditSheet",

  components: {
    CostModelCombobox,
    PluginMetadataInput,
    TemplateSelect,
    ServiceSelect,
  },

  data() {
    return {
      visibilities: ["Open", "Restricted"],
    }
  },

  computed: {
    ...mapFields("incident_type", [
      "dialogs.showCreateEdit",
      "selected.commander_service",
      "selected.liaison_service",
      "selected.description",
      "selected.id",
      "selected.project",
      "selected.loading",
      "selected.name",
      "selected.slug",
      "selected.incident_template_document",
      "selected.tracking_template_document",
      "selected.review_template_document",
      "selected.executive_template_document",
      "selected.plugin_metadata",
      "selected.visibility",
      "selected.enabled",
      "selected.cost_model",
      "selected.exclude_from_metrics",
      "selected.default",
      "selected.channel_description",
      "selected.description_service",
    ]),
    ...mapFields("incident_type", {
      default_incident_type: "selected.default",
    }),
  },

  methods: {
    ...mapActions("incident_type", ["save", "closeCreateEdit"]),
  },
  created() {
    if (this.$route.query.project) {
      this.project = { name: this.$route.query.project }
    }
  },
}
</script>
