<template>
  <v-form @submit.prevent v-slot="{ isValid }">
    <v-navigation-drawer v-model="showCreateEdit" clipped location="right" width="500">
      <template #prepend>
        <v-list-item lines="two">
          <v-list-item-title v-if="id" class="text-h6"> Edit </v-list-item-title>
          <v-list-item-title v-else class="text-h6"> New </v-list-item-title>
          <v-list-item-subtitle>Signal Definition</v-list-item-subtitle>

          <v-btn
            icon
            variant="text"
            color="info"
            :loading="loading"
            :disabled="!isValid.value"
            @click="save()"
          >
            <v-icon>save</v-icon>
          </v-btn>
          <v-btn icon variant="text" color="secondary" @click="closeCreateEdit()">
            <v-icon>close</v-icon>
          </v-btn>
        </v-list-item>
      </template>
      <v-row no-gutters>
        <v-col cols="12">
          <v-card flat rounded="0">
            <v-card-text>
              <v-row no-gutters>
                <v-col cols="12">
                  <v-text-field
                    v-model="name"
                    label="Name"
                    persistent-hint
                    hint="A human readable display name for this signal."
                    clearable
                    name="Name"
                    :rules="[rules.required]"
                  />
                </v-col>
                <v-col cols="12">
                  <v-textarea
                    v-model="description"
                    label="Description"
                    rows="1"
                    auto-grow
                    hint="A short description of the signal."
                    persistent-hint
                    clearable
                    name="Description"
                  />
                </v-col>
                <v-col cols="12">
                  <v-text-field
                    v-model="variant"
                    label="Variant"
                    hint="The same signal can have multiple variants with different defintions."
                    persistent-hint
                    clearable
                    name="variant"
                  />
                </v-col>
                <v-col cols="12">
                  <v-text-field
                    v-model="owner"
                    label="Owner"
                    hint="Typically the team or owner that produces the signal."
                    persistent-hint
                    clearable
                    name="owner"
                    :rules="[rules.required]"
                  />
                </v-col>
                <v-col cols="12">
                  <v-text-field
                    v-model="external_id"
                    label="External ID"
                    hint="This ID will be used to correctly associate incoming signals to this definition."
                    persistent-hint
                    clearable
                    name="externalId"
                    :rules="[rules.required]"
                  />
                </v-col>
                <v-col cols="12">
                  <v-text-field
                    v-model="external_url"
                    label="External URL"
                    hint="This is a reference to an external app or documentation for this signal."
                    persistent-hint
                    clearable
                    name="externalURL"
                  />
                </v-col>
                <v-col cols="12">
                  <v-checkbox
                    v-model="enabled"
                    label="Enabled"
                    hint="Determines whether this signal definition is currently active and should be used to process signals."
                  />
                </v-col>
                <v-col cols="12">
                  <v-checkbox
                    v-model="create_case"
                    label="Create Case"
                    hint="Determines whether this signal is eligible for case creation (signals could still be associated with existing cases via SignalFilters)."
                  />
                </v-col>
                <v-col cols="12">
                  <v-form @submit.prevent>
                    <service-select
                      :project="project"
                      label="Oncall Service"
                      v-model="oncall_service"
                    />
                  </v-form>
                </v-col>
                <v-col cols="12">
                  <v-text-field
                    v-model="conversation_target"
                    label="Conversation Target"
                    hint="The conversation identifier that new case messages will be sent to."
                    clearable
                    name="ConversationTarget"
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
          <v-card flat rounded="0">
            <v-app-bar color="white" flat>
              <v-toolbar-title class="text-subtitle-2"> Entity Configuration </v-toolbar-title>
              <v-spacer />
              <v-tooltip max-width="250px" location="bottom">
                <template #activator="{ on, attrs }">
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
              />
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12">
          <v-card flat rounded="0">
            <v-app-bar color="white" flat>
              <v-toolbar-title class="text-subtitle-2"> Case Configuration </v-toolbar-title>
              <v-spacer />
              <v-tooltip max-width="250px" location="bottom">
                <template #activator="{ on, attrs }">
                  <v-icon v-bind="attrs" v-on="on"> help_outline </v-icon>
                </template>
                The following options allow you to configure the type of case that Dispatch will
                create when it encounters this signal.
              </v-tooltip>
            </v-app-bar>
            <v-card-text>
              <v-row no-gutters>
                <v-col cols="12">
                  <case-type-select label="Case Type" :project="project" v-model="case_type" />
                </v-col>
                <v-col cols="12">
                  <case-priority-select
                    label="Case Priority"
                    :project="project"
                    v-model="case_priority"
                  />
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12">
          <v-card flat rounded="0">
            <v-app-bar color="white" flat>
              <v-toolbar-title class="text-subtitle-2"> Filter(s) </v-toolbar-title>
              <v-spacer />
              <v-tooltip max-width="250px" location="bottom">
                <template #activator="{ on, attrs }">
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
              />
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12">
          <v-card flat rounded="0">
            <v-app-bar color="white" flat>
              <v-toolbar-title class="text-subtitle-2"> Engagement(s) </v-toolbar-title>
              <v-spacer />
              <v-tooltip max-width="250px" location="bottom">
                <template #activator="{ on, attrs }">
                  <v-icon v-bind="attrs" v-on="on"> help_outline </v-icon>
                </template>
                Defines an Engagement filter.
              </v-tooltip>
            </v-app-bar>
            <v-card-text>
              <signal-engagement-combobox
                v-model="engagements"
                :project="project"
                :signalDefinition="selected"
              />
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12">
          <v-card flat rounded="0">
            <v-app-bar color="white" flat>
              <v-toolbar-title class="text-subtitle-2"> Workflow(s) </v-toolbar-title>
              <v-spacer />
              <v-tooltip max-width="250px" location="bottom">
                <template #activator="{ on, attrs }">
                  <v-icon v-bind="attrs" v-on="on"> help_outline </v-icon>
                </template>
                Defines a workflow.
              </v-tooltip>
            </v-app-bar>
            <v-card-text>
              <workflow-combobox
                v-model="workflows"
                :project="project"
                :signalDefinition="selected"
              />
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-navigation-drawer>
  </v-form>
