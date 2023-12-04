<script setup lang="ts">
import { ref, onMounted } from "vue"
import ProjectApi from "@/project/api"
import SearchPopover from "@/components/SearchPopover.vue"
import { useSavingState } from "@/composables/useSavingState"

import type { Ref } from "vue"
import { useStore } from "vuex"
import CaseApi from "@/case/api"

type Project = {
  name: string
}

const store = useStore()

defineProps<{ project: string }>()
const { setSaving } = useSavingState()
const projects: Ref<Project[]> = ref([])

onMounted(async () => {
  try {
    const options = { itemsPerPage: -1 }
    const response = await ProjectApi.getAll(options)
    projects.value = response.data.items.map((item: any) => item.name)
  } catch (error) {
    console.error("Error fetching projects:", error)
  }
})

const selectProject = async (projectName: string) => {
  // Fetch the participant object from the API
  const response = await ProjectApi.getAll({
    filter: JSON.stringify([
      { and: [{ model: "Project", field: "name", op: "==", value: projectName }] },
    ]),
  })

  const project = response.data.items[0]

  const caseDetails = store.state.case_management.selected

  caseDetails.project = project

  setSaving(true)
  CaseApi.update(caseDetails.id, caseDetails)
    .then(() => console.log("Case details updated successfully"))
    .catch((e) => console.error("Failed to update case details", e))
  setSaving(false)
}
</script>

<template>
  <SearchPopover
    :items="projects"
    :initialValue="project"
    label="Set project to..."
    @item-selected="selectProject"
    :hotkeys="[]"
  />
</template>
