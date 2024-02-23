<template>
  <v-form @submit.prevent v-slot="{ isValid }">
    <v-navigation-drawer v-model="showCreateEdit" location="right" width="500">
      <template #prepend>
        <v-list-item lines="two">
          <v-list-item-title v-if="id" class="text-h6"> Edit </v-list-item-title>
          <v-list-item-title v-else class="text-h6"> New </v-list-item-title>
          <v-list-item-subtitle>Tag Type</v-list-item-subtitle>

          <template #append>
            <v-btn
              icon
              variant="text"
              color="info"
              :loading="loading"
              :disabled="!isValid.value"
              @click="save()"
            >
              <v-icon>mdi-content-save</v-icon>
            </v-btn>
            <v-btn icon variant="text" color="secondary" @click="closeCreateEdit()">
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </template>
        </v-list-item>
      </template>
      <v-card>
        <v-card-text>
          <v-container>
            <v-row>
              <v-col cols="12">
                <span class="text-subtitle-2">Details</span>
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="name"
                  label="Name"
                  hint="A name for your tag type."
                  clearable
                  required
                  name="Name"
                  :rules="[rules.required]"
                />
              </v-col>
              <v-col cols="12">
                <v-textarea
                  v-model="description"
                  label="Description"
                  hint="A description for your tag type."
                  clearable
                  required
                  name="Description"
                />
              </v-col>
              <v-col cols="12">
                <color-picker-input v-model="color" default="#000000" />
              </v-col>
              <v-col cols="12">
                <icon-picker-input v-model="icon" :color="color" />
              </v-col>
              <v-divider class="mb-2" />
              <v-col cols="5">
                <span class="text-body-1">Discoverablitity</span>
              </v-col>
              <v-col cols="7">
                <v-tooltip max-width="500px" open-delay="50" location="bottom">
                  <template #activator="{ props }">
                    <v-icon v-bind="props">mdi-information</v-icon>
                  </template>
                  <span>
                    If activated, this tag type will be visible in tag selection boxes for these
                    entities.
                  </span>
                </v-tooltip>
              </v-col>
              <v-col cols="12">
                <v-checkbox
                  class="discoverable_checkbox"
                  v-model="discoverable_incident"
                  hide-details
                  label="Incidents"
                  hint="Should this type be visible in incidents?"
                />
                <v-checkbox
                  class="discoverable_checkbox"
                  v-model="discoverable_case"
                  hide-details
                  label="Cases"
                  hint="Should this type be visible in cases?"
                />
                <v-checkbox
                  class="discoverable_checkbox"
                  v-model="discoverable_query"
                  hide-details
                  label="Queries"
                  hint="Should this type be visible in queries?"
                />
                <v-checkbox
                  class="discoverable_checkbox"
                  v-model="discoverable_signal"
                  hide-details
                  label="Signals"
                  hint="Should this type be visible in signals?"
                />
                <v-checkbox
                  class="discoverable_checkbox"
                  v-model="discoverable_source"
                  hide-details
                  label="Sources"
                  hint="Should this type be visible in sources?"
                />
              </v-col>
              <v-divider />
              <v-col cols="5">
                <v-checkbox
                  v-model="exclusive"
                  label="Exclusive"
                  hint="Should an incident only have one tag of this type?"
                />
              </v-col>
              <v-col cols="7">
                <v-tooltip max-width="500px" open-delay="50" location="bottom">
                  <template #activator="{ props }">
                    <v-icon class="mt-4" v-bind="props">mdi-information</v-icon>
                  </template>
                  <span>
                    If activated, only one tag of this type is allowed per discoverable type.
                  </span>
                </v-tooltip>
              </v-col>
              <v-col cols="5">
                <v-checkbox
                  v-model="required"
                  label="Required"
                  hint="Is this tag type required for new entities of the discoverable types?"
                />
              </v-col>
              <v-col cols="7">
                <v-tooltip max-width="500px" open-delay="50" location="bottom">
                  <template #activator="{ props }">
                    <v-icon class="mt-4" v-bind="props">mdi-information</v-icon>
                  </template>
                  <span>
                    If activated, at least one tag of this type is required per discoverable type.
                  </span>
                </v-tooltip>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
      </v-card>
    </v-navigation-drawer>
  </v-form>
</template>

<script>
import { required } from "@/util/form"
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

import ColorPickerInput from "@/components/ColorPickerInput.vue"
import IconPickerInput from "@/components/IconPickerInput.vue"

export default {
  setup() {
    return {
      rules: { required },
    }
  },
  name: "TagTypeNewEditSheet",

  components: {
    ColorPickerInput,
    IconPickerInput,
  },

  computed: {
    ...mapFields("tag_type", [
      "dialogs.showCreateEdit",
      "selected.id",
      "selected.name",
      "selected.project",
      "selected.description",
      "selected.discoverable_incident",
      "selected.discoverable_case",
      "selected.discoverable_query",
      "selected.discoverable_signal",
      "selected.discoverable_source",
      "selected.icon",
      "selected.color",
      "selected.exclusive",
      "selected.required",
      "selected.loading",
    ]),
    ...mapFields("tag_type", {
      default_tag_type: "selected.default",
    }),
  },

  methods: {
    ...mapActions("tag_type", ["save", "closeCreateEdit"]),
  },

  created() {
    if (this.$route.query.project) {
      this.project = { name: this.$route.query.project }
    }
  },
}
</script>

<style scoped>
.discoverable_checkbox {
  margin-top: -20px;
}
</style>
