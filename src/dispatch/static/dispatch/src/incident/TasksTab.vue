<template>
  <div>
    <task-edit-dialog v-if="showEditTaskDialog" />
    <div v-if="tasks && tasks.length">
      <div class="text-h6 ml-4 mt-6">Open tasks</div>
      <span
        v-for="task in tasks
          .filter((task) => task.status === 'Open')
          .sort((a, b) => new Date(a.resolve_by) - new Date(b.resolve_by))"
        :key="task.id"
      >
        <v-list-item @click="showNewTaskDialog(task)">
          <v-list-item-title class="text-wrap">
            {{ task.description }}
          </v-list-item-title>
          <v-list-item-subtitle>
            <span
              ><strong>Created:</strong> {{ formatRelativeDate(task.created_at) }} |
              <strong>Status:</strong> {{ task.status }} | <strong>Assignee:</strong>
              {{ individualNames(task.assignees) }} | <strong>Due:</strong>
              {{ formatRelativeDate(task.resolve_by) }}
            </span>
          </v-list-item-subtitle>
          <template #append>
            <v-menu location="right" origin="overlap">
              <template #activator="{ props }">
                <v-btn icon variant="text" v-bind="props">
                  <v-icon>mdi-dots-vertical</v-icon>
                </v-btn>
              </template>
              <v-list>
                <v-list-item @click="showNewTaskDialog(task)">
                  <v-list-item-title>View / Edit</v-list-item-title>
                </v-list-item>
                <v-list-item :href="task.weblink" target="_blank">
                  <v-list-item-title>Go to task</v-list-item-title>
                </v-list-item>
                <v-list-item @click="menu = true">
                  <v-list-item-title>Create ticket</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
          </template>
        </v-list-item>
        <v-divider />
      </span>
      <div class="text-h6 ml-4 mt-6">Resolved tasks</div>
      <span
        v-for="task in tasks
          .filter((task) => task.status === 'Resolved')
          .sort((a, b) => new Date(a.resolved_at) - new Date(b.resolved_at))"
        :key="task.id"
      >
        <v-list-item @click="showNewTaskDialog(task)">
          <v-list-item-title class="text-wrap">
            {{ task.description }}
          </v-list-item-title>
          <v-list-item-subtitle>
            <span
              ><strong>Created:</strong> {{ formatRelativeDate(task.created_at) }} |
              <strong>Status:</strong> {{ task.status }} | <strong>Assignee:</strong>
              {{ individualNames(task.assignees) }} | <strong>Resolved:</strong>
              {{ formatRelativeDate(task.resolved_at) }}
            </span>
          </v-list-item-subtitle>
          <template #append>
            <v-menu location="right" origin="overlap">
              <template #activator="{ props }">
                <v-btn icon variant="text" v-bind="props">
                  <v-icon>mdi-dots-vertical</v-icon>
                </v-btn>
              </template>
              <v-list>
                <v-list-item @click="showNewTaskDialog(task)">
                  <v-list-item-title>View / Edit</v-list-item-title>
                </v-list-item>
                <v-list-item :href="task.weblink" target="_blank">
                  <v-list-item-title>Go to task</v-list-item-title>
                </v-list-item>
                <v-list-item @click="createTicket(task)">
                  <v-list-item-title>Create ticket</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
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
import { mapActions } from "vuex"
import { formatRelativeDate, individualNames } from "@/filters"
import TaskEditDialog from "@/incident/TaskEditDialog.vue"

export default {
  name: "IncidentTasksTab",

  components: {
    TaskEditDialog,
  },
  setup() {
    return { formatRelativeDate, individualNames }
  },

  computed: {
    ...mapFields("incident", ["selected.tasks", "dialogs.showEditTaskDialog"]),
  },

  methods: {
    ...mapActions("incident", ["showNewTaskDialog"]),
  },
}
</script>
