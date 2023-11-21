<template>
  <v-tabs v-model="tab" background-color="transparent" grow>
    <v-tab key="main">
      <v-skeleton-loader v-if="internalLoading" type="text"></v-skeleton-loader>
      <v-icon v-else dense small> mdi-clock-outline </v-icon>
      Timeline
    </v-tab>
    <v-tab key="resources">
      <v-icon dense small> mdi-semantic-web </v-icon>
      Resources
    </v-tab>
    <v-tab key="signals" :disabled="signalInstances?.length === 0">
      <v-icon dense small> mdi-broadcast </v-icon>
      Signals
      <v-badge v-if="signalInstances?.length" inline :content="signalInstances?.length"> </v-badge>
    </v-tab>
    <v-tab key="entities" :disabled="entities?.length === 0">
      <v-icon dense small> mdi-account-group </v-icon>
      Entities
      <v-badge v-if="entities?.length" inline :content="entities?.length"> </v-badge>
    </v-tab>
  </v-tabs>
  <v-divider></v-divider>
  <v-window v-model="tab">
    <v-window-item key="main" class="tab">
      <case-timeline-tab v-model="events"></case-timeline-tab>
    </v-window-item>
    <v-window-item key="resources" class="tab">
      <case-resources-tab v-model="resources"></case-resources-tab>
    </v-window-item>
    <v-window-item key="signals" class="tab">
      <case-signal-instance-tab
        :loading="loading"
        v-model="signalInstances"
        :selected-signal-id="selectedSignalId"
      />
    </v-window-item>
    <v-window-item key="entities" class="tab">
      <entities-tab v-model="entities" />
    </v-window-item>
  </v-window>
</template>

<script>
import { ref, watch, toRefs } from "vue"
import CaseResourcesTab from "@/case/ResourcesTab.vue"
import EntitiesTab from "@/entity/EntitiesTab.vue"
import CaseSignalInstanceTab from "@/case/CaseSignalInstanceTab.vue"
import CaseTimelineTab from "@/case/TimelineTab.vue"

export default {
  name: "CaseTabs",
  props: {
    modelValue: {
      type: Object,
      default: () => ({
        signal_instances: [],
        resources: [],
        entities: [],
        events: [],
      }),
      required: true,
    },
    loading: {
      type: Boolean,
      default: false,
    },
    selectedSignalId: {
      type: String,
      default: "",
    },
  },
  components: {
    CaseResourcesTab,
    EntitiesTab,
    CaseSignalInstanceTab,
    CaseTimelineTab,
  },
  setup(props) {
    const tab = ref(null)
    const { modelValue, loading } = toRefs(props)
    const signalInstances = ref(props.modelValue.signal_instances)
    const internalLoading = ref(props.loading)
    const resources = ref(props.modelValue.resources)
    const entities = ref(props.modelValue.entities)
    const events = ref(props.modelValue.events)
    console.log("Got events for timeline", events)

    watch(loading, (newValue) => {
      internalLoading.value = newValue
    })

    watch(modelValue, (newValue) => {
      signalInstances.value = newValue.signal_instances
      resources.value = newValue.resources
      entities.value = newValue.entities
      events.value = newValue.events
    })

    watch(
      () => props.selectedSignalId,
      (id) => {
        if (id) {
          tab.value = "signals" // Assuming 'signals' is the key for the signals tab
        }
      }
    )

    return {
      tab,
      signalInstances,
      internalLoading,
      events,
      resources,
      entities,
    }
  },
}
</script>
<style scoped>
.v-tab {
  text-transform: initial; /* Keeping the text's original state */
  color: #272727; /* Slightly darker shade of gray for better contrast and readability */
  font-weight: 400; /* Normal text-weight */
  letter-spacing: normal;
  line-height: 1.5; /* Spacing for better readability */
  font-family: "Inter", sans-serif; /* A modern, readable typeface */
}
.tab {
  transition: all 0.2s ease;
}
</style>
