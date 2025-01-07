<template>
  <v-form @submit.prevent v-slot="{ isValid }">
    <v-navigation-drawer v-model="showCreateEdit" location="right" width="500">
      <template #prepend>
        <v-list-item lines="two">
          <v-list-item-title v-if="id" class="text-h6"> Edit </v-list-item-title>
          <v-list-item-title v-else class="text-h6"> New </v-list-item-title>
          <v-list-item-subtitle>Case Type</v-list-item-subtitle>

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
                  hint="A name for your case type."
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
                  hint="A description for your case type."
                  clearable
                  required
                  name="Description"
                  :rules="[rules.required]"
                />
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="conversation_target"
                  label="Conversation Target"
                  hint="The conversation identifier that new case messages will be sent to."
                  clearable
                  name="ConversationTarget"
                />
              </v-col>
              <v-col cols="12">
                <v-select
                  v-model="visibility"
                  label="Visibility"
                  :items="visibilities"
                  hint="A visibility for your case type"
                  clearable
                />
              </v-col>
              <v-col cols="12">
                <v-form @submit.prevent>
                  <template-select
                    :project="project"
                    label="Case Template"
                    v-model="case_template_document"
                    resource-type="dispatch-case-document-template"
                  />
                </v-form>
              </v-col>
              <v-col cols="12">
                <v-form @submit.prevent>
                  <service-select
                    :project="project"
                    label="Oncall Service"
                    v-model="oncall_service"
                  />
                </v-form>
              </v-col>
              <v-col cols="12">
                <cost-model-combobox
                  v-if="experimental_features"
                  :project="project"
                  v-model="cost_model"
                  persistent-hint
                  clearable
                  hint="If unassigned, the case cost is not calculated."
                />
              </v-col>
              <v-col cols="6">
                <project-select label="Incident Project" v-model="incidentProject" />
              </v-col>
              <v-col cols="6">
                <v-form @submit.prevent>
                  <incident-type-select
                    label="Incident Type"
                    :project="incidentProject"
                    v-model="incident_type"
                  />
                </v-form>
              </v-col>
              <v-col cols="12">
                <v-checkbox
                  v-model="enabled"
                  label="Enabled"
                  hint="Determines whether this case type is available for new cases."
                />
              </v-col>
              <v-col cols="12">
                <v-checkbox
                  v-model="default_case_type"
                  label="Default Case Type"
                  hint="Check this if this case type should be the default."
                />
              </v-col>
              <v-col cols="12">
                <v-checkbox
                  v-model="auto_close"
                  label="Auto Close"
                  hint="Check this if the case should be automatically closed after being created."
                />
              </v-col>
              <v-col cols="12">
                <v-checkbox
                  v-model="exclude_from_metrics"
                  label="Exclude From Metrics"
                  hint="Check if this case type should be excluded from all metrics."
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
import IncidentTypeSelect from "@/incident/type/IncidentTypeSelect.vue"
import PluginMetadataInput from "@/plugin/PluginMetadataInput.vue"
import ServiceSelect from "@/service/ServiceSelect.vue"
import ProjectSelect from "@/project/ProjectSelect.vue"
import TemplateSelect from "@/document/template/TemplateSelect.vue"
import ProjectApi from "@/project/api"

export default {
  setup() {
    return {
      rules: { required },
    }
  },
  name: "CaseTypeNewEditSheet",

  components: {
    CostModelCombobox,
    IncidentTypeSelect,
    PluginMetadataInput,
    ServiceSelect,
    ProjectSelect,
    TemplateSelect,
  },

  data() {
    return {
      visibilities: ["Open", "Restricted"],
      incidentProject: null,
    }
  },

  computed: {
    ...mapFields("case_type", [
      "dialogs.showCreateEdit",
      "selected.auto_close",
      "selected.case_template_document",
      "selected.conversation_target",
      "selected.cost_model",
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
    ...mapFields("auth", ["currentUser.experimental_features"]),
  },

  methods: {
    ...mapActions("case_type", ["save", "closeCreateEdit"]),
  },
  created() {
    if (this.$route.query.project) {
      // required for plugin metadata
      this.project = { name: this.$route.query.project }
      ProjectApi.getAll({ q: this.$route.query.project }).then((response) => {
        this.incidentProject = response.data.items[0]
        this.project = response.data.items[0]
      })
    }
  },
}
</script>
