<template>
  <v-dialog v-model="showCreateEdit" persistent max-width="600px">
    <ValidationObserver disabled v-slot="{ invalid, validated }">
      <v-card>
        <v-card-title>
          <span class="headline" v-if="id">Edit Organization</span>
          <span class="headline" v-else>Create an Organization</span>
        </v-card-title>
        <v-card-text>
          Organizations represent the top-level in your hierarchy. You'll be able to bundle a
          collection of projects within an organization.
          <ValidationProvider name="Name" rules="required" immediate>
            <v-text-field
              v-if="id"
              v-model="name"
              label="Name"
              hint="A name for your organization. Note: it can't be modified once the organization has been created."
              slot-scope="{ errors, valid }"
              :error-messages="errors"
              :success="valid"
              disabled
            />
            <v-text-field
              v-else
              v-model="name"
              label="Name"
              hint="A name for your organization. Note: it can't be modified once the organization has been created."
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
              hint="A short description for your organization."
              slot-scope="{ errors, valid }"
              :error-messages="errors"
              :success="valid"
              clearable
              auto-grow
              required
            />
          </ValidationProvider>
        </v-card-text>
        <v-list-item-title class="subtitle-2 ml-4">
          Banner Settings
          <v-tooltip max-width="250px" bottom>
            <template v-slot:activator="{ on, attrs }">
              <v-icon v-bind="attrs" v-on="on"> help_outline </v-icon>
            </template>
            When enabled, this banner will be presented to users throughout the application when
            using this organization.
          </v-tooltip>
        </v-list-item-title>
        <v-card-text>
          <ValidationProvider name="text" immediate>
            <v-textarea
              v-model="banner_text"
              label="Text"
              hint="Any information you would like to include in an organizational banner."
              slot-scope="{ errors, valid }"
              :error-messages="errors"
              :success="valid"
              clearable
              auto-grow
              required
            />
          </ValidationProvider>
          <color-picker-input label="Color" v-model="banner_color"></color-picker-input>
          <v-checkbox v-model="banner_enabled" label="Enabled" />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="closeCreateEditDialog()"> Cancel </v-btn>
          <v-btn
            v-if="id"
            color="info"
            text
            @click="save()"
            :loading="loading"
            :disabled="invalid || !validated"
          >
            Update
          </v-btn>
          <v-btn
            v-else
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
import { mapActions } from "vuex"
import { mapFields } from "vuex-map-fields"
import { required } from "vee-validate/dist/rules"

import ColorPickerInput from "@/components/ColorPickerInput.vue"

extend("required", {
  ...required,
  message: "This field is required",
})

export default {
  name: "OrganizationCreateEditDialog",

  components: {
    ColorPickerInput,
    ValidationObserver,
    ValidationProvider,
  },

  data() {
    return {}
  },

  computed: {
    ...mapFields("organization", [
      "selected.id",
      "selected.name",
      "selected.description",
      "selected.banner_text",
      "selected.banner_color",
      "selected.banner_enabled",
      "selected.loading",
      "dialogs.showCreateEdit",
    ]),
  },

  methods: {
    ...mapActions("organization", ["save", "closeCreateEditDialog"]),
  },
}
</script>
