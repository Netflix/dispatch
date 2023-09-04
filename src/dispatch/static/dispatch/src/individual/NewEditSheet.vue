<template>
  <ValidationObserver v-slot="{ invalid, validated }">
    <v-navigation-drawer v-model="showCreateEdit" app clipped location="right" width="500">
      <template #prepend>
        <v-list-item lines="two">
          <v-list-item-title v-if="id" class="text-h6"> Edit </v-list-item-title>
          <v-list-item-title v-else class="text-h6"> New </v-list-item-title>
          <v-list-item-subtitle>Individual</v-list-item-subtitle>

          <v-btn
            icon
            variant="text"
            color="info"
            :loading="loading"
            :disabled="invalid || !validated"
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
                <ValidationProvider name="Name" rules="required" immediate>
                  <v-text-field
                    v-model="name"
                    slot-scope="{ errors, valid }"
                    :error-messages="errors"
                    :success="valid"
                    label="Name"
                    hint="Name of individual."
                    clearable
                    required
                  />
                </ValidationProvider>
              </v-flex>
              <v-flex xs12>
                <ValidationProvider name="Email" rules="required" immediate>
                  <v-text-field
                    v-model="email"
                    slot-scope="{ errors, valid }"
                    label="Email"
                    :error-messages="errors"
                    :success="valid"
                    hint="Individual's email address."
                    clearable
                    required
                  />
                </ValidationProvider>
              </v-flex>
              <v-flex xs12>
                <ValidationProvider name="Company" immediate>
                  <v-text-field
                    v-model="company"
                    slot-scope="{ errors, valid }"
                    label="Company"
                    :error-messages="errors"
                    :success="valid"
                    hint="Individual's company."
                    clearable
                  />
                </ValidationProvider>
              </v-flex>
              <v-flex xs12>
                <ValidationProvider name="ExternalId" immediate>
                  <v-text-field
                    v-model="external_id"
                    slot-scope="{ errors, valid }"
                    label="External Id"
                    :error-messages="errors"
                    :success="valid"
                    hint="Individual's external ID."
                    clearable
                  />
                </ValidationProvider>
              </v-flex>
              <v-flex xs12>
                <span class="text-subtitle-2"
                  >Engagement
                  <v-tooltip max-width="250px" location="bottom">
                    <template #activator="{ on, attrs }">
                      <v-icon v-bind="attrs" v-on="on"> help_outline </v-icon>
                    </template>
                    This individual will be automatically engaged for any incident or case matching
                    the following filters.
                  </v-tooltip>
                </span>
              </v-flex>
              <v-flex xs12>
                <search-filter-combobox
                  v-model="filters"
                  :project="project"
                  label="Filters"
                  hint="Select one or more filters that will determine when the individual is engaged."
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
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import { ValidationObserver, ValidationProvider, extend } from "vee-validate"
import { required } from "vee-validate/dist/rules"
import SearchFilterCombobox from "@/search/SearchFilterCombobox.vue"

extend("required", {
  ...required,
  message: "This field is required",
})

export default {
  name: "IndividualNewEditSheet",

  data() {
    return {
      visibilities: ["Open"],
    }
  },

  components: {
    ValidationObserver,
    ValidationProvider,
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
