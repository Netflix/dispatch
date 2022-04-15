<template>
  <ValidationObserver v-slot="{ invalid, validated }">
    <v-navigation-drawer v-model="showCreateEdit" app clipped right width="500">
      <template v-slot:prepend>
        <v-list-item two-line>
          <v-list-item-content>
            <v-list-item-title v-if="id" class="title"> Edit </v-list-item-title>
            <v-list-item-title v-else class="title"> New </v-list-item-title>
            <v-list-item-subtitle>Incident Priority</v-list-item-subtitle>
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
                    hint="A name for your incident priority."
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
                    hint="A description for your incident priority."
                    clearable
                    required
                  />
                </ValidationProvider>
              </v-flex>
              <v-flex xs12>
                <ValidationProvider name="View Order" rules="required" immediate>
                  <v-text-field
                    v-model="view_order"
                    slot-scope="{ errors, valid }"
                    label="View Order"
                    :error-messages="errors"
                    :success="valid"
                    type="number"
                    hint="Enter an value indicating where you want this priority to be in a list (lowest are first)."
                    clearable
                    required
                  />
                </ValidationProvider>
              </v-flex>
              <v-flex xs12>
                <ValidationProvider name="Tactical Report Reminder" rules="required" immediate>
                  <v-text-field
                    v-model="tactical_report_reminder"
                    slot-scope="{ errors, valid }"
                    label="Tactical Report Reminder"
                    :error-messages="errors"
                    :success="valid"
                    type="number"
                    hint="Number of hours to send a tactical report reminder to the incident commander."
                    clearable
                    required
                    min="1"
                  />
                </ValidationProvider>
              </v-flex>
              <v-flex xs12>
                <ValidationProvider name="Executive Report Reminder" rules="required" immediate>
                  <v-text-field
                    v-model="executive_report_reminder"
                    slot-scope="{ errors, valid }"
                    label="Executive Report Reminder"
                    :error-messages="errors"
                    :success="valid"
                    type="number"
                    hint="Number of hours to send an executive report reminder to the incident commander."
                    clearable
                    required
                    min="1"
                  />
                </ValidationProvider>
              </v-flex>
              <v-flex xs12>
                <v-checkbox
                  v-model="page_commander"
                  label="Page Commander"
                  hint="Would you like Dispatch to page the incident commander on incident creation?"
                />
              </v-flex>
              <v-flex xs12>
                <color-picker-input label="Color" v-model="color"></color-picker-input>
              </v-flex>
              <v-flex xs12>
                <v-checkbox
                  v-model="default_incident_priority"
                  label="Default Incident Priority"
                  hint="Check if this incident priority should be the default."
                />
              </v-flex>
              <v-flex xs12>
                <v-checkbox
                  v-model="enabled"
                  label="Enabled"
                  hint="Determines whether this incident priority is availible for new incidents."
                />
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
import { required } from "vee-validate/dist/rules"
import { ValidationObserver, ValidationProvider, extend } from "vee-validate"

import ColorPickerInput from "@/components/ColorPickerInput.vue"

extend("required", {
  ...required,
  message: "This field is required",
})

export default {
  name: "IncidentPriorityNewEditSheet",

  components: {
    ColorPickerInput,
    ValidationObserver,
    ValidationProvider,
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
    ...mapFields("route", ["query"]),
  },

  methods: {
    ...mapActions("incident_priority", ["save", "closeCreateEdit"]),
  },

  created() {
    if (this.query.project) {
      this.project = { name: this.query.project }
    }
  },
}
</script>
