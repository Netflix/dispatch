<template>
  <v-dialog persistent max-width="800px" v-model="dialog">
    <template #activator="{ props }">
      <v-btn icon variant="text" v-bind="props">
        <v-icon>mdi-plus</v-icon>
      </v-btn>
    </template>
    <v-card>
      <v-card-title>
        <span class="text-h5">Create Signal Engagement Filter</span>
        <v-spacer />
      </v-card-title>
      <v-stepper v-model="step">
        <v-stepper-header>
          <v-stepper-item :complete="step > 1" :value="1" editable>
            Engagement Filter
          </v-stepper-item>
          <v-divider />

          <v-stepper-item :value="2" editable> Save </v-stepper-item>
        </v-stepper-header>

        <v-stepper-window>
          <v-stepper-window-item :value="1">
            <v-card>
              <v-card-text>
                Define the entity types that will be used to match with existing signal instances.
                <v-tabs v-model="activeTab" color="primary" align-tabs="end">
                  <v-tab>Basic</v-tab>
                </v-tabs>
                <v-window v-model="activeTab">
                  <v-window-item>
                    <span>
                      <entity-type-select
                        v-model="entity_type"
                        :project="project"
                        :signalDefinition="selected"
                      />
                      <v-textarea
                        v-model="message"
                        label="Message"
                        hint="Message sent to the user when engaged."
                        clearable
                      />
                      <v-checkbox
                        v-model="require_mfa"
                        label="Require Multi-Factor Authentication"
                      />
                    </span>
                  </v-window-item>
                </v-window>
              </v-card-text>
              <v-card-actions>
                <v-spacer />
                <v-btn @click="dialog = false" variant="text"> Cancel </v-btn>
                <v-btn color="info" @click="step = 2"> Continue </v-btn>
              </v-card-actions>
            </v-card>
          </v-stepper-window-item>

          <v-stepper-window-item :value="2">
            <v-form @submit.prevent v-slot="{ isValid }">
              <v-card>
                <v-card-text>
                  Provide a name and description for your filter.
                  <v-text-field
                    v-model="name"
                    label="Name"
                    hint="A name for your saved search."
                    clearable
                    required
                    name="Name"
                    :rules="[rules.required]"
                  />
                  <v-textarea
                    v-model="description"
                    label="Description"
                    hint="A short description."
                    clearable
                    auto-grow
                    name="Description"
                    :rules="[rules.required]"
                  />
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn @click="dialog = false" variant="text"> Cancel </v-btn>
                  <v-btn
                    color="info"
                    @click="saveEngagement()"
                    :loading="loading"
                    :disabled="!isValid.value"
                  >
                    Save
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-form>
          </v-stepper-window-item>
        </v-stepper-window>
      </v-stepper>
    </v-card>
  </v-dialog>
</template>

<script>
import { required } from "@/util/form"

import { mapActions } from "vuex"
import { mapFields } from "vuex-map-fields"

import EntityTypeSelect from "@/entity_type/EntityTypeSelect.vue"
export default {
  setup() {
    return {
      rules: { required },
    }
  },
  name: "SignalEngagementDialog",
  data() {
    return {
      activeTab: 0,
      step: 1,
      dialog: false,
    }
  },
  components: {
    EntityTypeSelect,
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
  },
  methods: {
    ...mapActions("signalEngagement", ["save"]),
    saveEngagement() {
      // reset local data
      this.save().then((engagement) => {
        this.$emit("save", engagement)
        this.dialog = false
      })
    },
  },
  created() {
    if (this.$route.query.project) {
      this.project = { name: this.$route.query.project }
    }
  },
}
</script>
