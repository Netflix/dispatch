<template>
  <ValidationObserver v-slot="{ invalid, validated }">
    <v-navigation-drawer v-model="showCreateEdit" app clipped right width="500">
      <template v-slot:prepend>
        <v-list-item two-line>
          <v-list-item-content>
            <v-list-item-title v-if="id" class="title"> Edit </v-list-item-title>
            <v-list-item-title v-else class="title"> New </v-list-item-title>
            <v-list-item-subtitle>Signal</v-list-item-subtitle>
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
          <v-container>
            <v-row>
              <v-col cols="12">
                <span class="subtitle-2">Details</span>
              </v-col>
              <v-col cols="12">
                <ValidationProvider name="Name" rules="required" immediate>
                  <v-text-field
                    v-model="name"
                    slot-scope="{ errors, valid }"
                    :error-messages="errors"
                    :success="valid"
                    label="Name"
                    hint="A name for your signal."
                    clearable
                    required
                  />
                </ValidationProvider>
              </v-col>
              <v-col cols="12">
                <ValidationProvider name="Description" immediate>
                  <v-textarea
                    v-model="description"
                    slot-scope="{ errors, valid }"
                    label="Description"
                    :error-messages="errors"
                    :success="valid"
                    hint="A description for your signal."
                    clearable
                  />
                </ValidationProvider>
              </v-col>
              <v-col cols="12">
                <ValidationProvider name="owner" rules="required" immediate>
                  <v-text-field
                    v-model="owner"
                    slot-scope="{ errors, valid }"
                    :error-messages="errors"
                    :success="valid"
                    label="Owner"
                    hint="A owner for your signal."
                    clearable
                  />
                </ValidationProvider>
              </v-col>
              <v-col cols="12">
                <ValidationProvider name="variant" rules="required" immediate>
                  <v-text-field
                    v-model="variant"
                    slot-scope="{ errors, valid }"
                    :error-messages="errors"
                    :success="valid"
                    label="Variant"
                    hint="A variant for your signal."
                    clearable
                  />
                </ValidationProvider>
              </v-col>
              <v-col cols="12">
                <ValidationProvider name="externalUrl" rules="required" immediate>
                  <v-text-field
                    v-model="variant"
                    slot-scope="{ errors, valid }"
                    :error-messages="errors"
                    :success="valid"
                    label="Variant"
                    hint="A variant for your signal."
                    clearable
                  />
                </ValidationProvider>
              </v-col>
              <v-col cols="12">
                <ValidationProvider name="variant" rules="required" immediate>
                  <v-text-field
                    v-model="variant"
                    slot-scope="{ errors, valid }"
                    :error-messages="errors"
                    :success="valid"
                    label="Variant"
                    hint="A variant for your signal."
                    clearable
                  />
                </ValidationProvider>
              </v-col>
            </v-row>
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

export default {
  name: "SignalNewEditSheet",

  components: {
    ValidationObserver,
    ValidationProvider,
  },

  computed: {
    ...mapFields("signal", [
      "dialogs.showCreateEdit",
      "selected.id",
      "selected.name",
      "selected.project",
      "selected.description",
      "selected.loading",
    ]),
    ...mapFields("route", ["query"]),
  },

  methods: {
    ...mapActions("signal", ["save", "closeCreateEdit"]),
  },

  created() {
    if (this.query.project) {
      this.project = { name: this.query.project }
    }
  },
}
</script>
