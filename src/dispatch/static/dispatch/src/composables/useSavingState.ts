import { computed, ComputedRef } from "vue"
import { useStore } from "vuex"
import { Store } from "vuex"
import { CaseState } from "@/store/case"

interface UseSavingStateReturns {
  saving: ComputedRef<boolean>
  // eslint-disable-next-line no-unused-vars
  setSaving: (value: boolean) => void
}

export function useSavingState(): UseSavingStateReturns {
  const store = useStore<Store<{ case: CaseState }>>()

  const saving = computed(() => store.state.case_management.selected.saving)

  const setSaving = (value: boolean) => {
    store.commit("case_management/SET_SELECTED_SAVING", value)
  }

  return {
    saving,
    setSaving,
  }
}
