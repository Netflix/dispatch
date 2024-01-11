<template>
  <v-dialog v-model="showCreateEdit" persistent max-width="600px">
    <v-form @submit.prevent v-slot="{ isValid }">
      <v-card>
        <v-card-title>
          <span class="text-h5" v-if="id">Edit Organization</span>
          <span class="text-h5" v-else>Create an Organization</span>
        </v-card-title>
        <v-card-text>
          Organizations represent the top-level in your hierarchy. You'll be able to bundle a
          collection of projects within an organization.
          <v-text-field
            v-if="id"
            v-model="name"
            name="Name"
            label="Name"
            hint="A name for your organization. Note: it can't be modified once the organization has been created."
            disabled
          />
          <v-text-field
            v-else
            v-model="name"
            name="Name"
            label="Name"
            hint="A name for your organization. Note: it can't be modified once the organization has been created."
            clearable
            required
            :rules="[rules.required]"
          />
          <v-textarea
            v-model="description"
            label="Description"
            hint="A short description for your organization."
            clearable
            auto-grow
            required
            name="Description"
            :rules="[rules.required]"
          />
        </v-card-text>
        <v-list-item-title class="text-subtitle-2 ml-4">
          Banner Settings
          <v-tooltip max-width="250px" location="bottom">
            <template #activator="{ props }">
              <v-icon v-bind="props">mdi-help-circle-outline</v-icon>
            </template>
            When enabled, this banner will be presented to users throughout the application when
            using this organization.
          </v-tooltip>
        </v-list-item-title>
        <v-card-text>
          <v-textarea
            v-model="banner_text"
            label="Text"
            hint="Any information you would like to include in an organizational banner."
            clearable
            auto-grow
            required
            name="text"
          />
          <color-picker-input label="Color" v-model="banner_color" />
          <v-checkbox v-model="banner_enabled" label="Enabled" />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="closeCreateEditDialog()"> Cancel </v-btn>
          <v-btn
            v-if="id"
            color="info"
            variant="text"
            @click="save()"
            :loading="loading"
            :disabled="!isValid.value"
          >
            Update
          </v-btn>
          <v-btn
            v-else
            color="info"
            variant="text"
            @click="save()"
            :loading="loading"
            :disabled="!isValid.value"
          >
            Create
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-form>
  </v-dialog>
</template>

<script>
import { required } from "@/util/form"

import { mapActions } from "vuex"
import { mapFields } from "vuex-map-fields"

import ColorPickerInput from "@/components/ColorPickerInput.vue"

export default {
  setup() {
    return {
      rules: { required },
    }
  },
  name: "OrganizationCreateEditDialog",

  components: {
    ColorPickerInput,
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
