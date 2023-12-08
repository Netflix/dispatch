<script setup lang="ts">
import { ref, watch } from "vue"
import CasePriorityApi from "@/case/priority/api"
import CaseApi from "@/case/api"
import SearchPopover from "@/components/SearchPopover.vue"
import { useSavingState } from "@/composables/useSavingState"
import type { Ref } from "vue"
import { useStore } from "vuex"

type CasePriority = {
  name: string
}

const props = defineProps<{ casePriority: string; project: string }>()

const store = useStore()
const { setSaving } = useSavingState()
const casePriorities: Ref<CasePriority[]> = ref([])
const currentProject: Ref<string> = ref(props.project)

watch(
  () => props.project,
  async (newVal) => {
    currentProject.value = newVal
    if (newVal) {
      try {
        const options = {
          itemsPerPage: -1,
          filter: JSON.stringify([
            { and: [{ model: "Project", field: "name", op: "==", value: newVal }] },
          ]),
        }

        const response = await CasePriorityApi.getAll(options)
        casePriorities.value = response.data.items.map((item: any) => item.name)
      } catch (error) {
        console.error("Error fetching priorities:", error)
      }
    }
  },
  { immediate: true }
)

const selectCasePriority = async (casePriorityName: string) => {
  // Fetch the participant object from the API
  const response = await CasePriorityApi.getAll({
    filter: JSON.stringify([
      { and: [{ model: "CasePriority", field: "name", op: "==", value: casePriorityName }] },
    ]),
  })

  const caseType = response.data.items[0]

  // Get the case details from the Vuex store
  const caseDetails = store.state.case_management.selected
  caseDetails.case_priority = caseType

  setSaving(true)
  await CaseApi.update(caseDetails.id, caseDetails)
  setSaving(false)
}
</script>

<template>
  <SearchPopover
    :items="casePriorities"
    :initialValue="casePriority"
    @item-selected="selectCasePriority"
    label="Set priority..."
    :hotkeys="[]"
  />
</template>
