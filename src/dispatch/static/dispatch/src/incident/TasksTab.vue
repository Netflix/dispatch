<template>
  <div>
    <div v-if="tasks && tasks.length">
      <span v-for="task in tasks" :key="task.id">
        <v-list-item :href="task.weblink" target="_blank">
          <v-list-item-content>
            <v-list-item-title style="width: 200px" class="text-truncate">
              {{ task.description }}
            </v-list-item-title>
            <v-list-item-subtitle>
              <strong>Created:</strong> {{ task.created_at | formatRelativeDate }}
              | <strong>Status:</strong> {{ task.status }}
              | <strong>Assignees:</strong> {{ task.assignees | individualNames }}
            </v-list-item-subtitle>
          </v-list-item-content>
          <v-list-item-action>
            <v-list-item-icon>
              <v-icon>open_in_new</v-icon>
            </v-list-item-icon>
          </v-list-item-action>
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
import map from "lodash"
import { mapFields } from "vuex-map-fields"

export default {
  name: "IncidentTasksTab",

  computed: {
    ...mapFields("incident", ["selected.tasks"]),
  },
}
</script>
