<template>
  <ValidationObserver v-slot="{ invalid, validated }">
    <v-navigation-drawer v-model="showCreateEdit" app clipped right width="500">
      <template v-slot:prepend>
        <v-list-item two-line>
          <v-list-item-content>
            <v-list-item-title v-if="id" class="title"> Edit </v-list-item-title>
            <v-list-item-title v-else class="title"> New </v-list-item-title>
            <v-list-item-subtitle>Supression Rule</v-list-item-subtitle>
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
          <v-container>
            <v-row>
              <span class="subtitle-2">Details</span>
            </v-row>
            <v-row>
              <v-col>
                <ValidationProvider name="Name" rules="required" immediate>
                  <v-text-field
                    v-model="name"
                    slot-scope="{ errors, valid }"
                    :error-messages="errors"
                    :success="valid"
                    label="Name"
                    hint="A name for your duplication rule."
                    clearable
                    required
                  />
                </ValidationProvider>
              </v-col>
            </v-row>
            <v-row>
              <v-col>
                <ValidationProvider name="Description" rules="required" immediate>
                  <v-textarea
                    v-model="description"
                    slot-scope="{ errors, valid }"
                    label="Description"
                    :error-messages="errors"
                    :success="valid"
                    hint="A description for your duplication rule."
                    clearable
                    required
                  />
                </ValidationProvider>
              </v-col>
            </v-row>
            <v-row>
              <v-col>
                <v-select
                  v-model="mode"
                  label="Mode"
                  :items="modes"
                  hint="The rules current mode."
                />
              </v-col>
            </v-row>
            <v-row>
              <date-time-picker-menu label="Expires At" v-model="expiration" />
            </v-row>
            <v-row>
              <v-col>
                <span class="subtitle-2">
                  Evergreen
                  <v-tooltip max-width="250px" bottom>
                    <template v-slot:activator="{ on, attrs }">
                      <v-icon v-bind="attrs" v-on="on"> help_outline </v-icon>
                    </template>
                    Dispatch will send an email reminder to the template owner to keep it up to
                    date.
                  </v-tooltip>
                </span>
              </v-col>
            </v-row>
            <v-row>
              <v-col>
                <ValidationProvider name="Owner" immediate>
                  <v-text-field
                    v-model="evergreen_owner"
                    slot-scope="{ errors, valid }"
                    label="Owner"
                    :error-messages="errors"
                    :success="valid"
                    hint="Owner of this document template."
                    clearable
                  />
                </ValidationProvider>
              </v-col>
            </v-row>
            <v-row>
              <v-col>
                <ValidationProvider name="Reminder Interval" immediate>
                  <v-text-field
                    v-model="evergreen_reminder_interval"
                    slot-scope="{ errors, valid }"
                    label="Reminder Interval"
                    :error-messages="errors"
                    :success="valid"
                    type="number"
                    hint="Number of days that should elapse between reminders sent to the document template owner."
                    placeholder="90"
                    clearable
                    min="1"
                  />
                </ValidationProvider>
              </v-col>
            </v-row>
            <v-row>
              <v-col>
                <v-checkbox
                  v-model="evergreen"
                  hint="Enabling evergreen will send periodic reminders to the owner to update this document template."
                  label="Enabled"
                />
              </v-col>
            </v-row>
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

extend("required", {
  ...required,
  message: "This field is required",
})

export default {
  name: "SupressionRuleNewEditSheet",

  components: {
    ValidationObserver,
    ValidationProvider,
  },

  data() {
    return {
      modes: ["Active", "Monitor", "Inactive", "Expired"],
    }
  },

  computed: {
    ...mapFields("signalSupressionRule", [
      "dialogs.showCreateEdit",
      "selected.id",
      "selected.name",
      "selected.description",
      "selected.expression",
      "selected.mode",
      "selected.expiration",
      "selected.evergreen_owner",
      "selected.evergreen",
      "selected.evergreen_reminder_interval",
      "selected.loading",
      "selected.project",
    ]),
    ...mapFields("signalSupressionRule", {
      default_incident_priority: "selected.default",
    }),
    ...mapFields("route", ["query"]),
  },

  methods: {
    ...mapActions("signalSupressionRule", ["save", "closeCreateEdit"]),
  },

  created() {
    if (this.query.project) {
      this.project = { name: this.query.project }
    }
  },
}
</script>
