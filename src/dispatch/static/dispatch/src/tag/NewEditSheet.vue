<template>
  <ValidationObserver v-slot="{ invalid, validated }">
    <v-navigation-drawer v-model="showCreateEdit" app clipped right width="500">
      <template v-slot:prepend>
        <v-list-item two-line>
          <v-list-item-content>
            <v-list-item-title v-if="id" class="title">Edit</v-list-item-title>
            <v-list-item-title v-else class="title">New</v-list-item-title>
            <v-list-item-subtitle>Tag</v-list-item-subtitle>
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
                <span class="subtitle-2">Details</span>
              </v-flex>
              <v-flex xs12>
                <ValidationProvider name="name" rules="required" immediate>
                  <v-text-field
                    v-model="name"
                    slot-scope="{ errors, valid }"
                    :error-messages="errors"
                    :success="valid"
                    label="Name"
                    hint="A name for your tag."
                    clearable
                    required
                  />
                </ValidationProvider>
              </v-flex>
              <v-flex xs12>
                <tag-type-select v-model="tag_type" />
              </v-flex>
              <v-flex xs12>
                <ValidationProvider name="source" immediate>
                  <v-text-field
                    v-model="source"
                    slot-scope="{ errors, valid }"
                    :error-messages="errors"
                    :success="valid"
                    label="Source"
                    hint="Tag's source."
                    clearable
                    required
                  />
                </ValidationProvider>
              </v-flex>
              <v-flex xs12>
                <ValidationProvider name="uri" immediate>
                  <v-text-field
                    v-model="uri"
                    slot-scope="{ errors, valid }"
                    :error-messages="errors"
                    :success="valid"
                    label="URI"
                    hint="Tag's URI."
                    clearable
                    required
                  />
                </ValidationProvider>
              </v-flex>
              <v-flex xs12>
                <ValidationProvider name="description" immediate>
                  <v-textarea
                    v-model="description"
                    slot-scope="{ errors, valid }"
                    label="Description"
                    :error-messages="errors"
                    :success="valid"
                    hint="The tag's description."
                    clearable
                    required
                  />
                </ValidationProvider>
              </v-flex>
              <v-flex>
                <v-checkbox
                  v-model="discoverable"
                  label="Discoverable"
                  hint="Is this tag a common word or is it eligible for auto-detection?"
                ></v-checkbox>
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
import TagTypeSelect from "@/tag_type/TagTypeSelect.vue"

extend("required", {
  ...required,
  message: "This field is required"
})

export default {
  name: "TagNewEditSheet",

  components: {
    ValidationObserver,
    ValidationProvider,
    TagTypeSelect
  },

  computed: {
    ...mapFields("tag", [
      "selected.name",
      "selected.id",
      "selected.tag_type",
      "selected.uri",
      "selected.description",
      "selected.source",
      "selected.discoverable",
      "selected.loading",
      "dialogs.showCreateEdit"
    ])
  },

  methods: {
    ...mapActions("tag", ["save", "closeCreateEdit"])
  }
}
</script>
