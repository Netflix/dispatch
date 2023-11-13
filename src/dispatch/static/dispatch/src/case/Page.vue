<template>
  <case-attributes-drawer v-model="caseDetails" />
  <v-row align="center" justify="space-between" no-gutters>
    <v-col>
      <v-breadcrumbs :items="breadcrumbItems"></v-breadcrumbs>
    </v-col>
    <v-col class="text-right">
      <case-status-toggle v-model="caseDetails.status" />
    </v-col>
  </v-row>
  <v-row class="pl-6 pr-6" no-gutters>
    <v-col>
      <editable-text-area v-model="caseDetails.title" :loading="loading" label="Title" />
    </v-col>
  </v-row>
  <v-row class="pl-6 pr-6" no-gutters>
    <v-col>
      <editable-text-area
        v-model="caseDetails.description"
        :loading="loading"
        label="Description"
      />
    </v-col>
  </v-row>
  <v-row class="pl-6 pr-6" no-gutters>
    <v-col>
      <editable-text-area v-model="caseDetails.resolution" :loading="loading" label="Resolution" />
    </v-col>
    <v-col cols="3">
      <v-skeleton-loader v-if="loading" type="text"></v-skeleton-loader>
      <v-select
        v-else
        variant="underlined"
        density="compact"
        v-model="caseDetails.resolution_reason"
      >
      </v-select>
    </v-col>
  </v-row>
  <v-row no-gutters>
    <case-tabs :loading="loading" v-model="caseDetails" />
  </v-row>
</template>

<script>
import { computed, ref, watchEffect, onMounted, reactive } from "vue"
import { useRoute } from "vue-router"

import CaseApi from "@/case/api"
import CaseAttributesDrawer from "@/case/CaseAttributesDrawer.vue"
import CaseStatus from "@/case/CaseStatus.vue"
import CaseStatusToggle from "@/case/CaseStatusToggle.vue"
import CaseTabs from "@/case/CaseTabs.vue"
import EditableTextArea from "@/components/EditableTextArea.vue"

export default {
  name: "CasePage",
  components: {
    CaseAttributesDrawer,
    CaseStatusToggle,
    CaseTabs,
    CaseStatus,
    EditableTextArea,
  },
  setup(props, { root }) {
    const route = useRoute()

    const caseDefaults = {
      status: "New",
      assignee: null,
      case_priority: null,
      case_severity: null,
      case_type: null,
      closed_at: null,
      description: "",
      documents: [],
      duplicates: [],
      escalated_at: null,
      participants: [],
      events: [],
      groups: [],
      id: null,
      incidents: [],
      name: null,
      project: null,
      related: [],
      reporter: null,
      reported_at: null,
      resolution_reason: "",
      resolution: "",
      title: "",
      signal_instances: [],
      storage: null,
      tags: [],
      ticket: null,
      triage_at: null,
      visibility: "",
      conversation: null,
      workflow_instances: null,
    }

    const caseDetails = ref(caseDefaults)
    const loading = ref(false)

    const fetchDetails = async () => {
      const caseName = route.params.name
      loading.value = true
      try {
        CaseApi.getAll({
          filter: JSON.stringify([
            { and: [{ model: "Case", field: "name", op: "==", value: caseName }] },
          ]),
        }).then((response) => {
          if (response.data.items.length) {
            // get the full data set
            CaseApi.get(response.data.items[0].id).then((response) => {
              caseDetails.value = response.data
              loading.value = false
            })
          }
        })
      } catch (e) {
        console.error("Failed to fetch case details", e)
        caseDetails.value = {}
        loading.value = false
      }
    }

    onMounted(fetchDetails)

    watchEffect(() => {
      route.params.name
      fetchDetails()
    })

    const breadcrumbItems = computed(() => {
      let items = [
        {
          title: "Cases",
          disabled: false,
          href: `/${route.params.organization}/cases`,
        },
        {
          title: caseDetails.value.name,
          disabled: true,
        },
      ]
      return items
    })

    return {
      breadcrumbItems,
      loading,
      caseDetails,
    }
  },
}
</script>
