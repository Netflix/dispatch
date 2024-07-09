<template>
  <v-dialog v-model="showAttorneyEdit" persistent max-width="1000px">
    <v-card variant="flat">
      <template #prepend>
        <v-list-item lines="two">
          <v-list-item-title class="text-h6"> Attorney Review </v-list-item-title>
          <v-list-item-subtitle>
            {{ form_type?.name }} form for incident
            <span class="font-weight-black">{{ incident?.name }}</span>
          </v-list-item-subtitle>
        </v-list-item>
      </template>
      <span class="text-h5 ml-10 mt-3 mb-3">Incident Information</span>
      <span class="ml-10" v-for="item in incident_data.data" :key="item">
        <b>{{ item.question }}</b
        >: {{ item.answer }}<br />
      </span>
      <span class="ml-10" v-if="incident_data.slack_channel">
        <b>Slack channel</b>: <a :href="incident_data.slack_channel">#{{ incident_data.name }}</a>
        <br />
      </span>
      <span class="ml-10" v-if="incident_data.incident_doc">
        <b>Incident document</b>:
        <a :href="incident_data.incident_doc">{{ incident_data.name }} Incident Document</a> <br />
      </span>
      <v-divider class="mt-5" />
      <span class="text-h5 ml-10 mt-3 mb-3">Form Data</span>
      <span class="ml-10" v-for="item in page_data" :key="item">
        <b>{{ item.question }}</b
        >: {{ item.answer }}<br />
      </span>
      <v-divider class="mt-5" />
      <span class="text-h5 ml-10 mt-3">Attorney Section</span>
      <span class="text-caption ml-10"
        >To be completed by counsel only. This section is privileged and confidential.</span
      >
      <v-container class="ml-6">
        <v-row>
          <v-col cols="5">
            <v-select
              v-model="attorney_status"
              label="Attorney Status"
              :items="['Not reviewed', 'Reviewed: no action required', 'Reviewed: action required']"
            />
          </v-col>
        </v-row>
        <v-row style="margin-top: -40px">
          <v-col cols="6">
            <v-textarea v-model="attorney_questions" label="Open questions" />
          </v-col>
          <v-col cols="6">
            <v-textarea v-model="attorney_analysis" label="Attorney analysis" />
          </v-col>
        </v-row>
        <div v-if="attorney_page_schema && attorney_page_schema.length > 0">
          <span class="text-body-1 mt-3 text-medium-emphasis">Additional attorney questions</span>
          <FormKit
            style="margin-left: 20px; margin-right: 20px; margin-top: 10px"
            type="form"
            v-model="attorney_form_data"
            :actions="false"
          >
            <FormKitSchema :schema="attorney_page_schema" :data="attorney_form_data" />
          </FormKit>
        </div>
      </v-container>
      <v-card-actions>
        <v-spacer />
        <div>
          <v-menu anchor="bottom end">
            <template #activator="{ props }">
              <v-btn v-bind="props" color="red en-1" variant="text"> Exit without saving </v-btn>
            </template>
            <v-list>
              <v-list-item @click="closeDialog()">
                <v-list-item-title> You will lose any changes. Continue? </v-list-item-title>
              </v-list-item>
              <v-list-item @click="showAttorneyEdit = true">
                <v-list-item-title> Cancel </v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>
        </div>
        <v-btn color="blue en-1" variant="text" @click="saveAttorneyAnalysis()">
          Update form
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

export default {
  name: "FormsTableAttorneyEdit",

  props: {
    value: {
      type: Object,
      default: function () {
        return {}
      },
    },
  },

  computed: {
    ...mapFields("forms", [
      "dialogs.showAttorneyEdit",
      "selected.id",
      "selected.form_schema",
      "selected.attorney_form_data",
      "selected.form_type",
      "selected.form_data",
      "selected.incident_id",
      "selected.attorney_status",
      "selected.attorney_analysis",
      "selected.attorney_questions",
      "selected.project",
      "selected.incident",
      "page_data",
      "attorney_page_schema",
      "incident_data",
    ]),
    ...mapFields("incident", { selected_incident: "selected" }),
  },

  methods: {
    ...mapActions("forms", ["closeAttorneyEdit", "saveAttorneyAnalysis"]),
    closeDialog() {
      this.showAttorneyEdit = false
      this.closeAttorneyEdit()
    },
  },

  data() {
    return {
      dialog: false,
      editorOptions: {
        automaticLayout: true,
        renderValidationDecorations: "on",
        readOnly: true,
        minimap: {
          enabled: false,
        },
      },
    }
  },

  watch: {
    form_data() {
      if (!this.incident_id) {
        if (this.incident) {
          this.incident_id = this.incident.id
          this.project = this.incident.project
        } else {
          this.incident = this.selected_incident
          this.incident_id = this.selected_incident.id
          this.project = this.selected_incident.project
        }
      }
    },
  },
}
</script>
<style>
:root {
  --fk-max-width-input: 100em !important;
  --fk-font-size-help: 0.75em !important;
}
</style>
