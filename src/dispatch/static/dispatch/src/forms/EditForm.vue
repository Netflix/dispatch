<template>
  <v-dialog v-model="showCreateEdit" persistent max-width="1000px">
    <v-card variant="flat">
      <template #prepend>
        <v-list-item lines="two">
          <v-list-item-title v-if="id" class="text-h6"> Edit </v-list-item-title>
          <v-list-item-title v-else class="text-h6"> New </v-list-item-title>
          <v-list-item-subtitle>
            {{ form_type?.name }} form for incident
            <span class="font-weight-black">{{ incident?.name }}</span>
          </v-list-item-subtitle>
        </v-list-item>
      </template>
      <v-card-text v-if="page_schema">
        <FormKit
          style="margin-left: 20px; margin-right: 20px"
          type="form"
          v-model="form_data"
          :actions="false"
        >
          <FormKitSchema :schema="page_schema" :data="form_data" />
        </FormKit>
      </v-card-text>
      <div v-if="!has_formkit_pro" class="ml-11 text-caption text-grey">
        For more advanced form components, upgrade to
        <a href="https://formkit.com/pro" target="_blank" rel="noopener noreferrer">FormKit Pro</a>
      </div>
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
      "selected.attorney_analysis",
      "selected.attorney_questions",
      "selected.project",
      "selected.incident",
      "page_schema",
      "has_formkit_pro",
    ]),
    ...mapFields("incident", { selected_incident: "selected" }),
  },

  methods: {
    ...mapActions("forms", ["closeCreateEdit", "saveAsDraft", "saveAsCompleted"]),
    closeDialog() {
      this.showCreateEdit = false
      this.closeCreateEdit()
    },
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
