<template>
  <v-card class="mx-auto">
    <v-subheader>Search results for: "{{ query }}"</v-subheader>
    <v-list v-if="!results.length">
      <v-list-item no-action>
        <v-list-item-content>
          <v-list-item-title class="title"
            >Sorry, we didn't find anything matching your query.</v-list-item-title
          >
        </v-list-item-content>
      </v-list-item>
    </v-list>
    <div v-else>
      <incident-list :items="incidents" />
      <task-list :items="tasks" />
      <term-list :items="terms" />
      <definition-list :items="definitions" />
      <tag-list :items="tags" />
      <individual-list :items="individuals" />
      <team-list :items="teams" />
      <service-list :items="services" />
    </div>
  </v-card>
</template>

<script>
import { mapState } from "vuex"
import IncidentList from "@/incident/List.vue"
import ServiceList from "@/service/List.vue"
import IndividualList from "@/individual/List.vue"
import TeamList from "@/team/List.vue"
import DefinitionList from "@/definition/List.vue"
import TermList from "@/term/List.vue"
import TagList from "@/tag/List.vue"
import TaskList from "@/task/List.vue"
export default {
  name: "SearchResultList",
  components: {
    IncidentList,
    ServiceList,
    IndividualList,
    DefinitionList,
    TermList,
    TeamList,
    TagList,
    TaskList
  },
  data() {
    return {}
  },

  computed: {
    ...mapState("search", ["results", "query"]),
    definitions() {
      return this.results.filter(item => {
        return item.type.toLowerCase().includes("definition")
      })
    },
    services() {
      return this.results.filter(item => {
        return item.type.toLowerCase().includes("service")
      })
    },
    individuals() {
      return this.results.filter(item => {
        return item.type.toLowerCase().includes("individual_contact")
      })
    },
    teams() {
      return this.results.filter(item => {
        return item.type.toLowerCase().includes("team")
      })
    },
    terms() {
      return this.results.filter(item => {
        return item.type.toLowerCase().includes("term")
      })
    },
    tags() {
      return this.results.filter(item => {
        return item.type.toLowerCase().includes("tag")
      })
    },
    tasks() {
      return this.results.filter(item => {
        return item.type.toLowerCase().includes("task")
      })
    },
    incidents() {
      return this.results.filter(item => {
        return item.type.toLowerCase().includes("incident")
      })
    }
  },

  methods: {}
}
</script>
