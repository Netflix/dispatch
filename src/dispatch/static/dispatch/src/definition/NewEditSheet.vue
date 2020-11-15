<template>
  <ValidationObserver v-slot="{ invalid, validated }">
    <v-navigation-drawer v-model="showCreateEdit" app clipped right width="500">
      <template v-slot:prepend>
        <v-list-item two-line>
          <v-list-item-content>
            <v-list-item-title v-if="id" class="title">Edit</v-list-item-title>
            <v-list-item-title v-else class="title">New</v-list-item-title>
            <v-list-item-subtitle>Definition</v-list-item-subtitle>
          </v-list-item-content>
          <v-btn
            icon
            color="primary"
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
                <ValidationProvider name="Text" rules="required" immediate>
                  <v-textarea
                    v-model="text"
                    slot-scope="{ errors, valid }"
                    :error-messages="errors"
                    :success="valid"
                    label="Text"
                    hint="A short description."
                    clearable
                    auto-grow
                    required
                  />
                </ValidationProvider>
              </v-flex>
              <v-flex xs12>
                <term-combobox v-model="terms" />
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
import TermCombobox from "@/term/TermCombobox.vue"

extend("required", {
  ...required,
  message: "This field is required"
})

export default {
  name: "DefinitionNewEditSheet",

  components: {
    ValidationObserver,
    ValidationProvider,
    TermCombobox
  },

  computed: {
    ...mapFields("definition", [
      "selected.text",
      "selected.terms",
      "selected.id",
      "selected.loading",
      "dialogs.showCreateEdit"
    ])
  },

  methods: {
    ...mapActions("definition", ["save", "closeCreateEdit"])
  }
}
</script>
