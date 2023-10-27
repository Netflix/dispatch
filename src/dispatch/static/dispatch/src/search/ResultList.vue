<template>
  <v-card class="mx-auto" variant="flat" :loading="loading">
    <div class="text-h6 pl-4">Search results for: "{{ query }}"</div>
    <v-expansion-panels>
      <v-expansion-panel>
        <v-expansion-panel-title>
          Incidents ({{ results.incidents.length }})
        </v-expansion-panel-title>
        <v-expansion-panel-text>
          <incident-summary-table :items="results.incidents" />
        </v-expansion-panel-text>
      </v-expansion-panel>
      <v-expansion-panel>
        <v-expansion-panel-title>Cases ({{ results.cases.length }})</v-expansion-panel-title>
        <v-expansion-panel-text>
          <case-summary-table :items="results.cases" />
        </v-expansion-panel-text>
      </v-expansion-panel>
      <v-expansion-panel>
        <v-expansion-panel-title>Tasks ({{ results.tasks.length }})</v-expansion-panel-title>
        <v-expansion-panel-text>
          <task-summary-table :items="results.tasks" />
        </v-expansion-panel-text>
      </v-expansion-panel>
      <v-expansion-panel>
        <v-expansion-panel-title>Sources ({{ results.sources.length }})</v-expansion-panel-title>
        <v-expansion-panel-text>
          <source-summary-table :items="results.sources" />
        </v-expansion-panel-text>
      </v-expansion-panel>
      <v-expansion-panel>
        <v-expansion-panel-title>Queries ({{ results.queries.length }})</v-expansion-panel-title>
        <v-expansion-panel-text>
          <query-summary-table :items="results.sources" />
        </v-expansion-panel-text>
      </v-expansion-panel>
      <v-expansion-panel>
        <v-expansion-panel-title>
          Documents ({{ results.documents.length }})
        </v-expansion-panel-title>
        <v-expansion-panel-text>
          <document-summary-table :items="results.documents" />
        </v-expansion-panel-text>
      </v-expansion-panel>
      <v-expansion-panel>
        <v-expansion-panel-title>Tags ({{ results.tags.length }})</v-expansion-panel-title>
        <v-expansion-panel-text>
          <tag-summary-table :items="results.tags" />
        </v-expansion-panel-text>
      </v-expansion-panel>
    </v-expansion-panels>
  </v-card>
</template>

<script>
import { mapState } from "vuex"
import { mapActions } from "vuex"
import IncidentSummaryTable from "@/incident/IncidentSummaryTable.vue"
import CaseSummaryTable from "@/case/CaseSummaryTable.vue"
import TaskSummaryTable from "@/task/TaskSummaryTable.vue"
import SourceSummaryTable from "@/data/source/SourceSummaryTable.vue"
import QuerySummaryTable from "@/data/query/QuerySummaryTable.vue"
import DocumentSummaryTable from "@/document/DocumentSummaryTable.vue"
import TagSummaryTable from "@/tag/TagSummaryTable.vue"

export default {
  name: "SearchResultList",
  components: {
    IncidentSummaryTable,
    CaseSummaryTable,
    TaskSummaryTable,
    DocumentSummaryTable,
    SourceSummaryTable,
    QuerySummaryTable,
    TagSummaryTable,
  },
  data() {
    return {}
  },
  created() {
    this.fetchDetails()
  },
  watch: {
    query: function (q) {
      // update URL in browser and search for new query
      this.$router.push({ name: "ResultList", query: { q: q } })
      this.setQuery(q)
      this.getResults()
    },
  },

  computed: {
    ...mapState("search", ["results", "query", "loading"]),
  },
  methods: {
    fetchDetails() {
      this.setQuery(this.$route.query.q)
      this.getResults()
    },
    ...mapActions("search", ["setQuery", "getResults"]),
  },
}
</script>
