<template>
  <ValidationObserver v-slot="{ invalid, validated }">
    <v-navigation-drawer v-model="showCreateEdit" app clipped right width="500">
      <template v-slot:prepend>
        <v-list-item two-line>
          <v-list-item-content>
            <v-list-item-title v-if="id" class="title"> Edit </v-list-item-title>
            <v-list-item-title v-else class="title"> New </v-list-item-title>
            <v-list-item-subtitle>Project</v-list-item-subtitle>
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
                    hint="A name for your project."
                    clearable
                    required
                  />
                </ValidationProvider>
              </v-flex>
              <v-flex xs12>
                <ValidationProvider name="Description" immediate>
                  <v-text-field
                    v-model="description"
                    slot-scope="{ errors, valid }"
                    label="Description"
                    :error-messages="errors"
                    :success="valid"
                    hint="A description for your project."
                    clearable
                    required
                  />
                </ValidationProvider>
              </v-flex>
              <v-flex xs12>
                <color-picker-input v-model="color"></color-picker-input>
              </v-flex>
              <v-flex xs12>
                <ValidationProvider name="Employee Cost" immediate>
                  <v-text-field
                    v-model.number="annual_employee_cost"
                    slot-scope="{ errors, valid }"
                    :error-messages="errors"
                    :success="valid"
                    label="Annual Employee Cost"
                    hint="An annual average cost per employee."
                    clearable
                    required
                    type="number"
                    min="1"
                    pattern="\d+"
                    prefix="$"
                    placeholder="50000"
                  />
                </ValidationProvider>
              </v-flex>
              <v-flex xs12>
                <ValidationProvider name="Year Hours" immediate>
                  <v-text-field
                    v-model.number="business_year_hours"
                    slot-scope="{ errors, valid }"
                    :error-messages="errors"
                    :success="valid"
                    label="Business Year Hours"
                    hint="Number of working hours in a year. Used to calculate hourly rate."
                    clearable
                    required
                    type="number"
                    min="1"
                    pattern="\d+"
                    placeholder="2080"
                  />
                </ValidationProvider>
              </v-flex>
              <v-flex xs12>
                <ValidationProvider name="Owner Email" rules="email" immediate>
                  <v-text-field
                    v-model="owner_email"
                    slot-scope="{ errors, valid }"
                    :error-messages="errors"
                    :success="valid"
                    label="Owner Email"
                    hint="The email account of the project owner."
                    clearable
                    required
                  />
                </ValidationProvider>
              </v-flex>
              <v-flex xs12>
                <ValidationProvider name="Owner Conversation" immediate>
                  <v-text-field
                    v-model="owner_conversation"
                    slot-scope="{ errors, valid }"
                    :error-messages="errors"
                    :success="valid"
                    label="Owner Conversation"
                    hint="The conversation of the project owner (e.g. Slack channel)."
                    clearable
                    required
                  />
                </ValidationProvider>
              </v-flex>
            </v-layout>
          </v-container>
        </v-card-text>
      </v-card>
    </v-navigation-drawer>
  </ValidationObserver>
</template>

<script>
import { mapActions } from "vuex"
import { mapFields } from "vuex-map-fields"
import { required, email } from "vee-validate/dist/rules"
import { ValidationObserver, ValidationProvider, extend } from "vee-validate"

import ColorPickerInput from "@/components/ColorPickerInput.vue"

extend("email", email)

extend("required", {
  ...required,
  message: "This field is required",
})

export default {
  name: "ProjectNewEditSheet",

  components: {
    ColorPickerInput,
    ValidationObserver,
    ValidationProvider,
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
      "dialogs.showCreateEdit",
    ]),
    ...mapFields("route", ["params"]),
  },

  methods: {
    ...mapActions("project", ["save", "closeCreateEdit"]),
  },

  created() {
    this.organization = { name: this.params.organization, slug: this.params.organization }
  },
}
</script>
