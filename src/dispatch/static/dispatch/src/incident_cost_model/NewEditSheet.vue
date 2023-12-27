<template>
  <v-navigation-drawer v-model="showCreateEdit" location="right" width="600">
    <template #prepend>
      <v-list-item lines="two">
        <v-list-item-title v-if="id" class="text-h6"> Edit </v-list-item-title>
        <v-list-item-title v-else class="text-h6"> New </v-list-item-title>
        <v-list-item-subtitle>Incident Cost Model</v-list-item-subtitle>

        <template #append>
          <v-btn
            icon
            variant="text"
            color="info"
            :loading="loading"
            :disabled="!valid"
            @click="save"
          >
            <v-icon>mdi-content-save</v-icon>
          </v-btn>
          <v-btn icon variant="text" color="secondary" @click="closeCreateEdit">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </template>
      </v-list-item>
    </template>
    <v-card>
      <v-card-text>
        <v-form v-model="valid">
          <v-checkbox
            v-model="enabled"
            hint="When an incident is associated with a disabled cost model, the
            incident will automatically revert to the traditional incident cost model."
            label="Enabled"
          />
          <v-text-field
            v-model="name"
            label="Name"
            hint="Name of the incident cost model."
            clearable
            required
            name="Name"
            :rules="[rules.required]"
          />

          <v-textarea
            v-model="description"
            label="Description"
            hint="Description of the incident cost model."
            clearable
            required
            name="Description"
          />
          <cost-model-activity-input v-model="activities" />
        </v-form>
      </v-card-text>
    </v-card>
  </v-navigation-drawer>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { required } from "@/util/form"
import { mapActions } from "vuex"
import CostModelActivityInput from "@/incident_cost_model/CostModelActivityInput.vue"

export default {
  name: "IncidentCostModelEditSheet",
  data() {
    return {
      valid: false,
      options: {
        initialValidation: "all",
      },
    }
  },
  components: {
    CostModelActivityInput,
  },
  setup() {
    return {
      rules: { required },
    }
  },
  computed: {
    ...mapFields("incident_cost_model", [
      "selected.id",
      "selected.name",
      "selected.enabled",
      "selected.description",
      "selected.created_at",
      "selected.updated_at",
      "selected.project",
      "selected.loading",
      "selected.activities",
      "selected.incident_cost_model",
      "dialogs.showCreateEdit",
    ]),
  },

  methods: {
    ...mapActions("incident_cost_model", ["save", "closeCreateEdit"]),
  },

  created() {
    if (this.$route.query.project) {
      this.project = { name: this.$route.query.project }
    }
  },
}
</script>
