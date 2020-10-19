<template>
  <ValidationObserver v-slot="{ invalid, validated }">
    <v-navigation-drawer v-model="showCreateEdit" app clipped right width="500">
      <template v-slot:prepend>
        <v-list-item two-line>
          <v-list-item-content>
            <v-list-item-title v-if="id" class="title">Edit</v-list-item-title>
            <v-list-item-title v-else class="title">New</v-list-item-title>
            <v-list-item-subtitle>Service</v-list-item-subtitle>
          </v-list-item-content>
          <v-btn
            icon
            color="primary"
            :loading="loading"
            :disabled="invalid || !validated"
            @click="save()"
          >
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
              <!-- Disable type (default to pager duty) until we have a way to validate. -->
              <v-flex xs12>
                <ValidationProvider name="Type" rules="required" immediate>
                  <v-select
                    v-model="type"
                    slot-scope="{ errors, valid }"
                    :loading="loading"
                    :items="oncall_plugins"
                    label="Type"
                    :error-messages="errors"
                    hint="Oncall plugin to use"
                    :success="valid"
                  ></v-select>
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
                    hint="An external identififer for service."
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
                <term-combobox v-model="terms" />
              </v-flex>
              <v-flex xs12>
                <incident-priority-multi-select v-model="incident_priorities" />
              </v-flex>
              <v-flex>
                <incident-type-multi-select v-model="incident_types" />
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
import IncidentPriorityMultiSelect from "@/incident_priority/IncidentPriorityMultiSelect.vue"
import IncidentTypeMultiSelect from "@/incident_type/IncidentTypeMultiSelect.vue"
import TermCombobox from "@/term/TermCombobox.vue"
import PluginApi from "@/plugin/api"

extend("required", {
  ...required,
  message: "This field is required"
})

export default {
  name: "ServiceNewEditSheet",

  components: {
    ValidationObserver,
    ValidationProvider,
    IncidentPriorityMultiSelect,
    IncidentTypeMultiSelect,
    TermCombobox
  },

  computed: {
    ...mapFields("service", [
      "selected.name",
      "selected.terms",
      "selected.type",
      "selected.incident_priorities",
      "selected.incident_types",
      "selected.id",
      "selected.description",
      "selected.external_id",
      "selected.is_active",
      "selected.loading",
      "dialogs.showCreateEdit"
    ])
  },

  methods: {
    ...mapActions("service", ["save", "closeCreateEdit"])
  },

  data() {
    return {
      oncall_plugins: null
    }
  },

  mounted() {
    this.loading = true
    PluginApi.getByType("oncall").then(response => {
      this.loading = false
      this.oncall_plugins = response.data.items.map(p => p.slug)
    })
  }
}
</script>
