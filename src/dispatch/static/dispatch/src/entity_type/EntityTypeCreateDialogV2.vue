<template>
  <v-dialog
    :model-value="props.dialog"
    @update:model-value="$emit('update:dialog', $event)"
    width="1000"
    persistent
  >
    <template #default="{ isActive }">
      <v-card v-if="isActive" height="700px" class="flex-container hov-card" color="#fafafa">
        <v-card-title class="mb-n6 font-weight-regular d-flex align-center">
          <div class="d-flex align-center">
            <v-btn class="dispatch-button" variant="text" :ripple="false" disabled>
              {{ projectName }}
            </v-btn>
            <span class="pl-2 text-body-2">› New entity type</span>
          </div>
          <v-spacer />
          <v-btn icon="mdi-close" variant="plain" @click="closeDialog" />
        </v-card-title>

        <v-card-text>
          <v-form v-model="formValid">
            <v-text-field
              v-model="name"
              color="secondary-lighten-4"
              class="large-font-field"
              placeholder="Name"
              density="compact"
              variant="plain"
              validate-on="blur"
              :rules="[rules.required, rules.counter, rules.uniqueName]"
            />
          </v-form>

          <RichEditor v-model="description" placeholder="Add description..." class="pt-2" />
          <v-text-field
            v-model="newEntityTypeJpath"
            @update:model-value="(newJpath) => updateDecorations(newJpath)"
            bg-color="white"
            color="grey-lighten-2"
            base-color="grey-lighten-1"
            class="pt-8 code-font-field"
            density="compact"
            variant="outlined"
            append-inner-icon="mdi-code-json"
          />
        </v-card-text>
        <v-fade-transition>
          <div v-if="jpathInUse" class="pl-7 mt-n6 pb-6 text-caption" style="color: grey">
            <v-icon size="x-small" color="red-darken-2" icon="mdi-alert-circle-outline" />
            This pattern is already in use by the entity type "<b>{{ jpathInUse.name }}</b
            >".
          </div>
        </v-fade-transition>
        <VDivider />

        <div class="flex-item">
          <MonacoEditor
            :modelValue="editorValue"
            :options="editorOptions"
            :editorMounted="editorMounted"
            language="json"
            style="width: 100%; height: 100%"
          />
        </div>

        <VDivider />

        <v-card-actions class="mr-2 d-flex justify-space-between">
          <DTooltip text="View entity type documentation" hotkeys="">
            <template #activator="{ tooltip }">
              <v-btn
                v-bind="tooltip"
                icon="mdi-information-outline"
                variant="plain"
                target="_blank"
                size="small"
                href="https://netflix.github.io/dispatch/docs/administration/settings/signal/entity-type"
              />
            </template>
          </DTooltip>

          <v-spacer />
          <div class="d-flex align-center">
            <v-switch
              v-model="createMore"
              hide-details
              inset
              density="compact"
              class="small-switch"
              color="rgb(109, 119, 212)"
            />
            <span class="pr-4 ml-n2 text-caption">Create more</span>
            <v-btn class="create-entity-button" @click="saveEntityType"> Create Entity Type </v-btn>
          </div>
        </v-card-actions>
      </v-card>
    </template>
  </v-dialog>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, watch, watchEffect } from "vue"
import { useStore } from "vuex"

import { findPositions } from "@/util/jpath"
import DTooltip from "@/components/DTooltip.vue"
import EntityTypeApi from "@/entity_type/api"
import SignalApi from "@/signal/api"
import MonacoEditor from "@/components/MonacoEditor.vue"
import RichEditor from "@/components/RichEditor.vue"

const props = defineProps({
  dialog: {
    type: Boolean,
    default: false,
  },
  newEntityTypeJpath: {
    type: String,
    default: "",
  },
  editorValue: {
    type: String,
    default: "",
  },
  signalId: {
    type: Number,
    default: 0,
  },
  signalObj: {
    type: Object as () => Record<string, any>,
    default: () => ({}),
  },
})

watchEffect(() => {
  if (props.dialog) {
    console.log("props.dialog is now true")
  }
})

console.log(props.signalObj)

