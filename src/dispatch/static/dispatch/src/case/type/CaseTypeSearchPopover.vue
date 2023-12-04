<script setup lang="ts">
import { onMounted, ref } from "vue"
import CaseTypeApi from "@/case/type/api"
import CaseApi from "@/case/api"
import SearchPopover from "@/components/SearchPopover.vue"
import { useSavingState } from "@/composables/useSavingState"
import type { Ref } from "vue"
import { useStore } from "vuex"

type CaseType = {
  name: string
}

defineProps<{ caseType: string }>()

const store = useStore()
const { setSaving } = useSavingState()
const caseTypes: Ref<CaseType[]> = ref([])

onMounted(async () => {
  try {
    const response = await CaseTypeApi.getAll()
    caseTypes.value = response.data.items.map((item: any) => item.name)
  } catch (error) {
    console.error("Error fetching case types:", error)
  }
})

const selectCaseType = async (caseTypeName: string) => {
  // Fetch the participant object from the API
  const response = await CaseTypeApi.getAll({
    filter: JSON.stringify([
      { and: [{ model: "CaseType", field: "name", op: "==", value: caseTypeName }] },
    ]),
    itemsPerPage: -1,
  })

  const caseType = response.data.items[0]

  // Get the case details from the Vuex store
  const caseDetails = store.state.case_management.selected
  caseDetails.case_type = caseType

  setSaving(true)
  await CaseApi.update(caseDetails.id, caseDetails)
  setSaving(false)
}
</script>

<template>
  <SearchPopover
    :items="caseTypes"
    :initialValue="caseType"
    @item-selected="selectCaseType"
    label="Set case type..."
    :hotkeys="[]"
  >
    <template #default="{ item }">
      <v-list-item-title class="dispatch-text-title">{{ item }}</v-list-item-title>
    </template>
  </SearchPopover>
</template>

<style lang="scss" scoped>
@import "@/styles/index.scss";
</style>
