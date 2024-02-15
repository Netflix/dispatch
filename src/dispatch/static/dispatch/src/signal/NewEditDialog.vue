<template>
  <v-form @submit.prevent v-slot="{ isValid }">
    <v-navigation-drawer v-model="showCreateEdit" location="right" width="500">
      <template #prepend>
        <v-list-item lines="two">
          <v-list-item-title v-if="id" class="text-h6"> Edit </v-list-item-title>
          <v-list-item-title v-else class="text-h6"> New </v-list-item-title>
          <v-list-item-subtitle>Signal Definition</v-list-item-subtitle>

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
      <v-row no-gutters>
        <v-col cols="12">
          <v-card flat rounded="0">
            <v-card-text>
              <v-row no-gutters>
                <v-col cols="12">
                  <v-checkbox
                    v-model="default_signal"
                    label="Default"
                    hint="Whether this signal definition is the default or not."
                    persistent-hint
                  />
                </v-col>
                <v-col cols="12">
                  <v-checkbox
                    v-model="enabled"
                    label="Enabled"
                    hint="Determines whether this signal definition is currently active and should be used to process signals."
                    persistent-hint
                  />
                </v-col>
                <v-col cols="12">
                  <v-text-field
                    v-model="name"
                    label="Name (required)"
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
                    label="Owner (required)"
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
                    label="External ID (required)"
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
                  <tag-filter-auto-complete
                    label="Tags"
                    v-model="tags"
                    model="signal"
                    :model-id="id"
                    :project="project"
                    show-copy
                  />
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12">
          <v-card flat rounded="0">
            <v-toolbar color="transparent">
              <v-toolbar-title class="text-subtitle-2"> Case Configuration </v-toolbar-title>
              <template #append>
                <v-tooltip max-width="250px" location="bottom">
                  <template #activator="{ props }">
                    <v-icon v-bind="props">mdi-help-circle-outline</v-icon>
                  </template>
                  The following options allow you to configure the type of case that Dispatch will
                  create when it encounters this signal.
                </v-tooltip>
              </template>
            </v-toolbar>
            <v-card-text>
              <v-row no-gutters>
                <v-col cols="12">
                  <v-checkbox
                    v-model="create_case"
                    label="Create Case"
                    hint="Determines whether this signal is eligible for case creation (signals could still be associated with existing cases via SignalFilters)."
                    persistent-hint
                  />
                </v-col>
                <v-col cols="12">
                  <case-type-select v-model="case_type" :project="project" label="Type" />
                </v-col>
                <v-col cols="12">
                  <case-priority-select
                    v-model="case_priority"
                    :project="project"
                    label="Priority"
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
                  <signal-engagement-combobox
                    v-model="engagements"
                    label="Engagement(s)"
                    :project="project"
                    :signalDefinition="selected"
                  />
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12">
          <v-card flat rounded="0">
            <v-toolbar color="transparent">
              <v-toolbar-title class="text-subtitle-2"> Entity Configuration </v-toolbar-title>
              <template #append>
                <v-tooltip max-width="250px" location="bottom">
                  <template #activator="{ props }">
                    <v-icon v-bind="props">mdi-help-circle-outline</v-icon>
                  </template>
                  The follow options allow you to control which entities should be pulled from the
                  signal.
                </v-tooltip>
              </template>
            </v-toolbar>
            <v-card-text>
              <entity-type-filter-combobox
                v-model="entity_types"
                :project="project"
                :signalDefinition="selected"
                label="Add Entity Types"
              />
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12">
          <v-card flat rounded="0">
            <v-toolbar color="transparent">
              <v-toolbar-title class="text-subtitle-2"> Filter(s) </v-toolbar-title>
              <template #append>
                <v-tooltip max-width="250px" location="bottom">
                  <template #activator="{ props }">
                    <v-icon v-bind="props">mdi-help-circle-outline</v-icon>
                  </template>
                  Defines a signal filter allowing you to take either a "Snooze" or "Deduplication"
                  action for any match signal matching the filter.
                </v-tooltip>
              </template>
            </v-toolbar>
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
            <v-toolbar color="transparent">
              <v-toolbar-title class="text-subtitle-2"> Workflow(s) </v-toolbar-title>
              <template #append>
                <v-tooltip max-width="250px" location="bottom">
                  <template #activator="{ props }">
                    <v-icon v-bind="props">mdi-help-circle-outline</v-icon>
                  </template>
                  Defines a workflow.
                </v-tooltip>
              </template>
            </v-toolbar>
            <v-card-text>
              <workflow-combobox v-model="workflows" :project="project" />
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

import CasePrioritySelect from "@/case/priority/CasePrioritySelect.vue"
import CaseTypeSelect from "@/case/type/CaseTypeSelect.vue"
import EntityTypeFilterCombobox from "@/entity_type/EntityTypeFilterCombobox.vue"
import ServiceSelect from "@/service/ServiceSelect.vue"
import SignalEngagementCombobox from "@/signal/engagement/SignalEngagementCombobox.vue"
import SignalFilterCombobox from "@/signal/filter/SignalFilterCombobox.vue"
import TagFilterAutoComplete from "@/tag/TagPicker.vue"
import WorkflowCombobox from "@/workflow/WorkflowCombobox.vue"

export default {
  setup() {
    return {
      rules: { required },
    }
  },
  name: "SignalNewEditDialog",

  components: {
    CasePrioritySelect,
    CaseTypeSelect,
    EntityTypeFilterCombobox,
    ServiceSelect,
    SignalEngagementCombobox,
    SignalFilterCombobox,
    TagFilterAutoComplete,
    WorkflowCombobox,
  },

  computed: {
    ...mapFields("signal", [
      "dialogs.showCreateEdit",
      "selected",
      "selected.case_priority",
      "selected.case_type",
      "selected.conversation_target",
      "selected.create_case",
      "selected.description",
      "selected.enabled",
      "selected.engagements",
      "selected.entity_types",
      "selected.external_id",
      "selected.external_url",
      "selected.filters",
      "selected.id",
      "selected.loading",
      "selected.name",
      "selected.oncall_service",
      "selected.owner",
      "selected.project",
      "selected.signal_definition",
      "selected.source",
      "selected.tags",
      "selected.variant",
      "selected.workflows",
    ]),
    ...mapFields("signal", {
      default_signal: "selected.default",
    }),
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