const store = useStore()
const selectedCase = computed(() => store.state.case_management.selected)
console.log(selectedCase)
const createMore = ref(false)
let projectName = ref(selectedCase.value?.project?.name)

let name = ref("")
let description = ref("")
let newEntityTypeJpath = ref(props.newEntityTypeJpath)
watch(
  () => props.newEntityTypeJpath,
  (newJpath) => {
    newEntityTypeJpath.value = newJpath
  }
)

let jpath = ref(props.newEntityTypeJpath)
let signalId = ref(props.signalId)
let jpathInUse = ref(false)
let entityTypes = ref([])
let formValid = ref(false)

// Function to find an entity with a matching jpath
const findEntityByJpath = (jpath) => {
  // Attempt to find an entity in the list of entity types
  const matchingEntity = entityTypes.value.find((entity) => entity.jpath === jpath)
  return matchingEntity
}

const rules = {
  required: (value) => !!value || "Required.",
  counter: (value) => value.length >= 3 || "Name must be at least 3 characters.",
  uniqueName: (value: string) => {
    // Check if the name already exists in the list of entity types
    const exists = entityTypes.value.some(
      (entity) => entity.name.toLowerCase() === value.toLowerCase()
    )
    return !exists || "Name already taken."
  },
}

watch(
  () => props.dialog, // Watch the 'dialog' prop
  (isDialogOpen) => {
    // If the dialog is not open or there are no entity types defined, reset 'jpathInUse' and log a message
    if (!isDialogOpen || entityTypes.value.length === 0) {
      jpathInUse.value = false
      console.log(
        "The dialog is closed or no entity types are defined, resetting 'jpathInUse' to",
        jpathInUse.value
      )
      return
    }

    // Try to find a matching entity by jpath
    const matchingEntity = findEntityByJpath(props.newEntityTypeJpath)

    // If a matching entity is found, update the 'jpathInUse' ref and log a message
    if (matchingEntity) {
      jpathInUse.value = matchingEntity
      console.log(
        `The jpath is already in use by entity ${matchingEntity.name} for pattern`,
        props.newEntityTypeJpath
      )
      return
    }

    // If no matching entity is found, indicate that the jpath is not in use and log a message
    jpathInUse.value = false
    console.log("The jpath is not in use for pattern", props.newEntityTypeJpath)
  },
  { immediate: true } // Run the watcher immediately
)

const emit = defineEmits(["update:dialog", "new-entity-type"])

function closeDialog() {
  jpath.value = ""
  name.value = ""
  newEntityTypeJpath.value = props.newEntityTypeJpath // Add this line
  jpathInUse.value = false
  emit("update:dialog", false)
}

let editorInstance
let monacoInstance
let decorationIds = []

const updateDecorations = (newJpath = props.newEntityTypeJpath) => {
  if (!editorInstance || !monacoInstance) return
  const jsonString = editorInstance.getValue()
  const jpath = newJpath
  const positions = findPositions(jsonString, jpath)

  const newDecorations = positions.map((position) => {
    const start = editorInstance.getModel().getPositionAt(position.start)
    const end = editorInstance.getModel().getPositionAt(position.end)
    return {
      range: new monacoInstance.Range(start.lineNumber, start.column, end.lineNumber, end.column),
      options: {
        isWholeLine: false,
        className: "decorate",
      },
    }
  })

  // replace old decorations with new ones
  decorationIds = editorInstance.deltaDecorations(decorationIds, newDecorations)
}

const editorMounted = (editor, monaco) => {
  editorInstance = editor
  monacoInstance = monaco

  try {
    updateDecorations()
  } catch (error) {
    console.error("Error updating decorations:", error)
  }

  // Set the initial view position to the decoration match
  // This ensures the decorated text is always in view on mount and not hidden

  // Get position of first decoration
  const firstDecoration = editorInstance.getModel().getDecorationRange(decorationIds[0])
  if (firstDecoration) {
    // Reveal the first decoration in center
    editor.revealPositionInCenter(firstDecoration.getStartPosition())
  }

  editor.onDidChangeModelContent(() => {
    try {
      updateDecorations()
    } catch (error) {
      console.error("Error updating decorations:", error)
    }
  })
}

