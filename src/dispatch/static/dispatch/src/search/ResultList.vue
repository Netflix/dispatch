<template>
  <v-card class="mx-auto" outlined :loading="loading" elevation="0">
    <v-subheader class="title">Search results for: "{{ query }}"</v-subheader>
    <v-expansion-panels flat>
      <v-expansion-panel>
        <v-expansion-panel-header>Incidents ({{ incidents.length }})</v-expansion-panel-header>
        <v-expansion-panel-content>
          <incident-summary-table :items="incidents" />
        </v-expansion-panel-content>
      </v-expansion-panel>
    </v-expansion-panels>
    <!--=<task-list :items="tasks" />
      <term-list :items="terms" />
      <definition-list :items="definitions" />
      <tag-list :items="tags" />
      <individual-list :items="individuals" />
      <team-list :items="teams" />
      <service-list :items="services" />
      <document-list :items="documents" />-->
  </v-card>
</template>

<script>
import { mapState } from "vuex"
import IncidentSummaryTable from "@/incident/IncidentSummaryTable.vue"
/*import ServiceList from "@/service/List.vue"
import IndividualList from "@/individual/List.vue"
import TeamList from "@/team/List.vue"
import DefinitionList from "@/definition/List.vue"
import TermList from "@/term/List.vue"
import TagList from "@/tag/List.vue"
import TaskList from "@/task/List.vue"
import DocumentList from "@/document/List.vue"*/

export default {
  name: "SearchResultList",
  components: {
    IncidentSummaryTable
    /*ServiceList,
    IndividualList,
    DefinitionList,
    TermList,
    TeamList,
    TagList,
    TaskList,
    DocumentList*/
  },
  data() {
    return {}
  },

  computed: {
    ...mapState("search", ["results", "query", "loading"]),
    definitions() {
      return this.results.filter(item => {
        return item.type
          .toLowerCase()
          .includes("definition")
          .map(x => x.content)
      })
    },
    services() {
      return this.results.filter(item => {
        return item.type
          .toLowerCase()
          .includes("service")
          .map(x => x.content)
      })
    },
    individuals() {
      return this.results.filter(item => {
        return item.type
          .toLowerCase()
          .includes("individual_contact")
          .map(x => x.content)
      })
    },
    teams() {
      return this.results.filter(item => {
        return item.type
          .toLowerCase()
          .includes("team")
          .map(x => x.content)
      })
    },
    terms() {
      return this.results.filter(item => {
        return item.type
          .toLowerCase()
          .includes("term")
          .map(x => x.content)
      })
    },
    tags() {
      return this.results.filter(item => {
        return item.type
          .toLowerCase()
          .includes("tag")
          .map(x => x.content)
      })
    },
    tasks() {
      return this.results.filter(item => {
        return item.type
          .toLowerCase()
          .includes("task")
          .map(x => x.content)
      })
    },
    incidents() {
      return this.results.filter(item => {
        return item.type
          .toLowerCase()
          .includes("incident")
          .map(x => x.content)
      })
    },
    documents() {
      return this.results.filter(item => {
        return item.type
          .toLowerCase()
          .inclues("documents")
          .map(x => x.content)
      })
    }
  },

  methods: {}
}
</script>
