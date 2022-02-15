<template>
  <ValidationObserver v-slot="{ invalid, validated }">
    <v-navigation-drawer v-model="showCreateEdit" app clipped right width="800">
      <template v-slot:prepend>
        <v-list-item two-line>
          <v-list-item-content>
            <v-list-item-title class="title"> New </v-list-item-title>
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
          <v-btn icon color="secondary" @click="closeCreateEdit">
            <v-icon>close</v-icon>
          </v-btn>
        </v-list-item>
        <v-card flat>
          <v-card-text>
            <v-container grid-list-md>
              <v-layout wrap>
                <v-flex xs12>
                  <ValidationProvider name="Name" rules="required" immediate>
                    <v-text-field
                      v-model="environment.name"
                      slot-scope="{ errors, valid }"
                      :error-messages="errors"
                      :success="valid"
                      label="Name"
                      hint="Name of environment."
                      clearable
                      required
                    />
                  </ValidationProvider>
                </v-flex>
                <v-flex xs12>
                  <ValidationProvider name="Description" rules="required" immediate>
                    <v-textarea
                      v-model="environment.description"
                      slot-scope="{ errors, valid }"
                      :error-messages="errors"
                      :success="valid"
                      label="Description"
                      hint="Description of environment."
                      clearable
                      required
                    />
                  </ValidationProvider>
                </v-flex>
              </v-layout>
            </v-container>
          </v-card-text>
        </v-card>
      </template>
    </v-navigation-drawer>
  </ValidationObserver>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import { ValidationProvider, ValidationObserver, extend } from "vee-validate"
import { required } from "vee-validate/dist/rules"

extend("required", {
  ...required,
  message: "This field is required",
})

export default {
  name: "SourceEnvironmentNewEditSheet",

  components: {
    ValidationProvider,
    ValidationObserver,
  },

  computed: {
    ...mapFields("sourceEnvironment", [
      "selected.environment",
      "selected.loading",
      "dialogs.showCreateEdit",
    ]),
  },

  methods: {
    ...mapActions("sourceEnvironment", ["closeCreateEdit"]),
    save() {
      const self = this
      this.$store.dispatch("sourceEnvironment/save").then(function (data) {
        self.$emit("new-source-environment-created", data)
      })
    },
  },

  data() {
    return {}
  },

  created() {},
}
</script>
