<template>
  <v-container class="pa-0" fluid>
    <v-row no-gutters>
      <v-col>
        <v-card flat>
          <v-card-text class="pa-4">
            <div v-if="loading" class="text-center">
              <v-progress-circular indeterminate color="primary" />
              <div class="mt-2">Loading notes...</div>
            </div>
            <div v-else>
              <div class="d-flex justify-space-between align-center mb-4">
                <h3 class="text-h6">Investigation Notes</h3>
                <div class="text-caption text-disabled">
                  <span v-if="notes?.last_updated_by">
                    Last updated {{ formatDate(notes.updated_at) }} by
                    {{ notes.last_updated_by.name }}
                  </span>
                </div>
              </div>

              <RichEditor
                v-model="notesContent"
                :placeholder="'Add investigation notes, findings, and action items...'"
                :disabled="!canEdit"
                @update:model-value="debouncedSave"
                class="notes-editor"
              />
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { computed, ref, watch } from "vue"
import { useStore } from "vuex"
import { debounce } from "lodash"
import { useSavingState } from "@/composables/useSavingState"
import { formatRelativeDate } from "@/filters"

import RichEditor from "@/components/RichEditor.vue"
import CaseApi from "@/case/api"

export default {
  name: "NotesTab",
  components: {
    RichEditor,
  },
  setup() {
    const store = useStore()
    const { setSaving } = useSavingState()

    // Reactive data
    const loading = ref(false)
    const notesContent = ref("")

    // Computed values
    const selected = computed(() => store.state.case_management.selected)
    const notes = computed(() => selected.value?.case_notes)
    const canEdit = computed(() => {
      // Add your permission logic here
      return true // For now, allow all users to edit
    })

    // Watchers
    watch(
      () => selected.value?.case_notes,
      (newNotes) => {
        if (newNotes) {
          notesContent.value = newNotes.content || ""
        } else {
          notesContent.value = ""
        }
      },
      { immediate: true }
    )

    // Methods
    const saveNotes = async () => {
      if (!selected.value) return

      try {
        setSaving(true)

        const updatedCase = {
          ...selected.value,
          case_notes: {
            content: notesContent.value,
          },
        }

        const response = await CaseApi.update(selected.value.id, updatedCase)

        // Update the store with the response data
        store.commit("case_management/SET_SELECTED", response.data)
      } catch (error) {
        console.error("Failed to save notes:", error)
        store.dispatch("notification_backend/createNotification", {
          text: "Failed to save notes. Please try again.",
          type: "error",
        })
      } finally {
        setSaving(false)
      }
    }

    const debouncedSave = debounce(saveNotes, 1000)

    const formatDate = (date) => {
      if (!date) return ""
      return formatRelativeDate(date)
    }

    return {
      loading,
      notesContent,
      notes,
      canEdit,
      debouncedSave,
      formatDate,
    }
  },
}
</script>

<style scoped>
.notes-editor {
  min-height: 400px;
}

.notes-editor :deep(.ProseMirror) {
  min-height: 350px;
  padding: 16px;
  border: 1px solid rgba(0, 0, 0, 0.12);
  border-radius: 4px;
}

.notes-editor :deep(.ProseMirror:focus) {
  outline: 2px solid rgb(var(--v-theme-primary));
  outline-offset: -2px;
}

.notes-editor :deep(.ProseMirror p.is-editor-empty:first-child::before) {
  color: rgba(0, 0, 0, 0.38);
  content: attr(data-placeholder);
  float: left;
  height: 0;
  pointer-events: none;
}
</style>
