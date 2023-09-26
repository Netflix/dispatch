<template>
  <v-menu v-model="menu" origin="overlap">
    <template #activator="{ props }">
      <v-btn icon variant="text" size="small" v-bind="props">
        <v-icon>mdi-chevron-down</v-icon>
      </v-btn>
    </template>
    <v-card width="400">
      <v-list dark>
        <v-list-item>
          <v-list-item-title>Workflow Details</v-list-item-title>

          <template #append>
            <v-btn icon variant="text" @click="menu = false">
              <v-icon>mdi-close-circle</v-icon>
            </v-btn>
          </template>
        </v-list-item>
      </v-list>
      <v-list>
        <v-list-item>
          <template #prepend>
            <v-icon>mdi-text-box</v-icon>
          </template>

          <v-list-item-subtitle>Parameters</v-list-item-subtitle>
        </v-list-item>
        <v-list-item v-if="value.parameters">
          <template #prepend>
            <v-icon>mdi-code-json</v-icon>
          </template>

          <v-list-item-subtitle>
            <pre>{{ value.parameters }}</pre>
          </v-list-item-subtitle>
        </v-list-item>
      </v-list>
    </v-card>
  </v-menu>
</template>
<script>
export default {
  name: "WorkflowInstanceDetailMenu",
  props: {
    value: {
      type: Object,
      default: function () {
        return {}
      },
    },
  },
  data() {
    return {
      menu: false,
    }
  },
}
</script>
