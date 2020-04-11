<template>
  <ValidationObserver v-slot="{ invalid, validated }">
    <v-navigation-drawer v-model="showCreateEdit" app clipped right width="800">
      <template v-slot:prepend>
        <v-list-item two-line>
          <v-list-item-content>
            <v-list-item-title v-if="id" class="title">{{ name }}</v-list-item-title>
            <v-list-item-title v-else class="title">New</v-list-item-title>
            <v-list-item-subtitle>Reported - {{ reported_at | formatDate }}</v-list-item-subtitle>
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
      <v-tabs fixed-tabs v-model="tab">
        <v-tab key="details">Details</v-tab>
        <v-tab key="resources">Resources</v-tab>
        <v-tab key="people">People</v-tab>
        <v-tab key="timeline">Timeline</v-tab>
      </v-tabs>
      <v-tabs-items v-model="tab">
        <v-tab-item key="details">
          <v-container grid-list-md>
            <v-layout wrap>
              <v-flex xs12>
                <ValidationProvider name="Title" rules="required" immediate>
                  <v-text-field
                    v-model="title"
                    slot-scope="{ errors, valid }"
                    :error-messages="errors"
                    :success="valid"
                    label="Title"
                    hint="Title of incident."
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
                    :error-messages="errors"
                    :success="valid"
                    label="Description"
                    hint="Description of incident."
                    clearable
                    required
                  />
                </ValidationProvider>
              </v-flex>
              <v-flex xs6>
                <v-select
                  v-model="status"
                  label="Status"
                  :items="statuses"
                  hint="The incident's current status"
                />
              </v-flex>
              <v-flex xs6>
                <v-select
                  v-model="visibility"
                  label="Visibility"
                  :items="visibilities"
                  hint="The incident's current's visibilty"
                />
              </v-flex>
              <v-flex xs6>
                <incident-type-select v-model="incident_type" />
              </v-flex>
              <v-flex xs6>
                <incident-priority-select v-model="incident_priority" />
              </v-flex>
              <v-flex xs6>
                <ValidationProvider name="Commander" rules="required" immediate>
                  <individual-select
                    v-model="commander"
                    slot-scope="{ errors, valid }"
                    label="Commander"
                    :error-messages="errors"
                    :success="valid"
                    hint="The incident's current commander"
                    clearable
                    required
                  ></individual-select>
                </ValidationProvider>
              </v-flex>
              <v-flex xs6>
                <ValidationProvider name="Reporter" rules="required" immediate>
                  <individual-select
                    v-model="reporter"
                    slot-scope="{ errors, valid }"
                    label="Reporter"
                    :error-messages="errors"
                    :success="valid"
                    hint="The incident's current reporter"
                    clearable
                    required
                  ></individual-select>
                </ValidationProvider>
              </v-flex>
              <v-flex xs12>
                <span class="subtitle-2">Reported At</span>
              </v-flex>
              <v-flex xs12>
                <v-row>
                  <v-col cols="6">
                    <date-picker-menu v-model="reported_at"></date-picker-menu>
                  </v-col>
                  <v-col cols="6">
                    <time-picker-menu v-model="reported_at"></time-picker-menu>
                  </v-col>
                </v-row>
              </v-flex>
              <v-flex xs12>
                <span class="subtitle-2">Stable At</span>
              </v-flex>
              <v-flex xs12>
                <v-row>
                  <v-col cols="6">
                    <date-picker-menu v-model="stable_at"></date-picker-menu>
                  </v-col>
                  <v-col cols="6">
                    <time-picker-menu v-model="stable_at"></time-picker-menu>
                  </v-col>
                </v-row>
              </v-flex>
              <v-flex xs12>
                <term-combobox v-model="terms" />
              </v-flex>
              <v-flex xs12>
                <tag-combobox v-model="tags" />
              </v-flex>
            </v-layout>
          </v-container>
        </v-tab-item>
        <v-tab-item key="resources">
          <v-list>
            <v-list-item :href="ticket.weblink" target="_blank">
              <v-list-item-content>
                <v-list-item-title>Ticket</v-list-item-title>
                <v-list-item-subtitle>{{ ticket.description }}</v-list-item-subtitle>
              </v-list-item-content>
              <v-list-item-action>
                <v-list-item-icon>
                  <v-icon>open_in_new</v-icon>
                </v-list-item-icon>
              </v-list-item-action>
            </v-list-item>
            <v-divider />
            <v-list-item :href="conference.weblink" target="_blank">
              <v-list-item-content>
                <v-list-item-title>Video Conference</v-list-item-title>
                <v-list-item-subtitle>{{ conference.description }}</v-list-item-subtitle>
              </v-list-item-content>
              <v-list-item-action>
                <v-list-item-icon>
                  <v-icon>open_in_new</v-icon>
                </v-list-item-icon>
              </v-list-item-action>
            </v-list-item>
            <v-divider />
            <v-list-item :href="conversation.weblink" target="_blank">
              <v-list-item-content>
                <v-list-item-title>Conversation</v-list-item-title>
                <v-list-item-subtitle>{{ conversation.description }}</v-list-item-subtitle>
              </v-list-item-content>
              <v-list-item-action>
                <v-list-item-icon>
                  <v-icon>open_in_new</v-icon>
                </v-list-item-icon>
              </v-list-item-action>
            </v-list-item>
            <v-divider />
            <v-list-item :href="storage.weblink" target="_blank">
              <v-list-item-content>
                <v-list-item-title>Storage</v-list-item-title>
                <v-list-item-subtitle>{{ storage.description }}</v-list-item-subtitle>
              </v-list-item-content>
              <v-list-item-action>
                <v-list-item-icon>
                  <v-icon>open_in_new</v-icon>
                </v-list-item-icon>
              </v-list-item-action>
            </v-list-item>
            <v-divider />
            <span v-for="document in documents" :key="document.resource_id">
              <v-list-item :href="document.weblink" target="_blank">
                <v-list-item-content>
                  <v-list-item-title>{{ document.resource_type | deslug }}</v-list-item-title>
                  <v-list-item-subtitle>{{ document.description }}</v-list-item-subtitle>
                </v-list-item-content>
                <v-list-item-action>
                  <v-list-item-icon>
                    <v-icon>open_in_new</v-icon>
                  </v-list-item-icon>
                </v-list-item-action>
              </v-list-item>
              <v-divider />
            </span>
          </v-list>
        </v-tab-item>
        <v-tab-item key="people">
          <span v-for="participant in participants" :key="participant.id">
            <v-list-item :href="participant.individual.weblink" target="_blank">
              <v-list-item-content>
                <v-list-item-title
                  >{{ participant.individual.name }} ({{
                    participant.participant_role | commaString("role")
                  }})</v-list-item-title
                >
                <v-list-item-subtitle>
                  {{ participant.team }} - {{ participant.location }}
                </v-list-item-subtitle>
              </v-list-item-content>
              <v-list-item-action>
                <v-list-item-icon>
                  <v-icon>open_in_new</v-icon>
                </v-list-item-icon>
              </v-list-item-action>
            </v-list-item>
            <v-divider />
          </span>
        </v-tab-item>
      </v-tabs-items>
    </v-navigation-drawer>
  </ValidationObserver>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import { ValidationObserver, ValidationProvider } from "vee-validate"
