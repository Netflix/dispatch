<template>
  <v-form @submit.prevent v-slot="{ isValid }">
    <v-navigation-drawer v-model="showCreateEdit" location="right" width="500">
      <template #prepend>
        <v-list-item lines="two">
          <v-list-item-title v-if="id" class="text-h6"> Edit </v-list-item-title>
          <v-list-item-title v-else class="text-h6"> New </v-list-item-title>
          <v-list-item-subtitle>Project</v-list-item-subtitle>

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
                  label="Key"
                  hint="A key for your project."
                  clearable
                  required
                  name="Key"
                  :rules="[rules.required]"
                />
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="display_name"
                  label="Display Name"
                  hint="A display name for your project (used on forms)."
                  clearable
                  required
                  name="Display Name"
                  :rules="[rules.required]"
                />
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="description"
                  label="Description"
                  hint="A description for your project."
                  clearable
                  required
                  name="Description"
                />
              </v-col>
              <v-col cols="12">
                <v-checkbox
                  v-model="enabled"
                  label="Enabled"
                  hint="Whether this project is enabled for new cases and incidents."
                />
              </v-col>
              <v-col cols="12">
                <v-checkbox
                  v-model="allow_self_join"
                  label="Allow Self Join"
                  hint="Allow users to self-join an incident from the UI"
                />
              </v-col>
              <v-col cols="12">
                <color-picker-input v-model="color" />
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model.number="annual_employee_cost"
                  label="Annual Employee Cost"
                  hint="An annual average cost per employee."
                  clearable
                  required
                  type="number"
                  min="1"
                  pattern="\d+"
                  prefix="$"
                  placeholder="50000"
                  name="Employee Cost"
                />
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model.number="business_year_hours"
                  label="Business Year Hours"
                  hint="Number of working hours in a year. Used to calculate hourly rate."
                  clearable
                  required
                  type="number"
                  min="1"
                  pattern="\d+"
                  placeholder="2080"
                  name="Year Hours"
                />
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="owner_email"
                  label="Owner Email"
                  hint="The email account of the project owner."
                  clearable
                  required
                  name="Owner Email"
                  :rules="[rules.email]"
                />
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="owner_conversation"
                  label="Owner Conversation"
                  hint="The conversation of the project owner (e.g. Slack channel)."
                  clearable
                  required
                  name="Owner Conversation"
                />
              </v-col>
              <span class="text-body-1 text-medium-emphasis">Alternative folder structure</span>
              <v-col cols="12">
                <v-text-field
                  v-model="storage_folder_one"
                  label="Storage folder 1 name"
                  hint="The name of one of the storage folders."
                  clearable
                  required
                  name="Storage folder 1 name"
                />
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="storage_folder_two"
                  label="Storage folder 2 name"
                  hint="The name of the other storage folder."
                  clearable
                  required
                  name="Storage folder 2 name"
                />
              </v-col>
              <v-col cols="12">
                <v-checkbox
                  v-model="storage_use_folder_one_as_primary"
                  label="Use Storage folder 1 as the primary storage"
                  hint="For incidents and cases, use storage folder 1 as the primary storage."
                />
              </v-col>
              <v-col cols="12">
                <v-checkbox
                  v-model="storage_use_title"
                  label="Use the incident title as the storage folder name"
                  hint="Use the title of the incident as the name of the storage folder."
                />
              </v-col>
              <v-col cols="12">
                <v-checkbox
                  v-model="select_commander_visibility"
                  label="Allow incident commander selection"
                  hint="Enable the option to select a specific incident commander in the UI"
                />
              </v-col>
              <span class="text-body-1 text-medium-emphasis">Report incident card settings</span>
              <v-col cols="12">
                <v-text-field
                  v-model="report_incident_instructions"
                  label="Instructions for report incident card"
                  hint="Describes the instructions for the report incident card."
                  clearable
                  required
                  name="Instructions for report incident card"
                />
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="report_incident_title_hint"
                  label="Hint for the incident title on the report incident card"
                  hint="Describes the hint for the incident title on the report incident card."
                  clearable
                  required
                  name="Hint for the incident title on the report incident card"
                />
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="report_incident_description_hint"
                  label="Hint for the incident description on the report incident card"
                  hint="Describes the hint for the incident description on the report incident card."
                  clearable
                  required
                  name="Hint for the incident description on the report incident card"
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
import { required, email } from "@/util/form"
import { mapActions } from "vuex"
import { mapFields } from "vuex-map-fields"

import ColorPickerInput from "@/components/ColorPickerInput.vue"

export default {
  setup() {
    return {
      rules: { required, email },
    }
  },
  name: "ProjectNewEditSheet",

  components: {
    ColorPickerInput,
  },

  computed: {
    ...mapFields("project", [
      "selected.annual_employee_cost",
      "selected.business_year_hours",
      "selected.color",
      "selected.description",
      "selected.display_name",
      "selected.id",
      "selected.loading",
      "selected.name",
      "selected.organization",
      "selected.owner_conversation",
      "selected.owner_email",
      "selected.enabled",
      "selected.storage_folder_one",
      "selected.storage_folder_two",
      "selected.storage_use_folder_one_as_primary",
      "selected.storage_use_title",
      "selected.allow_self_join",
      "selected.select_commander_visibility",
      "selected.report_incident_instructions",
      "selected.report_incident_title_hint",
      "selected.report_incident_description_hint",
      "dialogs.showCreateEdit",
    ]),
  },

  methods: {
    ...mapActions("project", ["save", "closeCreateEdit"]),
  },

  created() {
    this.organization = {
      name: this.$route.params.organization,
      slug: this.$route.params.organization,
    }
  },
}
</script>
