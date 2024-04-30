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
                  label="Name"
                  hint="A name for your project."
                  clearable
                  required
                  name="Name"
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
      "selected.id",
      "selected.loading",
      "selected.name",
      "selected.organization",
      "selected.owner_conversation",
      "selected.owner_email",
      "selected.enabled",
      "selected.allow_self_join",
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