import IncidentPrioritySelect from "@/incident_priority/IncidentPrioritySelect.vue"
import IncidentTypeSelect from "@/incident_type/IncidentTypeSelect.vue"
import IndividualSelect from "@/individual/IndividualSelect.vue"
import DatePickerMenu from "@/components/DatePickerMenu.vue"
import TimePickerMenu from "@/components/TimePickerMenu.vue"
import TermCombobox from "@/term/TermCombobox.vue"
import TagCombobox from "@/tag/TagCombobox.vue"

export default {
  name: "IncidentNewEditSheet",

  components: {
    ValidationObserver,
    ValidationProvider,
    IncidentPrioritySelect,
    IncidentTypeSelect,
    IndividualSelect,
    TermCombobox,
    TagCombobox,
    TimePickerMenu,
    DatePickerMenu
  },

  data() {
    return {
      tab: null,
      statuses: ["Active", "Stable", "Closed"],
      visibilities: ["Open", "Restricted"]
    }
  },

  computed: {
    ...mapFields("incident", [
      "selected.id",
      "selected.name",
      "selected.title",
      "selected.description",
      "selected.commander",
      "selected.reporter",
      "selected.created_at",
      "selected.stable_at",
      "selected.reported_at",
      "selected.status",
      "selected.terms",
      "selected.tags",
      "selected.incident_priority",
      "selected.incident_type",
      "selected.visibility",
      "selected.ticket",
      "selected.storage",
      "selected.documents",
      "selected.conference",
      "selected.conversation",
      "selected.participants",
      "selected.loading",
      "dialogs.showCreateEdit"
    ])
  },

  methods: {
    ...mapActions("incident", ["save", "closeCreateEdit"])
  }
}
</script>