</template>

<script>
import { required } from "@/util/form"
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

import CaseTypeSelect from "@/case/type/CaseTypeSelect.vue"
import ServiceSelect from "@/service/ServiceSelect.vue"
import CasePrioritySelect from "@/case/priority/CasePrioritySelect.vue"
import EntityTypeFilterCombobox from "@/entity_type/EntityTypeFilterCombobox.vue"
import SignalEngagementCombobox from "@/signal/engagement/SignalEngagementCombobox.vue"
import SignalFilterCombobox from "@/signal/filter/SignalFilterCombobox.vue"
import TagFilterAutoComplete from "@/tag/TagFilterAutoComplete.vue"
import WorkflowCombobox from "@/workflow/WorkflowCombobox.vue"

export default {
  setup() {
    return {
      rules: { required },
    }
  },
  name: "SignalNewEditDialog",

  components: {
    ServiceSelect,
    CaseTypeSelect,
    CasePrioritySelect,
    SignalEngagementCombobox,
    SignalFilterCombobox,
    EntityTypeFilterCombobox,
    TagFilterAutoComplete,
    WorkflowCombobox,
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
      "selected.engagements",
      "selected.entity_types",
      "selected.signal_definition",
      "selected.oncall_service",
      "selected.conversation_target",
      "selected.create_case",
      "selected.source",
      "selected.tags",
      "selected.workflows",
      "selected.project",
      "selected.loading",
    ]),
  },

  methods: {
    ...mapActions("signal", ["save", "closeCreateEdit"]),
  },

  created() {
    if (this.$route.query.project) {
      this.project = { name: this.$route.query.project }
    }
  },
}
</script>
