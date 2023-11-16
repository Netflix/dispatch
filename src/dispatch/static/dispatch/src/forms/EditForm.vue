<template>
  <v-dialog v-model="showCreateEdit" persistent max-width="1000px">
    <v-card variant="flat">
      <template #prepend>
        <v-list-item lines="two">
          <v-list-item-title v-if="id" class="text-h6"> Edit </v-list-item-title>
          <v-list-item-title v-else class="text-h6"> New </v-list-item-title>
          <v-list-item-subtitle>
            {{ form_type.name }} form for incident
            <span class="font-weight-black">{{ incident.name }}</span>
          </v-list-item-subtitle>
        </v-list-item>
      </template>
      <v-card-text>
        <FormKit style="margin-left: 20px; outline: #4CAF50 solid 10px;" type="form" v-model="form_data" :actions="false">
          <FormKitSchema :schema="page_schema" />
        </FormKit>
      </v-card-text>
      <v-divider />
      <span class="text-h5 ml-10 mt-3">Attorney Section</span>
      <span class="text-caption ml-10">To be completed by counsel only</span>
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
          <v-col cols="8">
            <v-text-field v-model="memo_link" label="Attorney memo link" />
          </v-col>
        </v-row>
      </v-container>
      <v-card-actions>
        <v-spacer />

        <div>
          <v-menu anchor="bottom end">
            <template #activator="{ props }">
              <v-btn v-bind="props" color="red en-1" variant="text"> Exit without saving </v-btn>
            </template>
            <v-list>
              <v-list-item @click="showCreateEdit = false">
                <v-list-item-title> You will lose any changes. Continue? </v-list-item-title>
              </v-list-item>
              <v-list-item @click="showCreateEdit = true">
                <v-list-item-title> Cancel </v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>
        </div>
        <v-btn color="blue en-1" variant="text" @click="saveAsDraft()"> Save as Draft </v-btn>
        <v-btn color="blue en-1" variant="text" @click="saveAsCompleted()"> Submit </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

export default {
  name: "FormEditor",

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
      "dialogs.showCreateEdit",
      "selected.id",
      "selected.form_schema",
      "selected.form_type",
      "selected.form_data",
      "selected.incident_id",
      "selected.attorney_status",
      "selected.memo_link",
      "selected.project",
      "selected.incident",
      "page_schema",
    ]),
    ...mapFields("incident", { selected_incident: "selected" }),
  },

  methods: {
    ...mapActions("forms", [
      "closeCreateEdit",
      "saveAsDraft",
      "saveAsCompleted",
      "closeCreateEdit",
    ]),
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
      console.log(`*** Got form_data: ${JSON.stringify(this.form_data)}`)
      if (this.incident) {
        this.incident_id = this.incident.id
        this.project = this.incident.project
      } else {
        this.incident_id = this.selected_incident.id
        this.project = this.selected_incident.project
      }
      console.log(`*** Got incident: ${JSON.stringify(this.incident.id)}`)

      console.log(`*** Got project: ${JSON.stringify(this.project)}`)
    },
  },
}
</script>
<style>
:root {
  --fk-max-width-input: 100em !important;
}
</style>
