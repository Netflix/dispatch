<template>
  <v-dialog v-model="display" max-width="350px">
    <template #activator="{ props }">
      <v-badge
        :model-value="numFilters"
        bordered
        color="info"
        :content="numFilters"
        class="mt-3 mr-3"
      >
        <v-btn color="secondary" v-bind="props">
          <v-icon start class="mr-1">mdi-filter</v-icon> Filter
        </v-btn>
      </v-badge>
    </template>
    <v-card>
      <v-card-title>
        <span class="text-h5">Timeline Filters</span>
      </v-card-title>
      <v-card-subtitle class="subtitle_top">
        Only show the following types of events
      </v-card-subtitle>
      <v-list density="compact">
        <v-list-item>
          <template #prepend>
            <v-checkbox-btn v-model="local_filters.assessment_updates" color="#e50815" />
          </template>
          <v-list-item-title>
            <v-icon start class="mr-2">mdi-priority-high</v-icon>
            Assessment updates
          </v-list-item-title>
          <v-list-item-subtitle>Priority, severity, and status</v-list-item-subtitle>
        </v-list-item>
        <v-list-item>
          <template #prepend>
            <v-checkbox-btn v-model="local_filters.user_curated_events" color="#e50815" />
          </template>
          <v-list-item-title>
            <v-icon start class="mr-2">mdi-text-account</v-icon>
            User-curated events
          </v-list-item-title>
          <v-list-item-subtitle>Custom events and imported messages</v-list-item-subtitle>
        </v-list-item>
        <v-list-item>
          <template #prepend>
            <v-checkbox-btn v-model="local_filters.field_updates" color="#e50815" />
          </template>
          <v-list-item-title>
            <v-icon start class="mr-2">mdi-subtitles-outline</v-icon>
            Field updates
          </v-list-item-title>
          <v-list-item-subtitle>
            Fields like title, description, tags, type, etc.
          </v-list-item-subtitle>
        </v-list-item>
        <v-list-item>
          <template #prepend>
            <v-checkbox-btn v-model="local_filters.participant_updates" color="#e50815" />
          </template>
          <v-list-item-title>
            <v-icon start class="mr-2">mdi-account-outline</v-icon>
            Participant updates
          </v-list-item-title>
          <v-list-item-subtitle>Added/removed participants and role changes</v-list-item-subtitle>
        </v-list-item>
        <v-list-item>
          <template #prepend>
            <v-checkbox-btn v-model="local_filters.other_events" color="#e50815" />
          </template>
          <v-list-item-title>
            <v-icon start class="mr-2">mdi-monitor-star</v-icon>
            Other events
          </v-list-item-title>
          <v-list-item-subtitle>System events, resource creation, etc.</v-list-item-subtitle>
        </v-list-item>
      </v-list>
      <v-card-actions>
        <v-spacer />
        <v-btn color="info" variant="text" @click="applyFilters()"> Apply Filters </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { sum } from "lodash"
import { mapFields } from "vuex-map-fields"

function invertBooleanValues(obj) {
  return Object.keys(obj).reduce((acc, key) => {
    acc[key] = !obj[key]
    return acc
  }, {})
}

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
        field_updates: false,
        assessment_updates: true,
        user_curated_events: true,
        participant_updates: false,
        other_events: false,
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
      this.timeline_filters = invertBooleanValues(this.local_filters)
      this.display = false
    },
  },

  created() {
    this.$watch(
      (vm) => [vm.display],
      () => {
        if (this.display) {
          // copy actual to local on dialog show
          this.local_filters = invertBooleanValues(this.timeline_filters)
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
