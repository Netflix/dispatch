<template>
  <ValidationObserver v-slot="{ invalid, validated }">
    <v-navigation-drawer v-model="showCreateEdit" app clipped right width="500">
      <template v-slot:prepend>
        <v-list-item two-line>
          <v-list-item-content>
            <v-list-item-title v-if="id" class="title"> Edit </v-list-item-title>
            <v-list-item-title v-else class="title"> New </v-list-item-title>
            <v-list-item-subtitle>Signal Definition</v-list-item-subtitle>
          </v-list-item-content>
          <v-btn
            icon
            color="info"
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
      <v-row no-gutters>
        <v-col cols="12">
          <v-card flat tile>
            <v-card-text>
              <v-row no-gutters>
                <v-col cols="12">
                  <ValidationProvider name="Name" rules="required" immediate>
                    <v-text-field
                      v-model="name"
                      slot-scope="{ errors, valid }"
                      :error-messages="errors"
                      :success="valid"
                      label="Name"
                      persistent-hint
                      hint="A human readable display name for this signal."
                      clearable
                    />
                  </ValidationProvider>
                </v-col>
                <v-col cols="12">
                  <ValidationProvider name="Description" immediate>
                    <v-textarea
                      v-model="description"
                      slot-scope="{ errors, valid }"
                      label="Description"
                      :error-messages="errors"
                      :success="valid"
                      rows="1"
                      auto-grow
                      hint="A short description of the signal."
                      persistent-hint
                      clearable
                    />
                  </ValidationProvider>
                </v-col>
                <v-col cols="12">
                  <ValidationProvider name="variant" immediate>
                    <v-text-field
                      v-model="variant"
                      slot-scope="{ errors, valid }"
                      :error-messages="errors"
                      :success="valid"
                      label="Variant"
                      hint="The same signal can have multiple variants with different defintions."
                      persistent-hint
                      clearable
                    />
                  </ValidationProvider>
                </v-col>
                <v-col cols="12">
                  <ValidationProvider name="owner" rules="required" immediate>
                    <v-text-field
                      v-model="owner"
                      slot-scope="{ errors, valid }"
                      :error-messages="errors"
                      :success="valid"
                      label="Owner"
                      hint="Typically the team or owner that produces the signal."
                      persistent-hint
                      clearable
                    />
                  </ValidationProvider>
                </v-col>
                <v-col cols="12">
                  <ValidationProvider name="externalId" rules="required" immediate>
                    <v-text-field
                      v-model="external_id"
                      slot-scope="{ errors, valid }"
                      :error-messages="errors"
                      :success="valid"
                      label="External ID"
                      hint="This ID will be used to correctly associate incomming signals to this definition."
                      persistent-hint
                      clearable
                    />
                  </ValidationProvider>
                </v-col>
                <v-col cols="12">
                  <ValidationProvider name="externalURL" immediate>
                    <v-text-field
                      v-model="external_url"
                      slot-scope="{ errors, valid }"
                      :error-messages="errors"
                      :success="valid"
                      label="External URL"
                      hint="This is a reference to an external app or documentation for this signal."
                      persistent-hint
                      clearable
                    />
                  </ValidationProvider>
                </v-col>
                <v-col cols="12">
                  <v-checkbox
                    v-model="enabled"
                    label="Enabled"
                    hint="Determines whether this signal definition is currently active and should be used to process signals."
                  />
                </v-col>
                <v-col cols="12">
                  <tag-filter-auto-complete
                    label="Tags"
                    v-model="tags"
                    model="signal"
                    :model-id="id"
                  />
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12">
          <v-card flat tile>
            <v-app-bar color="white" flat>
              <v-toolbar-title class="subtitle-2"> Entity Configuration </v-toolbar-title>
              <v-spacer></v-spacer>
              <v-tooltip max-width="250px" bottom>
                <template v-slot:activator="{ on, attrs }">
                  <v-icon v-bind="attrs" v-on="on"> help_outline </v-icon>
                </template>
                The follow options allow you to control which entities should be pulled from the
                signal.
              </v-tooltip>
            </v-app-bar>
            <v-card-text>
              <entity-type-filter-combobox
                v-model="entity_types"
                :project="project"
                :signalDefinition="selected"
              ></entity-type-filter-combobox>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12">
          <v-card flat tile>
            <v-app-bar color="white" flat>
              <v-toolbar-title class="subtitle-2"> Case Configuration </v-toolbar-title>
              <v-spacer></v-spacer>
              <v-tooltip max-width="250px" bottom>
                <template v-slot:activator="{ on, attrs }">
                  <v-icon v-bind="attrs" v-on="on"> help_outline </v-icon>
                </template>
                The following options allow you to configure the type of case that Dispatch will
                create when it encounters this signal.
              </v-tooltip>
            </v-app-bar>
            <v-card-text>
              <v-row no-gutters>
                <v-col cols="12">
                  <case-type-select label="Case Type" v-model="case_type" />
                </v-col>
                <v-col cols="12">
                  <case-priority-select label="Case Priority" v-model="case_priority" />
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12">
          <v-card flat tile>
            <v-app-bar color="white" flat>
              <v-toolbar-title class="subtitle-2"> Filter(s) </v-toolbar-title>
              <v-spacer></v-spacer>
              <v-tooltip max-width="250px" bottom>
                <template v-slot:activator="{ on, attrs }">
                  <v-icon v-bind="attrs" v-on="on"> help_outline </v-icon>
                </template>
                Defines a signal filter allowing you to take either a "Snooze" or "Deduplication"
                action for any match signal matching the filter.
              </v-tooltip>
            </v-app-bar>
            <v-card-text>
              <signal-filter-combobox
                v-model="filters"
                :project="project"
                :signalDefinition="selected"
              ></signal-filter-combobox>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-navigation-drawer>
  </ValidationObserver>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import { ValidationObserver, ValidationProvider, extend } from "vee-validate"
import { required } from "vee-validate/dist/rules"

import CaseTypeSelect from "@/case/type/CaseTypeSelect.vue"
import CasePrioritySelect from "@/case/priority/CasePrioritySelect.vue"
import EntityTypeFilterCombobox from "@/entity_type/EntityTypeFilterCombobox.vue"
import SignalFilterCombobox from "@/signal/filter/SignalFilterCombobox.vue"
import TagFilterAutoComplete from "@/tag/TagFilterAutoComplete.vue"

extend("required", {
  ...required,
})

export default {
  name: "SignalNewEditDialog",

  components: {
    ValidationObserver,
    ValidationProvider,
    CaseTypeSelect,
    CasePrioritySelect,
    SignalFilterCombobox,
    EntityTypeFilterCombobox,
    TagFilterAutoComplete,
  },

  computed: {
    ...mapFields("signal", [
      "dialogs.showCreateEdit",
      "selected",
      "selected.id",
      "selected.name",
      "selected.description",
      "selected.enabled",
      "selected.variant",
      "selected.owner",
      "selected.external_id",
      "selected.external_url",
      "selected.case_type",
      "selected.case_priority",
      "selected.filters",
      "selected.entity_types",
      "selected.signal_definition",
      "selected.source",
      "selected.tags",
      "selected.project",
      "selected.loading",
    ]),
    ...mapFields("route", ["query"]),
  },

  methods: {
    ...mapActions("signal", ["save", "closeCreateEdit"]),
  },

  created() {
    if (this.query.project) {
      this.project = { name: this.query.project }
    }
  },
}
</script>
