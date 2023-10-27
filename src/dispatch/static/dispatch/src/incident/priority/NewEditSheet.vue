<template>
  <v-form @submit.prevent v-slot="{ isValid }">
    <v-navigation-drawer v-model="showCreateEdit" location="right" width="500">
      <template #prepend>
        <v-list-item lines="two">
          <v-list-item-title v-if="id" class="text-h6"> Edit </v-list-item-title>
          <v-list-item-title v-else class="text-h6"> New </v-list-item-title>
          <v-list-item-subtitle>Incident Priority</v-list-item-subtitle>

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
                  hint="A name for your incident priority."
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
                  hint="A description for your incident priority."
                  clearable
                  required
                  name="Description"
                  :rules="[rules.required]"
                />
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="view_order"
                  label="View Order"
                  type="number"
                  hint="Enter a value to indicate the order in which you want this priority to be shown in a list (lowest numbers are shown first)."
                  clearable
                  required
                  name="View Order"
                  :rules="[rules.required]"
                />
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="tactical_report_reminder"
                  label="Tactical Report Reminder"
                  type="number"
                  hint="Number of hours to send a tactical report reminder to the incident commander."
                  clearable
                  required
                  min="1"
                  name="Tactical Report Reminder"
                  :rules="[rules.required]"
                />
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="executive_report_reminder"
                  label="Executive Report Reminder"
                  type="number"
                  hint="Number of hours to send an executive report reminder to the incident commander."
                  clearable
                  required
                  min="1"
                  name="Executive Report Reminder"
                  :rules="[rules.required]"
                />
              </v-col>
              <v-col cols="12">
                <v-checkbox
                  v-model="page_commander"
                  label="Page Commander"
                  hint="Would you like Dispatch to page the incident commander on incident creation?"
                />
              </v-col>
              <v-col cols="12">
                <color-picker-input label="Color" v-model="color" />
              </v-col>
              <v-col cols="12">
                <v-checkbox
                  v-model="default_incident_priority"
                  label="Default Incident Priority"
                  hint="Check if this incident priority should be the default."
                />
              </v-col>
              <v-col cols="12">
                <v-checkbox
                  v-model="enabled"
                  label="Enabled"
                  hint="Determines whether this incident priority is availible for new incidents."
                />
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

import ColorPickerInput from "@/components/ColorPickerInput.vue"

export default {
  setup() {
    return {
      rules: { required },
    }
  },
  name: "IncidentPriorityNewEditSheet",

  components: {
    ColorPickerInput,
  },

  data() {
    return {}
  },

  computed: {
    ...mapFields("incident_priority", [
      "dialogs.showCreateEdit",
      "selected.color",
      "selected.default",
      "selected.description",
      "selected.enabled",
      "selected.executive_report_reminder",
      "selected.id",
      "selected.loading",
      "selected.name",
      "selected.page_commander",
      "selected.project",
      "selected.tactical_report_reminder",
      "selected.view_order",
    ]),
    ...mapFields("incident_priority", {
      default_incident_priority: "selected.default",
    }),
  },

  methods: {
    ...mapActions("incident_priority", ["save", "closeCreateEdit"]),
  },

  created() {
    if (this.$route.query.project) {
      this.project = { name: this.$route.query.project }
    }
  },
}
</script>