const editorOptions = {
  automaticLayout: true,
  renderValidationDecorations: "on",
  renderLineHighlight: "none",
  lineDecorationsWidth: 0,
  overviewRulerLanes: 0,
  scrollBeyondLastLine: false,
  hideCursorInOverviewRuler: true,
  readOnly: true,
  wordWrap: true,
  glyphMargin: true,
  contextmenu: false,
  scrollbar: {
    vertical: "hidden",
  },
  minimap: {
    enabled: false,
  },
}

const saveEntityType = async () => {
  if (!formValid.value) {
    const errors = [rules.required, rules.counter, rules.uniqueName]
      .map((rule) => rule(name.value))
      .filter((msg) => typeof msg === "string")

    store.commit(
      "notification_backend/addBeNotification",
      {
        text: `Form Invalid: ${errors}`,
        type: "exception",
      },
      { root: true }
    )
    return
  }

  const signalGetResponse = await SignalApi.get(signalId.value)

  const entityTypeData = {
    name: name.value,
    description: description.value,
    enabled: true,
    jpath: newEntityTypeJpath.value,
    scope: "multiple",
    project: selectedCase.value.project,
    regular_expression: null,
    signals: [signalGetResponse.data],
  }
  try {
    const newEntityType = await EntityTypeApi.create(entityTypeData)
    emit("new-entity-type", newEntityType.data)
    store.commit(
      "notification_backend/addBeNotification",
      {
        text: "Entity Type created and associated with signal successfully.",
        type: "success",
      },
      { root: true }
    )
    await EntityTypeApi.recalculate(newEntityType.data.id, props.signalObj.raw.id)
  } catch (error) {
    store.commit(
      "notification_backend/addBeNotification",
      {
        text: `Failed to create Entity Type: ${error.message}`,
        type: "error",
      },
      { root: true }
    )
    console.error(error)
  }
  closeDialog()
}

// Function to get all entity types
const getAllEntityTypes = async () => {
  try {
    const options = {
      itemsPerPage: -1,
    }

    const response = await EntityTypeApi.getAll(options)
    entityTypes.value = response.data.items
  } catch (error) {
    console.error("Error fetching entity types:", error)
  }
}

onMounted(async () => {
  await getAllEntityTypes()
})
</script>

<style lang="scss" scoped>
.v-dialog > .v-overlay__content > .v-card,
.v-dialog > .v-overlay__content > .v-sheet,
.v-dialog > .v-overlay__content > form > .v-card,
.v-dialog > .v-overlay__content > form > .v-sheet {
  --v-scrollbar-offset: 0px;
  border-radius: 4px;
  overflow-y: auto;
  box-shadow: rgba(0, 0, 0, 0.5) 0px 16px 70px !important;
}

.small-switch {
  transform: scale(0.5);
}

.code-font-field :deep(input) {
  font-family: sfmono-regular, consolas, menlo, dejavu sans mono, monospace !important;
  font-size: 0.8571428571em !important;
}

.v-btn.dispatch-button.v-btn--disabled {
  opacity: 1 !important;
  color: your-color !important;
}

.large-font-field :deep(input) {
  font-size: 1.125rem !important;
}

.flex-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.flex-item {
  flex-grow: 1;
  overflow: auto;
}

.hov-card {
  border-radius: 8px !important;
  box-shadow: rgba(0, 0, 0, 0.5) 0px 16px 70px !important;
}

.create-entity-button {
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  white-space: nowrap !important;
  flex-shrink: 0 !important;
  margin: 0px !important;
  border-radius: 4px !important;
  font-weight: 500 !important;
  line-height: normal !important;

  transition-property: border, background-color, color, opacity !important;
  transition-duration: 0, 15s !important;
  user-select: none !important;
  position: relative !important;
  border: 1px solid rgb(109, 119, 212) !important;
  box-shadow: rgba(0, 0, 0, 0.086) 0px 1px 2px !important;
  background-color: rgb(109, 119, 212) !important;
  color: rgb(254, 254, 255) !important;
  min-width: 28px !important;
  height: 28px !important;
  padding: 0px 14px !important;
  font-size: 0.75rem !important;
  text-transform: none !important;
  letter-spacing: normal !important;
}
</style>
