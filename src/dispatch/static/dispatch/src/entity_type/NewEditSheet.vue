<template>
  <ValidationObserver v-slot="{ invalid, validated }">
    <v-navigation-drawer v-model="showCreateEdit" app clipped right width="500">
      <template v-slot:prepend>
        <v-list-item two-line>
          <v-list-item-content>
            <v-list-item-title v-if="id" class="title"> Edit </v-list-item-title>
            <v-list-item-title v-else class="title"> New </v-list-item-title>
            <v-list-item-subtitle>Entity Type</v-list-item-subtitle>
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
          <v-container grid-list-md>
            <v-layout wrap>
              <v-flex xs12>
                <span class="subtitle-2">Details</span>
              </v-flex>
              <v-flex xs12>
                <ValidationProvider name="Name" rules="required" immediate>
                  <v-text-field
                    v-model="name"
                    slot-scope="{ errors, valid }"
                    :error-messages="errors"
                    :success="valid"
                    label="Name"
                    hint="A name for your entity type."
                    clearable
                    required
                  />
                </ValidationProvider>
              </v-flex>
              <v-flex xs12>
                <ValidationProvider name="Description" immediate>
                  <v-textarea
                    v-model="description"
                    slot-scope="{ errors, valid }"
                    label="Description"
                    :error-messages="errors"
                    :success="valid"
                    hint="A description for your entity type."
                    clearable
                  />
                </ValidationProvider>
              </v-flex>
              <v-flex xs12>
                <ValidationProvider rules="regexp" name="Regular Expression" immediate>
                  <v-textarea
                    v-model="regular_expression"
                    slot-scope="{ errors, valid }"
                    label="Regular Expression"
                    :error-messages="errors"
                    :success="valid"
                    hint="A regular expression pattern for your entity type. Multiple capture groups are not supported, the first group will be used."
                    clearable
                  />
                </ValidationProvider>
              </v-flex>
              <v-flex xs12>
                <ValidationProvider rules="jsonpath" name="Field" immediate>
                  <v-text-field
                    v-model="field"
                    slot-scope="{ errors, valid }"
                    :error-messages="errors"
                    :success="valid"
                    label="Field"
                    hint="The field where the entity will be present. Accepts JSONPath expressions."
                    clearable
                  />
                </ValidationProvider>
              </v-flex>
              <v-flex xs12>
                <v-checkbox
                  v-model="enabled"
                  label="Enabled"
                >
                </v-checkbox>
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
import jsonpath from "jsonpath";


extend("required", {
  ...required,
  message: "This field is required.",
})

extend('regexp', {
  validate(value) {
    try {
      new RegExp(value);
      return true;
    } catch (e) {
      return false;
    }
  },
  message: 'Must be a valid regular expression pattern.'
});

extend('jsonpath', {
  validate(value) {
    try {
      jsonpath.parse(value);
      return true;
    } catch (e) {
      return false;
    }
  },
  message: 'Must be a valid JSONPath expression.'
});

export default {
  name: "EntityTypeNewEditSheet",

  components: {
    ValidationObserver,
    ValidationProvider,
  },

  computed: {
    ...mapFields("entity_type", [
      "dialogs.showCreateEdit",
      "selected.id",
      "selected.name",
      "selected.description",
      "selected.field",
      "selected.project",
      "selected.regular_expression",
      "selected.enabled",
      "selected.loading",
    ]),
    ...mapFields("entity_type", {
      default_entity: "selected.default",
    }),
    ...mapFields("route", ["query"]),
  },

  methods: {
    ...mapActions("entity_type", ["save", "closeCreateEdit"]),
  },

  created() {
    if (this.query.project) {
      this.project = { name: this.query.project }
    }
  },
}
</script>

<style>
  .checkbox-tooltip-container {
    display: flex;
    align-items: center;
  }

  .checkbox-tooltip-container .v-icon {
    margin-left: 0rem;
    margin-top: -0rem;
  }
</style>
