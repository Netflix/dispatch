<script setup lang="ts">
import { onMounted, ref } from "vue"
import CaseSeverityApi from "@/case/severity/api"
import CaseApi from "@/case/api"
import SearchPopover from "@/components/SearchPopover.vue"
import type { Ref } from "vue"
import { useStore } from "vuex"

type CaseSeverity = {
  name: string
}

defineProps<{ caseSeverity: string }>()

const store = useStore()

const caseSeveritys: Ref<CaseSeverity[]> = ref([])

onMounted(async () => {
  try {
    const response = await CaseSeverityApi.getAll()
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

  await CaseApi.update(caseDetails.id, caseDetails)
}
</script>

<template>
  <SearchPopover
    :items="caseSeveritys"
    :initialValue="caseSeverity"
    @item-selected="selectCaseSeverity"
    label="Set case severity..."
    :hotkeys="[]"
  >
    <template v-slot:default="{ item }">
      <v-list-item-title class="dispatch-text-title">{{ item }}</v-list-item-title>
    </template>
  </SearchPopover>
</template>

<style lang="scss" scoped>
@import "@/styles/index.scss";
</style>
