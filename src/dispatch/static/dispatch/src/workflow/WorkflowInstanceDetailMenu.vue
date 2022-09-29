<template>
  <v-menu v-model="menu" bottom right transition="scale-transition" origin="top right">
    <template v-slot:activator="{ on }">
      <v-btn icon small v-on="on"><v-icon>mdi-chevron-down</v-icon></v-btn>
    </template>
    <v-card width="400">
      <v-list dark>
        <v-list-item>
          <v-list-item-content>
            <v-list-item-title>Workflow Details</v-list-item-title>
          </v-list-item-content>
          <v-list-item-action>
            <v-btn icon @click="menu = false">
              <v-icon>mdi-close-circle</v-icon>
            </v-btn>
          </v-list-item-action>
        </v-list-item>
      </v-list>
      <v-list>
        <v-list-item>
          <v-list-item-action>
            <v-icon>mdi-text-box</v-icon>
          </v-list-item-action>
          <v-list-item-subtitle>Parameters</v-list-item-subtitle>
        </v-list-item>
        <v-list-item v-if="value.parameters">
          <v-list-item-action>
            <v-icon>mdi-code-json</v-icon>
          </v-list-item-action>
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
