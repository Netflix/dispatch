<template>
  <v-row no-gutters align="center">
    <v-col cols="12" sm="11">
      <base-combobox
        :label="label"
        :api="signalEngagementApi"
        :project="project"
        v-model="engagements"
      >
        <template #selection="{ item, props: chipProps }">
          <v-menu origin="overlap">
            <template #activator="{ props: activatorProps }">
              <v-chip
                v-bind="mergeProps(chipProps, activatorProps)"
                pill
                @click:close="remove(item)"
              >
                {{ item ? item.title : "Unknown" }}
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
      <signal-engagement-create-dialog @save="createItem" />
    </v-col>
  </v-row>
</template>

<script>
import { mergeProps } from "vue"
import BaseCombobox from "@/components/BaseCombobox.vue"
import SignalEngagementApi from "@/signal/engagement/api"
import SignalEngagementCreateDialog from "@/signal/engagement/SignalEngagementCreateDialog.vue"

export default {
  name: "SignalEngagementCombobox",
  components: {
    BaseCombobox,
    SignalEngagementCreateDialog,
  },
  props: {
    modelValue: {
      type: Array,
      default: () => [],
    },
    label: {
      type: String,
      default: "Add Engagement(s)",
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
      signalEngagementApi: SignalEngagementApi,
      items: [],
    }
  },
  computed: {
    engagements: {
      get() {
        return this.modelValue
      },
      set(value) {
        this.$emit("update:modelValue", value)
      },
    },
  },

  methods: {
    createItem(value) {
      this.items.push(value)
      this.engagements.push(value)
    },
    initials(item) {
      if (!item) {
        return "Unknown"
      }
      return this.$options.filters.initials(item.name)
    },
    remove(item) {
      this.engagements.splice(this.engagements.indexOf(item), 1)
    },
  },
}
</script>
