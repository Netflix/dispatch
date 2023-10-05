<template>
  <v-dialog v-model="display" max-width="350px">
    <template #activator="{ on }">
      <v-badge
        :value="numFilters"
        bordered
        overlap
        color="info"
        :content="numFilters"
        class="mt-3 mr-3"
      >
        <v-btn color="secondary" v-on="on">
          <v-icon left class="mr-1">mdi-filter</v-icon> Filter
        </v-btn>
      </v-badge>
    </template>
    <v-card>
      <v-card-title>
        <span class="headline">Timeline Filters</span>
      </v-card-title>
      <v-card-subtitle class="subtitle_top">
        Do <b>not show</b> the following types of events
      </v-card-subtitle>
      <v-list dense>
        <v-list-item>
          <v-list-item-content class="pl-5 pt-5">
            <v-row align="center">
              <v-simple-checkbox v-model="local_filters.assessment_updates" color="#e50815" />
              <v-icon left class="mr-2">mdi-priority-high</v-icon>
              Assessment updates
            </v-row>
            <span class="text-caption ml-5">Priority, severity, and status</span>
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content class="pl-5 pt-5">
            <v-row align="center">
              <v-simple-checkbox v-model="local_filters.user_curated_events" color="#e50815" />
              <v-icon left class="mr-2">mdi-text-account</v-icon>
              User-curated events
            </v-row>
            <span class="text-caption ml-5">Custom events and imported messages</span>
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content class="pl-5 pt-5">
            <v-row align="center">
              <v-simple-checkbox v-model="local_filters.field_updates" color="#e50815" />
              <v-icon left class="mr-2">mdi-subtitles-outline</v-icon>
              Field updates
            </v-row>
            <span class="text-caption ml-5">Fields like title, description, tags, type, etc.</span>
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content class="pl-5 pt-5">
            <v-row align="center">
              <v-simple-checkbox v-model="local_filters.participant_updates" color="#e50815" />
              <v-icon left class="mr-2">mdi-account-outline</v-icon>
              Participant updates
            </v-row>
            <span class="text-caption ml-5">Added/removed participants and role changes</span>
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content class="pl-5 pt-5">
            <v-row align="center">
              <v-simple-checkbox v-model="local_filters.other_events" color="#e50815" />
              <v-icon left class="mr-2">mdi-monitor-star</v-icon>
              Other events
            </v-row>
            <span class="text-caption ml-5">System events, resource creation, etc.</span>
          </v-list-item-content>
        </v-list-item>
      </v-list>
      <v-card-actions>
        <v-spacer />
        <v-btn color="info" text @click="applyFilters()"> Apply Filters </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { sum } from "lodash"
import { mapFields } from "vuex-map-fields"

export default {
  name: "IncidentTimelineFilterDialog",

  props: {
    projects: {
      type: Array,
      default: function () {
        return []
      },
    },
  },

  data() {
    return {
      display: false,
      local_filters: {
        field_updates: true,
        assessment_updates: false,
        user_curated_events: false,
        participant_updates: true,
        other_events: true,
      },
    }
  },

  computed: {
    ...mapFields("incident", ["timeline_filters"]),
    numFilters: function () {
      return sum(Object.values(this.timeline_filters))
    },
  },

  methods: {
    applyFilters() {
      this.timeline_filters = structuredClone(this.local_filters)
      this.display = false
    },
  },

  created() {
    this.$watch(
      (vm) => [vm.display],
      () => {
        if (this.display) {
          // copy actual to local on dialog show
          this.local_filters = structuredClone(this.timeline_filters)
        }
      }
    )
  },
}
</script>

<style scoped lang="scss">
.subtitle_top {
  margin-top: -10px;
}
</style>
