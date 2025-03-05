<template>
  <v-form @submit.prevent v-slot="{ isValid }">
    <v-navigation-drawer v-model="showCreateEdit" location="right" width="500">
      <template #prepend>
        <v-list-item lines="two">
          <v-list-item-title v-if="id" class="text-h6"> Edit </v-list-item-title>
          <v-list-item-title v-else class="text-h6"> New </v-list-item-title>
          <v-list-item-subtitle>Case Cost Type</v-list-item-subtitle>

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
                  hint="A name for the case cost type."
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
                  hint="A description for the case cost type."
                  clearable
                  name="Description"
                />
              </v-col>
              <v-col cols="12">
                <case-cost-type-category-select v-model="category" />
              </v-col>
              <v-col cols="12">
                <v-tooltip max-width="500px" open-delay="50" location="bottom">
                  <template #activator="{ props }">
                    <div class="text-body-1 ml-1 mt-2">
                      Response Cost Model Type
                      <v-icon v-bind="props"> mdi-information-outline </v-icon>
                    </div>
                  </template>
                  <span>
                    The response cost model type is used to identify if the cost type is linked to
                    response cost calculation under either the new or classic cost model. If the
                    value is set to none, this cost is not related to response costs and is intended
                    for manual cost entry.
                  </span>
                </v-tooltip>
                <v-radio-group v-model="response_case_cost_type" disabled>
                  <v-radio
                    v-for="modelType in ['New', 'Classic', 'None']"
                    :key="modelType"
                    :label="modelType"
                    :value="modelType"
                  />
                </v-radio-group>
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

import CaseCostTypeCategorySelect from "@/case_cost_type/CaseCostTypeCategorySelect.vue"

export default {
  setup() {
    return {
      rules: { required },
    }
  },
  name: "CaseCostTypeNewEditSheet",

  components: {
    CaseCostTypeCategorySelect,
  },

  computed: {
    ...mapFields("case_cost_type", [
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
    ...mapFields("case_cost_type", {
      response_case_cost_type: "selected.model_type",
    }),
  },

  methods: {
    ...mapActions("case_cost_type", ["save", "closeCreateEdit"]),
  },

  created() {
    if (this.$route.query.project) {
      this.project = { name: this.$route.query.project }
    }
  },
}
</script>
