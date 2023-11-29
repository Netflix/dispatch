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

const props = defineProps<{ caseSeverity: string }>()

const store = useStore()

const caseSeveritys: Ref<CaseSeverity[]> = ref([])

onMounted(async () => {
  try {
    const response = await CaseSeverityApi.getAll()
    caseSeveritys.value = response.data.items.map((item: any) => item.name)
  } catch (error) {
    console.error("Error fetching priorities:", error)
  }
})

const selectCaseSeverity = async (caseSeverityName: string) => {
  // Handle selected case type here
  console.log(caseSeverityName)

  // Fetch the participant object from the API
  const response = await CaseSeverityApi.getAll({
    filter: JSON.stringify([
      { and: [{ model: "CaseSeverity", field: "name", op: "==", value: caseSeverityName }] },
    ]),
  })

  const caseSeverity = response.data.items[0]

  // Get the case details from the Vuex store
  const caseDetails = store.state.case_management.selected
  caseDetails.case_type = caseSeverity

  await CaseApi.update(caseDetails.id, caseDetails)
}
</script>

<template>
  <SearchPopover
    :items="caseSeveritys"
    :initialValue="caseSeverity"
    @item-selected="selectCaseSeverity"
    label="Set case type..."
    :hotkeys="['c']"
  >
    <template v-slot:default="{ item }">
      <v-list-item-title class="item-title-font">{{ item }}</v-list-item-title>
    </template>
  </SearchPopover>
</template>

<style scoped>
.item-title-font {
  font-size: 13px !important;
}
</style>
