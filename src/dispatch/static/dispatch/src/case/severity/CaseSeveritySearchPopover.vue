<script setup lang="ts">
import { watch, ref } from "vue"
import CaseSeverityApi from "@/case/severity/api"
import CaseApi from "@/case/api"
import SearchPopover from "@/components/SearchPopover.vue"
import { useSavingState } from "@/composables/useSavingState"
import type { Ref } from "vue"
import { useStore } from "vuex"

type CaseSeverity = {
  name: string
}

const props = defineProps<{ caseSeverity: string; project: string }>()

const store = useStore()
const { setSaving } = useSavingState()
const caseSeveritys: Ref<CaseSeverity[]> = ref([])
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

        const response = await CaseSeverityApi.getAll(options)
        caseSeveritys.value = response.data.items.map((item: any) => item.name)
      } catch (error) {
        console.error("Error fetching priorities:", error)
      }
    }
  },
  { immediate: true }
)

const selectCaseSeverity = async (caseSeverityName: string) => {
  // Fetch the participant object from the API
  const response = await CaseSeverityApi.getAll({
    filter: JSON.stringify([
      { and: [{ model: "CaseSeverity", field: "name", op: "==", value: caseSeverityName }] },
    ]),
  })

  const caseSeverity = response.data.items[0]

  // Get the case details from the Vuex store
  const caseDetails = store.state.case_management.selected
  caseDetails.case_severity = caseSeverity

  setSaving(true)
  await CaseApi.update(caseDetails.id, caseDetails)
  setSaving(false)
}
</script>

<template>
  <SearchPopover
    :items="caseSeveritys"
    :initialValue="caseSeverity"
    @item-selected="selectCaseSeverity"
    label="Set case severity..."
    :hotkeys="[]"
  />
</template>
