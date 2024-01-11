<template>
  <v-form @submit.prevent v-slot="{ isValid }">
    <v-navigation-drawer v-model="showCreateEdit" location="right" width="500">
      <template #prepend>
        <v-list-item lines="two">
          <v-list-item-title v-if="id" class="text-h6"> Edit </v-list-item-title>
          <v-list-item-title v-else class="text-h6"> New </v-list-item-title>
          <v-list-item-subtitle>Runbook</v-list-item-subtitle>

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
                  hint="A name for your runbook."
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
                  hint="A description for your runbook."
                  clearable
                  required
                  name="description"
                />
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="weblink"
                  label="Weblink"
                  hint="A weblink for the runbook."
                  clearable
                  required
                  name="Document Weblink"
                  :rules="[rules.required]"
                />
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="resource_id"
                  label="External Id"
                  hint="External identifier for runbook. Used for API integration (e.g. Google doc file id). Typically is the unique id in the weblink."
                  clearable
                  name="Resource Id"
                />
              </v-col>
              <v-col cols="12">
                <span class="text-subtitle-2"
                  >Engagement
                  <v-tooltip max-width="250px" location="bottom">
                    <template #activator="{ props }">
                      <v-icon v-bind="props">mdi-help-circle-outline</v-icon>
                    </template>
                    This runbook will be automatically suggested for any incident matching the
                    following filters.
                  </v-tooltip>
                </span>
              </v-col>
              <v-col cols="12">
                <search-filter-combobox
                  v-model="filters"
                  :project="project"
                  label="Filters"
                  hint="Select one or more filters that will determine when this runbook will be recommended."
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
                  </v-tooltip>
                </span>
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="evergreen_owner"
                  label="Owner"
                  hint="Owner of this runbook."
                  clearable
                  name="Owner"
                />
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="evergreen_reminder_interval"
                  label="Reminder Interval"
                  type="number"
                  hint="Number of days that should elapse between reminders sent to the runbook owner."
                  placeholder="90"
                  clearable
                  min="1"
                  name="Reminder Interval"
                />
              </v-col>
              <v-col cols="12">
                <v-checkbox
                  v-model="evergreen"
                  hint="Enabling evergreen will send periodic reminders to the owner to update this runbook."
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

import SearchFilterCombobox from "@/search/SearchFilterCombobox.vue"

export default {
  setup() {
    return {
      rules: { required },
    }
  },
  name: "DocumentNewEditSheet",

  components: {
    SearchFilterCombobox,
  },

  computed: {
    ...mapFields("runbook", [
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
    ...mapActions("runbook", ["closeCreateEdit"]),
    save() {
      const self = this
      this.$store.dispatch("runbook/save").then(function (data) {
        self.$emit("new-runbook-created", data)
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
