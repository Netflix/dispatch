<template>
  <v-form @submit.prevent v-slot="{ isValid }">
    <v-navigation-drawer v-model="showCreateEdit" app clipped location="right" width="500">
      <template #prepend>
        <v-list-item lines="two">
          <v-list-item-title v-if="id" class="text-h6"> Edit </v-list-item-title>
          <v-list-item-title v-else class="text-h6"> New </v-list-item-title>
          <v-list-item-subtitle>Incident severity</v-list-item-subtitle>

          <v-btn
            icon
            variant="text"
            color="info"
            :loading="loading"
            :disabled="!isValid.value || !validated"
            @click="save()"
          >
            <v-icon>save</v-icon>
          </v-btn>
          <v-btn icon variant="text" color="secondary" @click="closeCreateEdit()">
            <v-icon>close</v-icon>
          </v-btn>
        </v-list-item>
      </template>
      <v-card flat>
        <v-card-text>
          <v-container grid-list-md>
            <v-layout wrap>
              <v-flex xs12>
                <span class="text-subtitle-2">Details</span>
              </v-flex>
              <v-flex xs12>
                <v-text-field
                  v-model="name"
                  label="Name"
                  hint="A name for your incident severity."
                  clearable
                  required
                  name="Name"
                  :rules="[rules.required]"
                />
              </v-flex>
              <v-flex xs12>
                <v-textarea
                  v-model="description"
                  label="Description"
                  hint="A description for your incident severity."
                  clearable
                  required
                  name="Description"
                  :rules="[rules.required]"
                />
              </v-flex>
              <v-flex xs12>
                <v-text-field
                  v-model="view_order"
                  label="View Order"
                  type="number"
                  hint="Enter a value to indicate the order in which you want this severity to be shown in a list (lowest numbers are shown first)."
                  clearable
                  required
                  name="View Order"
                  :rules="[rules.required]"
                />
              </v-flex>
              <v-flex xs12>
                <color-picker-input label="Color" v-model="color" />
              </v-flex>
              <v-flex xs12>
                <v-checkbox
                  v-model="default_incident_severity"
                  label="Default Incident Severity"
                  hint="Check if this incident severity should be the default."
                />
              </v-flex>
              <v-flex xs12>
                <v-checkbox
                  v-model="enabled"
                  label="Enabled"
                  hint="Determines whether this incident severity is availible for new incidents."
                />
              </v-flex>
            </v-layout>
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
  name: "IncidentSeverityNewEditSheet",

  components: {
    ColorPickerInput,
  },

  data() {
    return {}
  },

  computed: {
    ...mapFields("incident_severity", [
      "dialogs.showCreateEdit",
      "selected.color",
      "selected.default",
      "selected.description",
      "selected.enabled",
      "selected.id",
      "selected.loading",
      "selected.name",
      "selected.project",
      "selected.view_order",
    ]),
    ...mapFields("incident_severity", {
      default_incident_severity: "selected.default",
    }),
  },

  methods: {
    ...mapActions("incident_severity", ["save", "closeCreateEdit"]),
  },

  created() {
    if (this.$route.query.project) {
      this.project = { name: this.$route.query.project }
    }
  },
}
</script>
