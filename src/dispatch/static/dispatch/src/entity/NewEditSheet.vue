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
                    hint="A name for your entity."
                    clearable
                    required
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
                    hint="A regular expression pattern for your entity."
                    clearable
                    required
                  />
                </ValidationProvider>
              </v-flex>
              <v-flex class="checkbox-tooltip-container">
                <v-checkbox
                  v-model="global_find"
                  label="Global"
                >
                </v-checkbox>
                <v-tooltip bottom>
                  <template v-slot:activator="{ on }">
                    <v-icon v-on="on" small class="ml-2">mdi-information</v-icon>
                  </template>
                  <span>Checking this box collect the entity from all signals.</span>
                </v-tooltip>
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

export default {
  name: "EntityNewEditSheet",

  components: {
    ValidationObserver,
    ValidationProvider,
  },

  computed: {
    ...mapFields("entity", [
      "dialogs.showCreateEdit",
      "selected.id",
      "selected.name",
      "selected.description",
      "selected.project",
      "selected.regular_expression",
      "selected.global_find",
      "selected.loading",
    ]),
    ...mapFields("entity", {
      default_entity: "selected.default",
    }),
    ...mapFields("route", ["query"]),
  },

  methods: {
    ...mapActions("entity", ["save", "closeCreateEdit"]),
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
