<template>
  <v-form @submit.prevent v-slot="{ isValid }">
    <v-navigation-drawer v-model="showCreateEdit" location="right" width="500">
      <template #prepend>
        <v-list-item lines="two">
          <v-list-item-title v-if="id" class="text-h6"> Edit </v-list-item-title>
          <v-list-item-title v-else class="text-h6"> New </v-list-item-title>
          <v-list-item-subtitle>Individual</v-list-item-subtitle>

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
                  hint="Name of individual."
                  clearable
                  required
                  name="Name"
                  :rules="[rules.required]"
                />
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="email"
                  label="Email"
                  hint="Individual's email address."
                  clearable
                  required
                  name="Email"
                  :rules="[rules.required]"
                />
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="company"
                  label="Company"
                  hint="Individual's company."
                  clearable
                  name="Company"
                />
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="external_id"
                  label="External Id"
                  hint="Individual's external ID."
                  clearable
                  name="ExternalId"
                />
              </v-col>
              <v-col cols="12">
                <span class="text-subtitle-2"
                  >Engagement
                  <v-tooltip max-width="250px" location="bottom">
                    <template #activator="{ props }">
                      <v-icon v-bind="props">mdi-help-circle-outline</v-icon>
                    </template>
                    This individual will be automatically engaged for any incident or case matching
                    the following filters.
                  </v-tooltip>
                </span>
              </v-col>
              <v-col cols="12">
                <search-filter-combobox
                  v-model="filters"
                  :project="project"
                  label="Filters"
                  hint="Select one or more filters that will determine when the individual is engaged."
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

import SearchFilterCombobox from "@/search/SearchFilterCombobox.vue"

export default {
  setup() {
    return {
      rules: { required },
    }
  },
  name: "IndividualNewEditSheet",

  data() {
    return {
      visibilities: ["Open"],
    }
  },

  components: {
    SearchFilterCombobox,
  },

  computed: {
    ...mapFields("individual", [
      "selected.name",
      "selected.email",
      "selected.company",
      "selected.external_id",
      "selected.filters",
      "selected.id",
      "selected.project",
      "selected.loading",
      "dialogs.showCreateEdit",
    ]),
  },

  methods: {
    ...mapActions("individual", ["save", "closeCreateEdit"]),
  },

  created() {
    if (this.$route.query.project) {
      this.project = { name: this.$route.query.project }
    }
  },
}
</script>
