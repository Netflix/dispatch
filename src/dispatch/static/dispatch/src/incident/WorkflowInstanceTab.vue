<template>
  <div>
    <div v-if="workflow_instances && workflow_instances.length">
      <span v-for="instance in workflow_instances" :key="instance.id">
        <v-card>
          <div>
            <v-card-title class="headline">
              {{ instance.workflow.name }}
            </v-card-title>
            <v-card-subtitle>{{ instance.workflow.description }}</v-card-subtitle>
            <v-list subheader>
              <v-subheader>Details</v-subheader>
              <v-list-item :href="instance.weblink">
                <v-list-item-content>
                  <v-list-item-title>{{ instance.status | capitalize }}</v-list-item-title>
                  <v-list-item-subtitle>Status</v-list-item-subtitle>
                </v-list-item-content>

                <v-list-item-icon>
                  <v-icon>open_in_new</v-icon>
                </v-list-item-icon>
              </v-list-item>

              <v-list-item :href="instance.creator.individual.weblink">
                <v-list-item-content>
                  <v-list-item-title>{{ instance.creator.individual.name }}</v-list-item-title>
                  <v-list-item-subtitle>Creator</v-list-item-subtitle>
                </v-list-item-content>

                <v-list-item-icon>
                  <v-icon>open_in_new</v-icon>
                </v-list-item-icon>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <code>{{ instance.parameters }}</code>
                  <v-list-item-subtitle>Parameters</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-list>
            <v-list subheader>
              <v-subheader>Artifacts</v-subheader>
              <span v-for="artifact in instance.artifacts" :key="artifact.id">
                <v-list-item :href="artifact.weblink">
                  <v-list-item-content>
                    <v-list-item-title>{{ artifact.name }}</v-list-item-title>
                    <v-list-item-subtitle>Name</v-list-item-subtitle>
                  </v-list-item-content>
                  <v-list-item-icon>
                    <v-icon>open_in_new</v-icon>
                  </v-list-item-icon>
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

export default {
  name: "IncidentWorkflowInstanceTab",
  computed: {
    ...mapFields("incident", ["selected.workflow_instances"]),
  },
}
</script>
