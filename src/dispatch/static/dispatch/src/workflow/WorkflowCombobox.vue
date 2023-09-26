<template>
  <v-row no-gutters align="center">
    <v-col cols="12" sm="11">
      <base-combobox
        :value="value"
        :label="label"
        :api="workflowApi"
        :project="project"
        v-bind="$attrs"
        v-model="workflows"
      >
        <template #selection="{ item, selected }">
          <v-menu origin="overlap">
            <template #activator="{ props }">
              <v-chip
                v-bind="props"
                :model-value="selected"
                pill
                closable
                @click:close="remove(item)"
              >
                {{ item ? item.name : "Unknown" }}
              </v-chip>
            </template>
            <v-card>
              <v-list dark>
                <v-list-item>
                  <template #prepend>
                    <v-avatar color="teal">
                      {{ initials(item) }}
                    </v-avatar>
                  </template>

                  <v-list-item-title>{{ item ? item.name : "Unknown" }}</v-list-item-title>
                  <v-list-item-subtitle>{{ item ? item.type : "Unknown" }}</v-list-item-subtitle>

                  <template #append>
                    <v-btn icon variant="text">
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

                  <v-list-item-subtitle>
                    {{ item ? item.description : "Unknown" }}
                  </v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-card>
          </v-menu>
        </template>
      </base-combobox>
    </v-col>
    <v-col cols="12" sm="1">
      <workflow-create-dialog
        v-model="createdItem"
        :project="project"
        :signalDefinition="signalDefinition"
      />
    </v-col>
  </v-row>
</template>

<script>
import BaseCombobox from "@/components/BaseCombobox.vue"
import WorkflowApi from "@/workflow/api"
import WorkflowCreateDialog from "@/workflow/WorkflowCreateDialog.vue"

export default {
  name: "WorkflowCombobox",
  inheritAttrs: false,
  components: {
    BaseCombobox,
    WorkflowCreateDialog,
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
    signalDefinition: {
      type: Object,
      required: false,
    },
  },
  data() {
    return {
      workflowApi: WorkflowApi,
      createdItem: null,
    }
  },
  computed: {
    workflows: {
      get() {
        return this.value
      },
      set(value) {
        this.$emit("input", value)
      },
    },
  },
  methods: {
    // ...
    initials(item) {
      if (!item) {
        return "Unknown"
      }
      return this.$options.filters.initials(item.name)
    },
    remove(item) {
      this.workflows.splice(this.workflows.indexOf(item), 1)
    },
  },
}
</script>
