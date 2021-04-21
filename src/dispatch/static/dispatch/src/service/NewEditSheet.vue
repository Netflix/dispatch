<template>
  <ValidationObserver v-slot="{ invalid, validated }">
    <v-navigation-drawer v-model="showCreateEdit" app clipped right width="500">
      <template v-slot:prepend>
        <v-list-item two-line>
          <v-list-item-content>
            <v-list-item-title v-if="id" class="title"> Edit </v-list-item-title>
            <v-list-item-title v-else class="title"> New </v-list-item-title>
            <v-list-item-subtitle>Service</v-list-item-subtitle>
          </v-list-item-content>
          <v-btn icon color="info" :disabled="invalid || !validated" @click="save()">
            <v-icon>save</v-icon>
          </v-btn>
          <v-btn icon color="secondary" @click="closeCreateEdit()">
            <v-icon>close</v-icon>
          </v-btn>
        </v-list-item>
      </template>
      <v-card flat>
        <v-card-text>
          <v-container grid-list-md>
            <v-layout wrap>
              <v-flex xs12>
                <span class="subtitle-2">Details</span>
              </v-flex>
              <v-flex xs12>
                <ValidationProvider name="Name" rules="required" immediate>
                  <v-text-field
                    v-model="name"
                    slot-scope="{ errors, valid }"
                    :error-messages="errors"
                    :success="valid"
                    label="Name"
                    hint="A name for your service."
                    clearable
                    required
                  />
                </ValidationProvider>
              </v-flex>
              <v-flex xs12>
                <ValidationProvider name="Description" rules="required" immediate>
                  <v-textarea
                    v-model="description"
                    slot-scope="{ errors, valid }"
                    label="Description"
                    :error-messages="errors"
                    :success="valid"
                    hint="A description for your service."
                    clearable
                    required
                  />
                </ValidationProvider>
              </v-flex>
              <v-flex xs12>
                <ValidationProvider name="Type" rules="required" immediate>
                  <v-select
                    v-model="type"
                    slot-scope="{ errors, valid }"
                    :loading="loading"
                    :items="oncall_plugins"
                    label="Type"
                    :error-messages="errors"
                    hint="Oncall plugin to use."
                    :success="valid"
                  />
                </ValidationProvider>
              </v-flex>
              <v-flex xs12>
                <ValidationProvider name="External Id" rules="required" immediate>
                  <v-text-field
                    v-model="external_id"
                    slot-scope="{ errors, valid }"
                    label="External Id"
                    :error-messages="errors"
                    :success="valid"
                    hint="An external identifier for service."
                    clearable
                    required
                  />
                </ValidationProvider>
              </v-flex>
              <v-flex xs12>
                <v-checkbox v-model="is_active" label="Enabled" />
              </v-flex>
              <v-flex xs12>
                <span class="subtitle-2">Engagement</span>
              </v-flex>
              <v-flex xs12>
                <search-filter-combobox
                  v-model="filters"
                  :project="project"
                  label="Filters"
                  hint="Select one or more filters that will determine when a service is engaged."
                />
              </v-flex>
            </v-layout>
          </v-container>
        </v-card-text>
      </v-card>
    </v-navigation-drawer>
  </ValidationObserver>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import { ValidationObserver, ValidationProvider, extend } from "vee-validate"
import { required } from "vee-validate/dist/rules"

import SearchFilterCombobox from "@/search/SearchFilterCombobox.vue"
import SearchUtils from "@/search/utils"
import PluginApi from "@/plugin/api"

extend("required", {
  ...required,
  message: "This field is required",
})

export default {
  name: "ServiceNewEditSheet",

  components: {
    ValidationObserver,
    ValidationProvider,
    SearchFilterCombobox,
  },

  computed: {
    ...mapFields("service", [
      "selected.name",
      "selected.type",
      "selected.id",
      "selected.filters",
      "selected.project",
      "selected.description",
      "selected.external_id",
      "selected.is_active",
      "selected.loading",
      "dialogs.showCreateEdit",
    ]),
    ...mapFields("route", ["query"]),
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
      oncall_plugins: null,
    }
  },

  created() {
    if (this.query.project) {
      this.project = { name: this.query.project }
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
