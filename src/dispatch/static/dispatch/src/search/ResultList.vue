<template>
  <v-layout row wrap>
    <v-flex>
      <service-list v-if="services.length" :items="services" />
      <individual-list v-if="individuals.length" :items="individuals" />
      <team-list v-if="teams.length" :items="teams" />
      <definition-list v-if="definitions.length" :items="definitions" />
      <term-list v-if="terms.length" :items="terms" />
      <v-layout v-if="!results.length" align-center justify-center row>
        <div class="mr-3 hidden-sm-and-down">
          <img src="/static/error/500.svg" alt />
        </div>
        <div class="text-md-center">
          <h1>Nothing to see here.</h1>
          <h2 class="my-3 headline">
            It looks like we weren't able to find anything for your query.
          </h2>
        </div>
      </v-layout>
    </v-flex>
  </v-layout>
</template>

<script>
import { mapState } from "vuex"
import ServiceList from "@/service/List.vue"
import IndividualList from "@/individual/List.vue"
import TeamList from "@/team/List.vue"
import DefinitionList from "@/definition/List.vue"
import TermList from "@/term/List.vue"
export default {
  name: "SearchResultList",
  components: {
    ServiceList,
    IndividualList,
    DefinitionList,
    TermList,
    TeamList
  },
  data() {
    return {}
  },

  computed: {
    ...mapState("search", ["results"]),
    //...mapGetters("term", ["selectedTerm"])
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
    }
  },

  methods: {}
}
</script>
