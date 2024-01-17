<template>
  <v-card class="grow">
    <v-card-title>
      <v-row>
        <v-col>
          {{ label }}
          <v-tooltip location="bottom">
            <template #activator="{ props: activatorProps }">
              <v-btn icon variant="text" color="info" v-bind="activatorProps" @click="add()">
                <v-icon>mdi-playlist-plus</v-icon>
              </v-btn>
            </template>
            <span>Create {{ label }} Policy</span>
          </v-tooltip>
        </v-col>
        <v-col cols="1" align="end">
          <v-tooltip location="bottom">
            <template #activator="{ props: activatorProps }">
              <v-btn
                icon
                variant="text"
                color="info"
                v-bind="activatorProps"
                :loading="loading"
                @click="save()"
              >
                <v-icon>mdi-content-save-outline</v-icon>
              </v-btn>
            </template>
            <span>Save {{ label }} Policies</span>
          </v-tooltip>
        </v-col>
      </v-row>
    </v-card-title>
    <v-card-text>
      <template v-if="!policies.length">
        <v-row justify="center"> No {{ label }} policies have been defined. </v-row>
      </template>
      <v-expansion-panels ref="sortableElement">
        <v-expansion-panel v-for="(policy, idx) in policies" :key="policy.id">
          <v-expansion-panel-title>
            <v-row align="center" justify="center">
              <v-col cols="1">
                <v-icon>mdi-drag-horizontal-variant</v-icon>
              </v-col>
              <v-col cols="1">
                <v-chip v-if="policy.enabled" color="green" size="small" label> Enabled </v-chip>
                <v-chip v-if="!policy.enabled" size="small" label>Disabled</v-chip>
              </v-col>
              <v-col>
                {{ policy.role }} - <span v-if="policy.service">{{ policy.service.name }}</span>
              </v-col>
            </v-row>
          </v-expansion-panel-title>
          <v-expansion-panel-text>
            <v-list density="compact">
              <v-list-item>
                <tag-filter-auto-complete
                  label="Tags"
                  :project="project"
                  v-model="policy.tags"
                  model="incident"
                />
              </v-list-item>
              <v-list-item>
                <incident-priority-combobox
                  :project="project"
                  v-model="policy.incident_priorities"
                />
              </v-list-item>
              <v-list-item>
                <incident-type-combobox :project="project" v-model="policy.incident_types" />
              </v-list-item>
              <v-list-item>
                <service-select-new
                  label="Oncall Service"
                  :project="project"
                  v-model="policy.service"
                />
              </v-list-item>
              <v-list-item>
                <v-checkbox
                  v-if="label === 'Incident Commander'"
                  v-model="policy.engage_next_oncall"
                  label="Add next on-call as an Observer"
                  hint="Check this if you would like the next oncall incident commander to be added as an observer."
                />
              </v-list-item>
              <v-list-item>
                <v-checkbox
                  style="margin-top: -18px"
                  v-model="policy.enabled"
                  label="Enabled"
                  hint="Check this if you would like this policy to be considered when resolving the role."
                />
              </v-list-item>
              <v-list-item>
                <v-btn color="primary" @click="remove(idx)"> Delete Policy </v-btn>
              </v-list-item>
            </v-list>
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, computed, watch } from "vue"
import { useSortable } from "@vueuse/integrations/useSortable"

import IncidentPriorityCombobox from "@/incident/priority/IncidentPriorityCombobox.vue"
import IncidentRoleApi from "@/incident_role/api"
import IncidentTypeCombobox from "@/incident/type/IncidentTypeCombobox.vue"
import ServiceSelectNew from "@/service/ServiceSelectNew.vue"
import TagFilterAutoComplete from "@/tag/TagPicker.vue"

const props = defineProps({
  label: {
    type: String,
    default: null,
  },
  project: {
    type: [Object],
    default: null,
  },
})

const loading = ref(false)
const sortableElement = ref()

const _policies = ref([])
const policies = computed({
  get() {
    return _policies.value
  },
  set(val) {
    _policies.value = val.map((policy, idx) => ({
      ...policy,
      order: idx + 1,
    }))
  },
})

useSortable(
  computed(() => sortableElement.value?.$el),
  policies
)

watch(
  () => props.project,
  () => {
    IncidentRoleApi.getRolePolicies(props.label, props.project.name).then((response) => {
      policies.value = response.data.policies
    })
  },
  { immediate: true }
)

function add() {
  policies.value.push({
    role: props.label,
    project: props.project,
    enabled: false,
    engage_next_oncall: false,
    service: null,
    incident_priorities: [],
    incident_types: [],
    tags: [],
  })
}
function remove(idx) {
  policies.value.splice(idx, 1)
}
function save() {
  loading.value = true
  IncidentRoleApi.updateRole(props.label, props.project.name, { policies: policies.value })
    .then((response) => {
      this.$store.commit(
        "notification_backend/addBeNotification",
        { text: "Role policies successfully updated.", type: "success" },
        { root: true }
      )
      policies.value = response.data.policies
    })
    .finally(() => {
      loading.value = false
    })
}
</script>
