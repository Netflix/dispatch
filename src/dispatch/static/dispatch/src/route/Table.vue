<template>
  <v-layout wrap>
    <div>
      <v-dialog v-model="loading" persistent width="300">
        <v-card dark>
          <v-card-text>
            Finding the best matches
            <v-progress-linear indeterminate color="primary" class="mb-0" />
          </v-card-text>
        </v-card>
      </v-dialog>
    </div>
    <div class="headline">Route</div>
    <v-flex xs12>
      <v-layout column>
        <v-flex>
          <v-card>
            <v-card-text>
              <v-textarea v-model="text" rows="2" clearable label="Text" auto-grow />
              <div v-if="matched_terms.length">
                Matched Terms:
                <span v-for="match in matched_terms" :key="match.id">
                  <v-tooltip max-width="200" bottom>
                    <template v-slot:activator="{ on }">
                      <v-chip v-on="on">{{ match.text }}</v-chip>
                    </template>
                    <span>{{ match.definitions[0].text }}</span>
                  </v-tooltip>
                </span>
              </div>
              <incident-priority-multi-select v-model="incident_priorities" />
              <incident-type-multi-select v-model="incident_types" />
            </v-card-text>
            <v-card-actions>
              <v-btn :loading="loading" text @click="getRecommendation()">Search</v-btn>
            </v-card-actions>
          </v-card>
        </v-flex>
        <v-flex>
          <service-list v-if="service_contacts.length" :items="service_contacts" />
          <individual-list v-if="individual_contacts.length" :items="individual_contacts" />
          <team-list v-if="team_contacts.length" :items="team_contacts" />
          <document-list v-if="documents.length" :items="documents" />
        </v-flex>
      </v-layout>
    </v-flex>
  </v-layout>
</template>

<script>
import { mapActions } from "vuex"
import { mapFields } from "vuex-map-fields"
import IncidentPriorityMultiSelect from "@/incident_priority/IncidentPriorityMultiSelect.vue"
import IncidentTypeMultiSelect from "@/incident_type/IncidentTypeMultiSelect.vue"
import ServiceList from "@/service/List.vue"
import IndividualList from "@/individual/List.vue"
import TeamList from "@/team/List.vue"
import DocumentList from "@/document/List.vue"

export default {
  name: "RouteTable",
  components: {
    TeamList,
    IndividualList,
    ServiceList,
    DocumentList,
    IncidentPriorityMultiSelect,
    IncidentTypeMultiSelect
  },

  computed: {
    ...mapFields("route", [
      "route.text",
      "route.context.incident_priorities",
      "route.context.incident_types",
      "recommendation.matched_terms",
      "recommendation.service_contacts",
      "recommendation.team_contacts",
      "recommendation.individual_contacts",
      "recommendation.documents",
      "recommendation.loading"
    ])
  },

  methods: {
    ...mapActions("route", ["getRecommendation"])
  }
}
</script>
