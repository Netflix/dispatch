<template>
  <v-form @submit.prevent v-slot="{ isValid }">
    <v-navigation-drawer v-model="showCreateEdit" location="right" width="500">
      <template #prepend>
        <v-list-item lines="two">
          <v-list-item-title v-if="id" class="text-h6"> Edit </v-list-item-title>
          <v-list-item-title v-else class="text-h6"> New </v-list-item-title>
          <v-list-item-subtitle>AI Prompt</v-list-item-subtitle>

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
                <v-select
                  v-model="genai_type"
                  label="GenAI Type"
                  hint="Select the type of AI prompt"
                  :items="genaiTypeOptions"
                  item-title="text"
                  item-value="value"
                  clearable
                  required
                  name="GenAI Type"
                  :rules="[rules.required]"
                />
              </v-col>
              <v-col cols="12">
                <v-textarea
                  v-model="genai_prompt"
                  label="Prompt"
                  hint="The main prompt template to send to the AI model. Use placeholders like {tags}, {incident_data}, etc."
                  clearable
                  auto-grow
                  rows="6"
                  required
                  name="Prompt"
                  :rules="[rules.required]"
                />
              </v-col>
              <v-col cols="12">
                <v-textarea
                  v-model="genai_system_message"
                  label="System Message"
                  hint="The system message to set the behavior of the AI assistant"
                  clearable
                  auto-grow
                  rows="4"
                />
              </v-col>
            </v-row>
            <v-col>
              <v-checkbox
                v-model="enabled"
                label="Enabled"
                hint="Is this prompt active and available for use? Only one prompt per type can be enabled."
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
import { getGenaiTypeOptions } from "@/constants/genai-types"

export default {
  setup() {
    return {
      rules: { required },
    }
  },
  name: "PromptNewEditSheet",

  computed: {
    ...mapFields("prompt", [
      "selected.genai_type",
      "selected.genai_prompt",
      "selected.genai_system_message",
      "selected.enabled",
      "selected.project",
      "selected.id",
      "selected.loading",
      "dialogs.showCreateEdit",
    ]),
    genaiTypeOptions() {
      return getGenaiTypeOptions()
    },
  },

  methods: {
    ...mapActions("prompt", ["save", "closeCreateEdit"]),
  },

  created() {
    if (this.$route.query.project) {
      this.project = { name: this.$route.query.project }
    }
  },
}
</script>
