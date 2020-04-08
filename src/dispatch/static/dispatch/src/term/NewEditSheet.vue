<template>
  <v-navigation-drawer v-model="showCreateEdit" app clipped right width="500">
    <template v-slot:prepend>
      <v-list-item two-line>
        <v-list-item-content>
          <v-list-item-title v-if="id" class="title">
            Edit
          </v-list-item-title>
          <v-list-item-title v-else class="title">
            New
          </v-list-item-title>
          <v-list-item-subtitle>Term</v-list-item-subtitle>
        </v-list-item-content>
      </v-list-item>
    </template>
    <ValidationObserver>
      <v-card slot-scope="{ invalid, validated }" flat>
        <v-card-text>
          <v-container grid-list-md>
            <v-layout wrap>
              <v-flex xs12>
                <ValidationProvider name="Text" rules="required" immediate>
                  <v-text-field
                    v-model="text"
                    slot-scope="{ errors, valid }"
                    :error-messages="errors"
                    :success="valid"
                    label="Text"
                    hint="A word or phrase."
                    clearable
                    auto-grow
                    required
                  />
                </ValidationProvider>
              </v-flex>
              <v-flex xs12>
                <definition-combobox v-model="definitions" />
              </v-flex>
            </v-layout>
          </v-container>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn color="secondary" @click="closeCreateEdit()">
            Cancel
          </v-btn>
          <v-btn
            color="primary"
            :disabled="invalid || !validated"
            :loading="loading"
            @click="save()"
          >
            Save
          </v-btn>
        </v-card-actions>
      </v-card>
    </ValidationObserver>
  </v-navigation-drawer>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import { ValidationObserver, ValidationProvider } from "vee-validate"
import DefinitionCombobox from "@/definition/DefinitionCombobox.vue"
export default {
  name: "TermNewEditSheet",

  components: {
    ValidationObserver,
    ValidationProvider,
    DefinitionCombobox
  },
  computed: {
    ...mapFields("term", [
      "selected.text",
      "selected.definitions",
      "selected.id",
      "selected.loading",
      "dialogs.showCreateEdit"
    ])
  },

  methods: {
    ...mapActions("term", ["save", "closeCreateEdit"])
  }
}
</script>
