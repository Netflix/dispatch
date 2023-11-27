<template>
  <div>
    <div class="pl-6 pr-8">
      <div class="button-group-container">
        <v-btn-toggle
          v-model="tab"
          mandatory
          variant="outlined"
          rounded="lg"
          selected-class="selected-button"
        >
          <v-btn
            class="text-subtitle-2 unselected-button"
            height="24px"
            value="main"
            variant="plain"
            :ripple="false"
          >
            <span class="button-text">Timeline</span>
          </v-btn>
          <v-btn
            class="text-subtitle-2 unselected-button"
            height="24px"
            value="signals"
            variant="plain"
            :ripple="false"
            :disabled="signalInstances?.length === 0"
          >
            <span class="button-text">Alerts</span>
            <v-badge
              v-if="signalInstances?.length"
              inline
              :content="signalInstances?.length"
              class="small-badge"
            >
            </v-badge>
          </v-btn>
          <v-btn
            class="text-subtitle-2 unselected-button"
            height="24px"
            value="graph"
            variant="plain"
            :ripple="false"
            :disabled="entities?.length === 0"
          >
            <span class="button-text">Graph</span>
            <v-badge v-if="entities?.length" inline :content="entities?.length"> </v-badge>
          </v-btn>
        </v-btn-toggle>
      </div>
      <v-divider></v-divider>
    </div>

    <v-window v-model="tab">
      <v-window-item value="main" class="tab">
        <case-timeline-tab v-model="events"></case-timeline-tab>
      </v-window-item>
      <v-window-item value="signals" class="tab">
        <case-signal-instance-tab
          :loading="loading"
          v-model="signalInstances"
          :selected-signal-id="selectedSignalId"
        />
      </v-window-item>
      <v-window-item value="graph" class="tab">
        <GraphTab :signal-instances="signalInstances" />
      </v-window-item>
    </v-window>
  </div>
</template>

<script>
import { ref, watch, toRefs } from "vue"
import { useRoute, useRouter } from "vue-router"

import GraphTab from "@/case/GraphTab.vue"
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
  },
  components: {
    CaseResourcesTab,
    EntitiesTab,
    CaseSignalInstanceTab,
    CaseTimelineTab,
    GraphTab,
  },
  setup(props) {
    const tab = ref("main")
    const route = useRoute()
    const router = useRouter()

    const { modelValue, loading } = toRefs(props)
    const signalInstances = ref(props.modelValue.signal_instances)
    const internalLoading = ref(props.loading)
    const resources = ref(props.modelValue.resources)
    const entities = ref(props.modelValue.entities)
    const events = ref(props.modelValue.events)
    console.log("Got events for timeline", events)
    console.log("Got signalInstances", signalInstances.value)

    watch(loading, (newValue) => {
      internalLoading.value = newValue
    })

    watch(modelValue, (newValue) => {
      signalInstances.value = newValue.signal_instances
      console.log("Got signalInstances", signalInstances.value)
      resources.value = newValue.resources
      entities.value = newValue.entities
      events.value = newValue.events
    })

    watch(
      () => tab.value,
      (tabValue) => {
        if (tabValue === "main") {
          router.push({ name: "CasePage", params: { id: route.id } })
        }

        if (tabValue === "signals") {
          router.push({
            name: "SignalDetails",
            params: { signal_id: signalInstances.value[0].raw.id },
          })
        }
      }
    )

    watch(
      () => route.params,
      (newParams) => {
        const newSignalId = newParams.signal_id
        if (newSignalId) {
          tab.value = "signals"
        }
      },
      { immediate: true, deep: true }
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

.button-group-container {
  background-color: rgb(244, 245, 248);
  margin-bottom: 10px;
  border-radius: 8px; /* Adjust as necessary */
  z-index: 1;
  height: 24px !important;

  transform: scale(0.95);
  display: inline-flex; /* Shrink container to content's size */
}

.selected-button {
  background: white !important;
  background-color: white !important;
  color: white !important;
  box-shadow: rgba(0, 0, 0, 0.09) 0px 1px 4px;
  border: 1px solid black !important;
  border-color: rgb(223, 225, 228) !important;
  height: 24px !important;
  border-width: 1px;
  border-radius: 7px !important; /* Adjust the value as necessary */
}

.small-badge {
  transform: scale(0.9);
}

.selected-button .button-text {
  color: rgb(40, 42, 28) !important;
}

.selected-button.v-btn--variant-plain {
  opacity: 1 !important;
}

/* .unselected-button {
  border: none !important;
  color: rgb(107, 111, 118);
  background-color: rgb(244, 245, 248);
} */
</style>
