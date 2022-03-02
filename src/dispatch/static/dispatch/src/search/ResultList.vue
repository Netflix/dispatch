<template>
  <v-card class="mx-auto" outlined :loading="loading" elevation="0">
    <v-subheader class="title"> Search results for: "{{ query }}" </v-subheader>
    <v-expansion-panels flat>
      <v-expansion-panel>
        <v-expansion-panel-header>
          Incidents ({{ results.incidents.length }})
        </v-expansion-panel-header>
        <v-expansion-panel-content>
          <incident-summary-table :items="results.incidents" />
        </v-expansion-panel-content>
      </v-expansion-panel>
      <v-expansion-panel>
        <v-expansion-panel-header>Tasks ({{ results.tasks.length }})</v-expansion-panel-header>
        <v-expansion-panel-content>
          <task-summary-table :items="results.tasks" />
        </v-expansion-panel-content>
      </v-expansion-panel>
      <v-expansion-panel>
        <v-expansion-panel-header>Sources ({{ results.sources.length }})</v-expansion-panel-header>
        <v-expansion-panel-content>
          <source-summary-table :items="results.sources" />
        </v-expansion-panel-content>
      </v-expansion-panel>
      <v-expansion-panel>
        <v-expansion-panel-header>Queries ({{ results.queries.length }})</v-expansion-panel-header>
        <v-expansion-panel-content>
          <query-summary-table :items="results.sources" />
        </v-expansion-panel-content>
      </v-expansion-panel>
      <v-expansion-panel>
        <v-expansion-panel-header>
          Documents ({{ results.documents.length }})
        </v-expansion-panel-header>
        <v-expansion-panel-content>
          <document-summary-table :items="results.documents" />
        </v-expansion-panel-content>
      </v-expansion-panel>
      <v-expansion-panel>
        <v-expansion-panel-header>Tags ({{ results.tags.length }})</v-expansion-panel-header>
        <v-expansion-panel-content>
          <tag-summary-table :items="results.tags" />
        </v-expansion-panel-content>
      </v-expansion-panel>
    </v-expansion-panels>
  </v-card>
</template>

<script>
import { mapState } from "vuex"
import IncidentSummaryTable from "@/incident/IncidentSummaryTable.vue"
import TaskSummaryTable from "@/task/TaskSummaryTable.vue"
import SourceSummaryTable from "@/data/source/SourceSummaryTable.vue"
import QuerySummaryTable from "@/data/query/QuerySummaryTable.vue"
import DocumentSummaryTable from "@/document/DocumentSummaryTable.vue"
import TagSummaryTable from "@/tag/TagSummaryTable.vue"

export default {
  name: "SearchResultList",
  components: {
    IncidentSummaryTable,
    TaskSummaryTable,
    DocumentSummaryTable,
    SourceSummaryTable,
    QuerySummaryTable,
    TagSummaryTable,
  },
  data() {
    return {}
  },

  computed: {
    ...mapState("search", ["results", "query", "loading"]),
  },
}
</script>
