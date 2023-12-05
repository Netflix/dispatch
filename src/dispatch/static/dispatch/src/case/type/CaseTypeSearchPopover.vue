<script setup lang="ts">
import { watch, ref } from "vue"
import CaseTypeApi from "@/case/type/api"
import CaseApi from "@/case/api"
import SearchPopover from "@/components/SearchPopover.vue"
import { useSavingState } from "@/composables/useSavingState"
import type { Ref } from "vue"
import { useStore } from "vuex"

type CaseType = {
  name: string
}

const props = defineProps<{ caseType: string; project: string }>()

const store = useStore()
const { setSaving } = useSavingState()
const caseTypes: Ref<CaseType[]> = ref([])
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

        const response = await CaseTypeApi.getAll(options)
        caseTypes.value = response.data.items.map((item: any) => item.name)
      } catch (error) {
        console.error("Error fetching priorities:", error)
      }
    }
  },
  { immediate: true }
)

const selectCaseType = async (caseTypeName: string) => {
  // Fetch the participant object from the API
  const response = await CaseTypeApi.getAll({
    filter: JSON.stringify([
      { and: [{ model: "CaseType", field: "name", op: "==", value: caseTypeName }] },
    ]),
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
