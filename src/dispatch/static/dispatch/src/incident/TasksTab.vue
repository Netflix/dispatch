<template>
  <div>
    <div v-if="tasks && tasks.length">
      <span v-for="task in tasks" :key="task.id">
        <v-list-item :href="task.weblink" target="_blank">
          <v-list-item-title style="width: 200px" class="text-truncate">
            {{ task.description }}
          </v-list-item-title>
          <v-list-item-subtitle>
            <strong>Created:</strong> {{ formatRelativeDate(task.created_at) }} |
            <strong>Status:</strong> {{ task.status }} | <strong>Assignees:</strong>
            {{ individualNames(task.assignees) }}
          </v-list-item-subtitle>

          <template #append>
            <v-icon>mdi-open-in-new</v-icon>
          </template>
        </v-list-item>
        <v-divider />
      </span>
    </div>
    <div v-else>
      <p class="text-center">No tasks have been created for this incident.</p>
    </div>
  </div>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { formatRelativeDate, individualNames } from "@/filters"

export default {
  name: "IncidentTasksTab",

  setup() {
    return { formatRelativeDate, individualNames }
  },

  computed: {
    ...mapFields("incident", ["selected.tasks"]),
  },
}
</script>
