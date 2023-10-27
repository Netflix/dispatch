<template>
  <v-form @submit.prevent v-slot="{ isValid }">
    <v-navigation-drawer v-model="showCreateEdit" location="right" width="500">
      <template #prepend>
        <v-list-item lines="two">
          <v-list-item-title v-if="id" class="text-h6"> Edit </v-list-item-title>
          <v-list-item-title v-else class="text-h6"> New </v-list-item-title>
          <v-list-item-subtitle>Service</v-list-item-subtitle>

          <template #append>
            <v-btn icon variant="text" color="info" :disabled="!isValid.value" @click="save()">
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
                  hint="A name for your service."
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
                  hint="A description for your service."
                  clearable
                  required
                  name="Description"
                  :rules="[rules.required]"
                />
              </v-col>
              <v-col cols="12">
                <v-select
                  v-model="type"
                  :loading="loading"
                  :items="oncall_plugins"
                  label="Type"
                  hint="Oncall plugin to use."
                  name="Type"
                  :rules="[rules.required]"
                />
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="external_id"
                  label="External Id"
                  hint="An external identifier for service."
                  clearable
                  required
                  name="External Id"
                  :rules="[rules.required]"
                />
              </v-col>
              <v-col cols="12">
                <v-checkbox v-model="health_metrics" label="Collect Health Metrics" />
              </v-col>
              <v-col cols="12">
                <v-checkbox v-model="is_active" label="Enabled" />
              </v-col>
              <v-col cols="12">
                <span class="text-subtitle-2"
                  >Engagement
                  <v-tooltip max-width="250px" location="bottom">
                    <template #activator="{ props }">
                      <v-icon v-bind="props">mdi-help-circle-outline</v-icon>
                    </template>
                    This service will be used to automatically engage services for any incident or
                    case matching the following filters.
                  </v-tooltip>
                </span>
              </v-col>
              <v-col cols="12">
                <search-filter-combobox
                  v-model="filters"
                  :project="project"
                  label="Filters"
                  hint="Select one or more filters that will determine when a service is engaged."
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
                  hint="Owner of this service."
                  clearable
                  name="Owner"
                />
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="evergreen_reminder_interval"
                  label="Reminder Interval"
                  type="number"
                  hint="Number of days that should elapse between reminders sent to the service owner."
                  placeholder="90"
                  clearable
                  min="1"
                  name="Reminder Interval"
                />
              </v-col>
              <v-col cols="12">
                <v-checkbox
                  v-model="evergreen"
                  hint="Enabling evergreen will send periodic reminders to the owner to update this service."
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
import SearchUtils from "@/search/utils"
import PluginApi from "@/plugin/api"

export default {
  setup() {
    return {
      rules: { required },
    }
  },
  name: "ServiceNewEditSheet",

  components: {
    SearchFilterCombobox,
  },

  computed: {
    ...mapFields("service", [
      "selected.description",
      "selected.evergreen",
      "selected.evergreen_owner",
      "selected.evergreen_reminder_interval",
      "selected.external_id",
      "selected.filters",
      "selected.health_metrics",
      "selected.id",
      "selected.is_active",
      "selected.loading",
      "selected.name",
      "selected.project",
      "selected.type",
      "dialogs.showCreateEdit",
    ]),
  },

  methods: {
    ...mapActions("service", ["closeCreateEdit"]),
    save() {
      const self = this
      this.$store.dispatch("service/save").then(function (data) {
        self.$emit("new-service-created", data)
      })
    },
  },

  data() {
    return {
      oncall_plugins: [],
    }
  },

  created() {
    if (this.$route.query.project) {
      this.project = { name: this.$route.query.project }
    }
    this.loading = "error"

    let filterOptions = {
      itemsPerPage: -1,
    }

    if (this.project) {
      filterOptions = {
        ...filterOptions,
        filters: {
          project: [this.project],
        },
      }
    }

    let typeFilter = [
      {
        model: "Plugin",
        field: "type",
        op: "==",
        value: "oncall",
      },
    ]

    filterOptions = SearchUtils.createParametersFromTableOptions({ ...filterOptions }, typeFilter)

    PluginApi.getAllInstances(filterOptions).then((response) => {
      this.loading = false
      this.oncall_plugins = response.data.items.map((p) => p.plugin.slug)
    })
  },
}
</script>
