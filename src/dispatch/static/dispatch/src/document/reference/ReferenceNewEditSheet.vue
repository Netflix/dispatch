<template>
  <v-form @submit.prevent v-slot="{ isValid }">
    <v-navigation-drawer v-model="showCreateEdit" location="right" width="500">
      <template #prepend>
        <v-list-item lines="two">
          <v-list-item-title v-if="id" class="text-h6"> Edit </v-list-item-title>
          <v-list-item-title v-else class="text-h6"> New </v-list-item-title>
          <v-list-item-subtitle>Reference</v-list-item-subtitle>

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
                  hint="A name for your reference."
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
                  hint="A description for your reference."
                  clearable
                  required
                  name="description"
                />
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="weblink"
                  label="Weblink"
                  hint="A weblink for the reference."
                  clearable
                  required
                  name="Reference Weblink"
                  :rules="[rules.required]"
                />
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="resource_id"
                  label="External Id"
                  hint="External identifier for document. Used for API integration (e.g. Google doc file id). Typically is the unique id in the weblink."
                  clearable
                  name="Resource Id"
                />
              </v-col>
              <v-col cols="12">
                <span class="text-subtitle-2"
                  >Evergreen
                  <v-tooltip max-width="250px" location="bottom">
                    <template #activator="{ props }">
                      <v-icon v-bind="props">mdi-help-circle-outline</v-icon>
                    </template>
                    Dispatch will send the owner a reminder email to the resource owner, reminding
                    them to keep the resource current.
                  </v-tooltip></span
                >
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="evergreen_owner"
                  label="Owner"
                  hint="Owner of this document."
                  clearable
                  name="Owner"
                />
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="evergreen_reminder_interval"
                  label="Reminder Interval"
                  type="number"
                  hint="Number of days that should elapse between reminders sent to the document owner."
                  placeholder="90"
                  clearable
                  min="1"
                  name="Reminder Interval"
                />
              </v-col>
              <v-col cols="12">
                <v-checkbox
                  v-model="evergreen"
                  hint="Enabling evergreen will send periodic reminders to the owner to update this document."
                  label="Enabled"
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
  name: "ReferenceNewEditSheet",

  computed: {
    ...mapFields("reference", [
      "selected.name",
      "selected.description",
      "selected.resource_type",
      "selected.weblink",
      "selected.resource_id",
      "selected.evergreen_owner",
      "selected.evergreen",
      "selected.evergreen_reminder_interval",
      "selected.project",
      "selected.filters",
      "selected.id",
      "selected.loading",
      "dialogs.showCreateEdit",
    ]),
  },

  methods: {
    ...mapActions("reference", ["closeCreateEdit"]),
    save() {
      const self = this
      this.$store.dispatch("reference/save").then(function (data) {
        self.$emit("new-document-created", data)
      })
    },
  },

  created() {
    if (this.$route.query.project) {
      this.project = { name: this.$route.query.project }
    }
  },
}
</script>
