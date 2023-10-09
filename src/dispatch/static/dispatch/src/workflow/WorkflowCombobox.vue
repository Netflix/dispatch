<template>
  <v-row no-gutters align="center">
    <v-col cols="12" sm="11">
      <base-combobox
        :label="label"
        :api="workflowApi"
        :project="project"
        v-bind="$attrs"
        v-model="workflows"
      >
        <template #selection="{ item, props: chipProps }">
          <v-menu origin="overlap">
            <template #activator="{ props: activatorProps }">
              <v-chip
                v-bind="mergeProps(chipProps, activatorProps)"
                pill
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
      <workflow-create-dialog @save="createItem" :project="project" />
    </v-col>
  </v-row>
</template>

<script>
import { mergeProps } from "vue"
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
    modelValue: {
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
  setup() {
    return { mergeProps }
  },
  data() {
    return {
      workflowApi: WorkflowApi,
    }
  },
  computed: {
    workflows: {
      get() {
        return this.modelValue
      },
      set(value) {
        this.$emit("update:modelValue", value)
      },
    },
  },
  methods: {
    createItem() {
      // do nothing?
    },
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
