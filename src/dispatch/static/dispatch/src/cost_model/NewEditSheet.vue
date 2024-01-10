<template>
  <v-navigation-drawer v-model="showCreateEdit" location="right" width="600">
    <template #prepend>
      <v-list-item lines="two">
        <v-list-item-title v-if="id" class="text-h6"> Edit </v-list-item-title>
        <v-list-item-title v-else class="text-h6"> New </v-list-item-title>
        <v-list-item-subtitle>Cost Model</v-list-item-subtitle>

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
            incident will automatically revert to the traditional cost model."
            label="Enabled"
          />
          <v-text-field
            v-model="name"
            label="Name"
            hint="Name of the cost model."
            clearable
            required
            name="Name"
            :rules="[rules.required]"
          />

          <v-textarea
            v-model="description"
            label="Description"
            hint="Description of the cost model."
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
import CostModelActivityInput from "@/cost_model/CostModelActivityInput.vue"

export default {
  name: "CostModelEditSheet",
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
    ...mapFields("cost_model", [
      "selected.id",
      "selected.name",
      "selected.enabled",
      "selected.description",
      "selected.created_at",
      "selected.updated_at",
      "selected.project",
      "selected.loading",
      "selected.activities",
      "selected.cost_model",
      "dialogs.showCreateEdit",
    ]),
  },

  methods: {
    ...mapActions("cost_model", ["save", "closeCreateEdit"]),
  },

  created() {
    if (this.$route.query.project) {
      this.project = { name: this.$route.query.project }
    }
  },
}
</script>
