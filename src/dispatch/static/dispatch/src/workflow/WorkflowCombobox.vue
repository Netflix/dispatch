<template>
  <base-combobox
    :value="value"
    :label="label"
    :api="workflowApi"
    :project="project"
    v-bind="$attrs"
    v-on="$listeners"
  >
    <template #selection="{ attr, item, selected }">
      <v-menu bottom right transition="scale-transition" origin="top left">
        <template v-slot:activator="{ on }">
          <v-chip v-bind="attr" :input-value="selected" pill v-on="on">
            {{ item ? item.name : "Unknown" }}
          </v-chip>
        </template>
        <v-card>
          <v-list dark>
            <v-list-item>
              <v-list-item-avatar color="teal">
                <span class="white--text">{{ initials(item) }}</span>
              </v-list-item-avatar>
              <v-list-item-content>
                <v-list-item-title>{{ item ? item.name : "Unknown" }}</v-list-item-title>
                <v-list-item-subtitle>{{ item ? item.type : "Unknown" }}</v-list-item-subtitle>
              </v-list-item-content>
              <v-list-item-action>
                <v-btn icon>
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
              <v-list-item-subtitle>{{ item ? item.description : "Unknown" }}</v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </v-card>
      </v-menu>
    </template>
  </base-combobox>
</template>

<script>
import BaseCombobox from "@/components/BaseCombobox.vue"
import WorkflowApi from "@/workflow/api"

export default {
  name: "WorkflowCombobox",
  components: {
    BaseCombobox,
  },
  props: {
    value: {
      type: Array,
      default: () => [],
    },
    label: {
      type: String,
      default: "Add Workflow(s)",
    },
    project: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      workflowApi: WorkflowApi,
    }
  },
  methods: {
    // ...
    initials(item) {
      if (!item) {
        return "Unknown"
      }
      return this.$options.filters.initials(item.name)
    },
  },
}
</script>
