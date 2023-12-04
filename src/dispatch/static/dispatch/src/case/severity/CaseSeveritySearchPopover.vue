<script setup lang="ts">
import { onMounted, ref } from "vue"
import CaseSeverityApi from "@/case/severity/api"
import CaseApi from "@/case/api"
import SearchPopover from "@/components/SearchPopover.vue"
import { useSavingState } from "@/composables/useSavingState"
import type { Ref } from "vue"
import { useStore } from "vuex"

type CaseSeverity = {
  name: string
}

defineProps<{ caseSeverity: string }>()

const store = useStore()
const { setSaving } = useSavingState()
const caseSeveritys: Ref<CaseSeverity[]> = ref([])

onMounted(async () => {
  try {
    const options = { itemsPerPage: -1 }
    const response = await CaseSeverityApi.getAll(options)
    caseSeveritys.value = response.data.items.map((item: any) => item.name)
  } catch (error) {
    console.error("Error fetching case severities:", error)
  }
})

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
