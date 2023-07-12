<template>
  <v-dialog persistent max-width="800px" v-model="dialog">
    <template v-slot:activator="{ on, attrs }">
      <v-btn icon v-bind="attrs" v-on="on">
        <v-icon>add</v-icon>
      </v-btn>
    </template>
    <v-card>
      <v-card-title>
        <span class="headline">Create Signal Engagement Filter</span>
        <v-spacer></v-spacer>
      </v-card-title>
      <v-stepper v-model="step">
        <v-stepper-header>
          <v-stepper-step :complete="step > 1" step="1" editable>
            Engagement Filter
          </v-stepper-step>
          <v-divider />

          <v-stepper-step step="2" editable> Save </v-stepper-step>
        </v-stepper-header>

        <v-stepper-items>
          <v-stepper-content step="1">
            <v-card>
              <v-card-text>
                Define the entity types that will be used to match with existing signal instances.
                <v-tabs color="primary" right>
                  <v-tab>Basic</v-tab>
                  <v-tab-item>
                    <span>
                      <entity-type-select
                        v-model="entity_type"
                        :project="project"
                        :signalDefinition="selected"
                      ></entity-type-select>
                      <v-textarea
                        v-model="message"
                        label="Message"
                        hint="Message sent to the user when engaged."
                        clearable
                      />
                      <v-checkbox
                        v-model="require_mfa"
                        label="Require Multi-Factor Authentication"
                      ></v-checkbox>
                    </span>
                  </v-tab-item>
                </v-tabs>
              </v-card-text>
              <v-card-actions>
                <v-spacer />
                <v-btn @click="dialog = false" text> Cancel </v-btn>
                <v-btn color="info" @click="step = 2"> Continue </v-btn>
              </v-card-actions>
            </v-card>
          </v-stepper-content>

          <v-stepper-content step="2">
            <ValidationObserver disabled v-slot="{ invalid, validated }">
              <v-card>
                <v-card-text>
                  Provide a name and description for your filter.
                  <ValidationProvider name="Name" rules="required" immediate>
                    <v-text-field
                      v-model="name"
                      label="Name"
                      hint="A name for your saved search."
                      slot-scope="{ errors, valid }"
                      :error-messages="errors"
                      :success="valid"
                      clearable
                      required
                    />
                  </ValidationProvider>
                  <ValidationProvider name="Description" rules="required" immediate>
                    <v-textarea
                      v-model="description"
                      label="Description"
                      hint="A short description."
                      slot-scope="{ errors, valid }"
                      :error-messages="errors"
                      :success="valid"
                      clearable
                      auto-grow
                    />
                  </ValidationProvider>
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn @click="dialog = false" text> Cancel </v-btn>
                  <v-btn
                    color="info"
                    @click="saveEngagement()"
                    :loading="loading"
                    :disabled="invalid || !validated"
                  >
                    Save
                  </v-btn>
                </v-card-actions>
              </v-card>
            </ValidationObserver>
          </v-stepper-content>
        </v-stepper-items>
      </v-stepper>
    </v-card>
  </v-dialog>
</template>

<script>
import { ValidationObserver, ValidationProvider, extend } from "vee-validate"
import { mapActions } from "vuex"
import { mapFields } from "vuex-map-fields"
import { required } from "vee-validate/dist/rules"
import EntityTypeSelect from "@/entity_type/EntityTypeSelect.vue"
import EntityTypeFilterCombobox from "@/entity_type/EntityTypeFilterCombobox.vue"
import EntityFilterCombobox from "@/entity/EntityFilterCombobox.vue"

extend("required", {
  ...required,
  message: "This field is required",
})
export default {
  name: "SignalEngagementDialog",
  props: {
    value: {
      type: Object,
      default: null,
    },
    signalDefinition: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      step: 1,
      dialog: false,
    }
  },
  components: {
    EntityFilterCombobox,
    EntityTypeSelect,
    EntityTypeFilterCombobox,
    ValidationObserver,
    ValidationProvider,
  },
  computed: {
    ...mapFields("signalEngagement", [
      "selected",
      "selected.name",
      "selected.description",
      "selected.entity_type",
      "selected.require_mfa",
      "selected.message",
      "selected.project",
      "loading",
    ]),
    ...mapFields("route", ["query"]),
  },
  methods: {
    ...mapActions("signalEngagement", ["save"]),
    saveEngagement() {
      // reset local data
      this.save().then((engagement) => {
        this.$emit("input", engagement)
        this.dialog = false
      })
    },
  },
  created() {
    if (this.query.project) {
      this.project = { name: this.query.project }
    }
  },
}
</script>
