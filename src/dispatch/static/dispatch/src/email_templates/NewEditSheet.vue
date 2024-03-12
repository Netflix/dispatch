<template>
  <v-form @submit.prevent v-slot="{ isValid }">
    <v-navigation-drawer v-model="showCreateEdit" location="right" width="500">
      <template #prepend>
        <v-list-item lines="two">
          <v-list-item-title v-if="id" class="text-h6"> Edit </v-list-item-title>
          <v-list-item-title v-else class="text-h6"> New </v-list-item-title>
          <v-list-item-subtitle>Email Template</v-list-item-subtitle>

          <template #append>
            <v-btn
              icon
              variant="text"
              color="info"
              :loading="loading"
              :disabled="!isValid.value"
              @click="saveLocal()"
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
                <v-select
                  v-model="email_template_type"
                  :items="['Incident Welcome Email']"
                  :menu-props="{ maxHeight: '400' }"
                  label="Email template type"
                  clearable
                  chips
                  :rules="[rules.required]"
                />
              </v-col>
              <v-col cols="12">
                <v-textarea
                  v-model="welcome_text"
                  label="Welcome text"
                  hint="To insert the name of the incident, use {{name}}"
                  clearable
                  name="Welcome text"
                />
              </v-col>
              <v-col cols="12">
                <v-textarea
                  v-model="welcome_body"
                  label="Welcome body"
                  hint="To insert the name of the incident, use {{name}}"
                  clearable
                  name="Welcome body"
                />
              </v-col>
              <v-col cols="12">
                <v-checkbox
                  v-model="enabled"
                  label="Enabled"
                  hint="Whether this form type is enabled."
                />
              </v-col>
              <v-col cols="12">
                <v-select
                  v-model="local_components"
                  :items="[
                    'Title',
                    'Description',
                    'Visibility',
                    'Status',
                    'Type',
                    'Severity',
                    'Priority',
                    'Reporter',
                    'Commander',
                    'Investigation Document',
                    'Storage',
                    'Conference',
                    'Slack Commands',
                    'FAQ Document',
                  ]"
                  multiple
                  :menu-props="{ maxHeight: '400' }"
                  label="Email components"
                  closable-chips
                  chips
                />
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

export default {
  setup() {
    return {
      rules: { required },
    }
  },
  name: "EmailTemplatesNewEditSheet",

  data: () => ({
    local_components: [],
  }),

  computed: {
    ...mapFields("email_templates", [
      "selected.email_template_type",
      "selected.welcome_text",
      "selected.welcome_body",
      "selected.components",
      "selected.id",
      "selected.project",
      "selected.enabled",
      "dialogs.showCreateEdit",
    ]),
  },

  methods: {
    ...mapActions("email_templates", ["save", "closeCreateEdit"]),
    saveLocal() {
      this.components = JSON.stringify(this.local_components)
      this.save()
    },
  },

  created() {
    if (this.$route.query.project) {
      this.project = { name: this.$route.query.project }
    }

    this.$watch(
      (vm) => [vm.components],
      () => {
        this.local_components = JSON.parse(this.components)
      }
    )
  },
}
</script>

<style>
.mdi-school {
  color: white !important;
}
</style>
