<template>
  <v-form @submit.prevent v-slot="{ isValid }">
    <v-navigation-drawer v-model="showCreateEdit" location="right" width="500">
      <template #prepend>
        <v-list-item lines="two">
          <v-list-item-title v-if="id" class="text-h6"> Edit </v-list-item-title>
          <v-list-item-title v-else class="text-h6"> New </v-list-item-title>
          <v-list-item-subtitle>Incident Cost Type</v-list-item-subtitle>

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
                  hint="A name for the incident cost type."
                  clearable
                  required
                  name="Name"
                  :rules="[rules.required]"
                />
              </v-col>
              <v-col cols="12">
                <v-textarea
                  v-model="description"
                  label="Description"
                  hint="A description for the incident cost type."
                  clearable
                  name="Description"
                />
              </v-col>
              <v-col cols="12">
                <incident-cost-type-category-select v-model="category" />
              </v-col>
              <!-- TODO(mvilanova): Add section for cost type details -->
              <v-col cols="12">
                <v-checkbox
                  v-model="default_incident_cost_type"
                  label="Default"
                  hint="Check this if this incident cost type should be the default."
                />
              </v-col>
              <v-col cols="12">
                <v-checkbox
                  v-model="editable"
                  label="Editable"
                  hint="Whether this cost type can be edited or not."
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
import { required } from "@/util/form"
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

import IncidentCostTypeCategorySelect from "@/incident_cost_type/IncidentCostTypeCategorySelect.vue"

export default {
  setup() {
    return {
      rules: { required },
    }
  },
  name: "IncidentCostTypeNewEditSheet",

  components: {
    IncidentCostTypeCategorySelect,
  },

  computed: {
    ...mapFields("incident_cost_type", [
      "selected.name",
      "selected.description",
      "selected.category",
      "selected.details",
      "selected.editable",
      "selected.id",
      "selected.project",
      "selected.loading",
      "dialogs.showCreateEdit",
    ]),
    ...mapFields("incident_cost_type", {
      default_incident_cost_type: "selected.default",
    }),
  },

  methods: {
    ...mapActions("incident_cost_type", ["save", "closeCreateEdit"]),
  },

  created() {
    if (this.$route.query.project) {
      this.project = { name: this.$route.query.project }
    }
  },
}
</script>
