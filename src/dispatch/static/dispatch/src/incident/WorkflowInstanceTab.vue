<template>
  <div>
    <div v-if="workflow_instances && workflow_instances.length">
      <span v-for="instance in workflow_instances" :key="instance.id">
        <v-card>
          <div>
            <v-card-title class="text-h5">
              {{ instance.workflow.name }}
            </v-card-title>
            <v-card-subtitle>{{ instance.workflow.description }}</v-card-subtitle>
            <v-list>
              <v-list-subheader>Details</v-list-subheader>
              <v-list-item :href="instance.weblink">
                <v-list-item-title>{{ capitalize(instance.status) }}</v-list-item-title>
                <v-list-item-subtitle>Status</v-list-item-subtitle>

                <template #append>
                  <v-icon>mdi-open-in-new</v-icon>
                </template>
              </v-list-item>

              <v-list-item :href="instance.creator.individual.weblink">
                <v-list-item-title>{{ instance.creator.individual.name }}</v-list-item-title>
                <v-list-item-subtitle>Creator</v-list-item-subtitle>

                <template #append>
                  <v-icon>mdi-open-in-new</v-icon>
                </template>
              </v-list-item>
              <v-list-item>
                <code>{{ instance.parameters }}</code>
                <v-list-item-subtitle>Parameters</v-list-item-subtitle>
              </v-list-item>
            </v-list>
            <v-list>
              <v-list-subheader>Artifacts</v-list-subheader>
              <span v-for="artifact in instance.artifacts" :key="artifact.id">
                <v-list-item :href="artifact.weblink">
                  <v-list-item-title>{{ artifact.name }}</v-list-item-title>
                  <v-list-item-subtitle>Name</v-list-item-subtitle>

                  <template #append>
                    <v-icon>mdi-open-in-new</v-icon>
                  </template>
                </v-list-item>
              </span>
            </v-list>
          </div>
        </v-card>
      </span>
    </div>
    <div v-else>
      <p class="text-center">No workflow data available.</p>
    </div>
  </div>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { capitalize } from "@/filters"

export default {
  name: "IncidentWorkflowInstanceTab",
  setup() {
    return { capitalize }
  },
  computed: {
    ...mapFields("incident", ["selected.workflow_instances"]),
  },
}
</script>
