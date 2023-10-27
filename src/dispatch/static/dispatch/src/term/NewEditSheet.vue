<template>
  <v-form @submit.prevent v-slot="{ isValid }">
    <v-navigation-drawer v-model="showCreateEdit" location="right" width="500">
      <template #prepend>
        <v-list-item lines="two">
          <v-list-item-title v-if="id" class="text-h6"> Edit </v-list-item-title>
          <v-list-item-title v-else class="text-h6"> New </v-list-item-title>
          <v-list-item-subtitle>Term</v-list-item-subtitle>

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
                <v-text-field
                  v-model="text"
                  label="Text"
                  hint="A word or phrase."
                  clearable
                  auto-grow
                  required
                  name="Text"
                  :rules="[rules.required]"
                />
              </v-col>
              <v-col cols="12">
                <definition-combobox :project="project" v-model="definitions" />
              </v-col>
            </v-row>
            <v-col>
              <v-checkbox
                v-model="discoverable"
                label="Discoverable"
                hint="Is this term a common word or is it eligible for auto-detection?"
              />
            </v-col>
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

import DefinitionCombobox from "@/definition/DefinitionCombobox.vue"

export default {
  setup() {
    return {
      rules: { required },
    }
  },
  name: "TermNewEditSheet",

  components: {
    DefinitionCombobox,
  },
  computed: {
    ...mapFields("term", [
      "selected.text",
      "selected.definitions",
      "selected.discoverable",
      "selected.project",
      "selected.id",
      "selected.loading",
      "dialogs.showCreateEdit",
    ]),
  },

  methods: {
    ...mapActions("term", ["save", "closeCreateEdit"]),
  },

  created() {
    if (this.$route.query.project) {
      this.project = { name: this.$route.query.project }
    }
  },
}
</script>
