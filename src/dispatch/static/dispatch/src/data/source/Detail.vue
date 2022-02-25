<template>
  <div>
    <new-edit-sheet />
    <v-toolbar dark flat>
      <v-toolbar-title>{{ name }}</v-toolbar-title>

      <v-spacer></v-spacer>

      <span v-if="source_status"> Status: {{ source_status.name }}</span>

      <v-menu bottom left>
        <template v-slot:activator="{ on }">
          <v-btn icon v-on="on">
            <v-icon>mdi-dots-vertical</v-icon>
          </v-btn>
        </template>
        <v-list>
          <v-list-item @click="createEditShow(selected)">
            <v-list-item-title>Edit</v-list-item-title>
          </v-list-item>
          <v-list-item @click="removeShow(selected)">
            <v-list-item-title>Delete</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>

      <template v-slot:extension>
        <v-tabs align-with-title>
          <v-tabs-slider></v-tabs-slider>
          <v-tab :to="{ params: { tab: 'details' } }">Details </v-tab>
          <!--<v-tab :to="{ params: { tab: 'schema' } }">Schema </v-tab>-->
          <v-tab :to="{ params: { tab: 'queries' } }">Queries </v-tab>
          <v-tab :to="{ params: { tab: 'incidents' } }">Incidents </v-tab>
        </v-tabs>
      </template>
    </v-toolbar>
    <v-tabs-items :value="tab">
      <v-tab-item value="details"><details-tab /></v-tab-item>
      <v-tab-item disabled value="schema"><schema-tab /></v-tab-item>
      <v-tab-item value="queries"><queries-tab /></v-tab-item>
      <v-tab-item value="incidents"><incidents-tab /></v-tab-item>
    </v-tabs-items>
  </div>
</template>

<script>
import { mapActions } from "vuex"
import { mapFields } from "vuex-map-fields"
import DetailsTab from "@/data/source/DetailsTab.vue"
import IncidentsTab from "@/data/source/IncidentsTab.vue"
import QueriesTab from "@/data/source/QueriesTab.vue"
import SchemaTab from "@/data/source/SchemaTab.vue"
import NewEditSheet from "@/data/source/NewEditSheet.vue"

export default {
  name: "SourceDetails",
  components: {
    DetailsTab,
    IncidentsTab,
    QueriesTab,
    SchemaTab,
    NewEditSheet,
  },

  created() {
    this.fetchDetails()
  },

  computed: {
    ...mapFields("source", [
      "selected",
      "selected.name",
      "selected.source_status",
      "selected.alerts",
      "selected.loading",
      "dialogs.showEditSheet",
    ]),
    alertCount: function () {
      if (this.alerts) {
        return this.alerts.length
      }
      return 0
    },
    tab: function () {
      return this.$route.params.tab
    },
  },
  watch: {
    "$route.params.name": function () {
      this.fetchDetails()
    },
  },
  methods: {
    fetchDetails() {
      this.getDetails({ name: this.$route.params.name })
    },
    ...mapActions("source", ["getDetails", "createEditShow"]),
  },
}
</script>
