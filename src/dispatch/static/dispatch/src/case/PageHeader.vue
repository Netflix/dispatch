<template>
  <v-app-bar class="border-bottom" elevation="0" density="compact" scroll-behavior="fixed">
    <v-breadcrumbs :items="breadcrumbItems" class="pl-7 text-subtitle-2" density="compact">
      <template #divider>
        <v-icon size="x-small" icon="mdi-chevron-right" />
      </template>
    </v-breadcrumbs>
    <template #append>
      <FancyTooltip text="View case participants" :hotkeys="['L', 'q']">
        <template #activator="{ tooltip }">
          <AvatarGroup :participants="caseParticipants" class="pl-3" v-bind="tooltip" />
        </template>
      </FancyTooltip>
      <LockButton :case-visibility="caseVisibility" class="ml-n2 mr-n2" />
      <EscalateButton class="ml-n4" />
      <v-divider vertical inset />
      <FancyTooltip text="Case details" :hotkeys="['⌘', '⇧', 'I']">
        <template #activator="{ tooltip }">
          <v-btn variant="plain" :ripple="false" @click="toggleDrawer" v-bind="tooltip">
            <v-icon>{{ isDrawerOpen ? "mdi-book-open" : "mdi-book-open-outline" }}</v-icon>
          </v-btn>
        </template>
      </FancyTooltip>
    </template>
  </v-app-bar>
</template>

<script setup lang="ts">
import { useRoute } from "vue-router"
import { computed, ref, defineEmits } from "vue"
import LockButton from "@/components/LockButton.vue"
import FancyTooltip from "@/components/FancyTooltip.vue"
import AvatarGroup from "@/participant/AvatarGroup.vue"
import CaseApi from "@/case/api"

const route = useRoute()

const props = defineProps({
  caseName: {
    type: String,
    required: true,
  },
  caseVisibility: {
    type: String,
    required: true,
  },
  caseStatus: {
    type: String,
    required: true,
  },
  isDrawerOpen: {
    type: Boolean,
    default: true,
  },
})

const caseParticipants = ref([])
const loading = ref(false)

const fetchParticipants = async () => {
  const caseId = route.params.id
  loading.value = true
  try {
    // get case participants
    CaseApi.getParticipants(caseId).then((response) => {
      caseParticipants.value = response.data
    })
    loading.value = false
  } catch (e) {
    console.error("Failed to fetch case participants", e)
    loading.value = false
  }
}

const emit = defineEmits(["toggle-drawer"])

const toggleDrawer = () => {
  emit("toggle-drawer")
}

const breadcrumbItems = computed(() => {
  let items = [
    {
      title: "Cases",
      disabled: false,
      href: `/${route.params.organization}/cases`,
    },
    {
      title: props.caseName,
      disabled: true,
    },
  ]
  return items
})

// Fetch participants immediately when the component is created
fetchParticipants()
</script>

<style scoped>
.border-bottom {
  border-bottom: 1px solid rgb(228, 228, 228); /* Adjust color and thickness as needed */
}
</style>
