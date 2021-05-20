<template>
  <v-dialog v-model="showCreate" persistent max-width="800px">
    <ValidationObserver disabled v-slot="{ invalid, validated }">
      <v-card>
        <v-card-title>
          <span class="headline">Create a New Organization</span>
        </v-card-title>
        <v-card-text>
          Organizations represent the top level in your hierarchy. You'll be able to bundle a
          collection of projects within an organization.
          <ValidationProvider name="Name" rules="required" immediate>
            <v-text-field
              v-model="name"
              label="Name"
              hint="A name for your saved search."
              slot-scope="{ errors, valid }"
              :error-messages="errors"
              :success="valid"
              clearable
              required
            />
          </ValidationProvider>
          <ValidationProvider name="Description" rules="required" immediate>
            <v-textarea
              v-model="description"
              label="Description"
              hint="A short description."
              slot-scope="{ errors, valid }"
              :error-messages="errors"
              :success="valid"
              clearable
              auto-grow
              required
            />
          </ValidationProvider>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="closeCreateDialog()"> Cancel </v-btn>
          <v-btn
            color="info"
            text
            @click="save()"
            :loading="loading"
            :disabled="invalid || !validated"
          >
            Create
          </v-btn>
        </v-card-actions>
      </v-card>
    </ValidationObserver>
  </v-dialog>
</template>

<script>
import { ValidationObserver, ValidationProvider, extend } from "vee-validate"
import { required } from "vee-validate/dist/rules"

import { mapActions } from "vuex"
import { mapFields } from "vuex-map-fields"

extend("required", {
  ...required,
  message: "This field is required",
})

export default {
  name: "OrganizationDeleteDialog",
  data() {
    return {}
  },
  components: {
    ValidationObserver,
    ValidationProvider,
  },
  computed: {
    ...mapFields("organization", [
      "selected.name",
      "selected.description",
      "loading",
      "dialogs.showCreate",
    ]),
  },

  methods: {
    ...mapActions("organization", ["save", "closeCreateDialog"]),
  },
}
</script>
