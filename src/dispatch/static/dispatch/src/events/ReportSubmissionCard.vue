<template>
  <v-form ref="form" @submit.prevent>
    <v-card
      class="mx-auto ma-4"
      max-width="600"
      variant="outlined"
      title="          Report a Security Event"
      :loading="loading"
    >
      <v-card-text>
        <p>
          Security Events are an input requiring triage and if deemed significant, can be escalated
          to incidents for futher investigation and response. If you suspect a security issue and
          need help, please fill out this form to the best of your abilities.
        </p>
        <v-container>
          <v-row>
            <v-col cols="12">
              <v-textarea
                v-model="description"
                label="Description"
                hint="A summary of what you know so far. It's all right if this is incomplete."
                clearable
                auto-grow
                rows="6"
                required
                name="Description"
                :rules="[rules.required]"
              />
            </v-col>
            <v-checkbox
              v-model="page_oncall"
              label="URGENT: I need immediate help with this (the oncall will be paged)"
              @update:model-value="updateCasePriority"
              hint="Urgent SLA: 15 minutes (24x7)<br>Default SLA: 2 hours (9am-5pm Pacific)"
              :persistent-hint="true"
            >
              <template #message="{ message, key }">
                <div v-html="message" :key="key" />
              </template>
            </v-checkbox>
          </v-row>
        </v-container>
      </v-card-text>
      <v-card-actions>
        <v-btn
          color="info"
          variant="flat"
          block
          :loading="loading"
          :disabled="!formIsValid"
          @click="report()"
        >
          Submit
          <template #loader>
            <v-progress-linear indeterminate color="white" />
          </template>
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-form>
</template>

<script>
import { required } from "@/util/form"
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import { resolveProject } from "@/util/project"

import router from "@/router"
import CasePrioritySelect from "@/case/priority/CasePrioritySelect.vue"
import CaseTypeApi from "@/case/type/api"
import CasePriorityApi from "@/case/priority/api"
import CaseSeverityApi from "@/case/severity/api"

export default {
  setup() {
    return {
      rules: { required },
    }
  },
  name: "ReportSubmissionCard",

  data() {
    return {
      isSubmitted: false,
      formIsValid: false,
      titleValid: false,
      descriptionValid: false,
      projectValid: false,
      page_oncall: false,
      items: [],
    }
  },

  computed: {
    ...mapFields("case_management", [
      "selected.dedicated_channel",
      "selected.title",
      "selected.tags",
      "selected.description",
      "selected.visibility",
      "selected.storage",
      "selected.documents",
      "selected.loading",
      "selected.ticket",
      "selected.project",
      "selected.id",
      "selected.case_priority",
      "selected.case_type",
      "selected.case_severity",
      "selected.event",
      "default_project",
    ]),
    ...mapFields("auth", ["currentUser.projects"]),
  },

  watch: {
    title() {
      this.titleValid = !!this.title
      this.checkFormValidity()
    },
    description() {
      this.descriptionValid = !!this.description
      this.checkFormValidity()
    },
    project() {
      this.projectValid = !!this.project
      this.checkFormValidity()
    },
  },

  methods: {
    ...CasePrioritySelect.methods,
    updateCasePriority(urgent) {
      if (urgent) {
        const page_assignee = this.items.find((p) => p.page_assignee === true)
        this.case_priority = { id: page_assignee.id, name: page_assignee.name }
      } else {
        // fall back on default priority configured for project
        this.case_priority = null
      }
    },
    checkFormValidity() {
      this.formIsValid = this.titleValid && this.descriptionValid && this.projectValid
    },

    loadDefaults(project) {
      // Load default case type for the project
      CaseTypeApi.getAll({
        filter: JSON.stringify({
          and: [
            {
              model: "Project",
              field: "id",
              op: "==",
              value: project.id,
            },
            {
              field: "default",
              op: "==",
              value: true,
            },
          ],
        }),
      }).then((response) => {
        if (response.data.items.length) {
          this.case_type = response.data.items[0]
        }
      })

      // Load default case severity for the project
      CaseSeverityApi.getAll({
        filter: JSON.stringify({
          and: [
            {
              model: "Project",
              field: "id",
              op: "==",
              value: project.id,
            },
            {
              field: "default",
              op: "==",
              value: true,
            },
          ],
        }),
      }).then((response) => {
        if (response.data.items.length) {
          this.case_severity = response.data.items[0]
        }
      })

      // Load default case priority for the project
      CasePriorityApi.getAll({
        filter: JSON.stringify({
          and: [
            {
              model: "Project",
              field: "id",
              op: "==",
              value: project.id,
            },
            {
              field: "default",
              op: "==",
              value: true,
            },
          ],
        }),
      }).then((response) => {
        if (response.data.items.length) {
          this.case_priority = response.data.items[0]
        }
      })

      // Set other defaults
      this.visibility = "Open"
    },

    fetchData() {
      // If project is not available yet, we'll load priorities later in onProjectResolved
      if (!this.project) {
        return
      }

      // Load case priority items for the urgent checkbox
      CasePriorityApi.getAll({
        filter: JSON.stringify({
          and: [
            {
              model: "Project",
              field: "id",
              op: "==",
              value: this.project.id,
            },
          ],
        }),
      }).then((response) => {
        this.items = response.data.items
      })
    },

    ...mapActions("case_management", ["report", "get", "resetSelected"]),
  },

  created() {
    this.event = true
    this.dedicated_channel = true

    // Use the utility function to resolve the project
    resolveProject({
      component: this,
      onProjectResolved: (project) => {
        // Project has been resolved and set
        this.projectValid = !!this.project
        this.checkFormValidity()

        // Auto-populate defaults based on the project
        this.loadDefaults(project)

        // Fetch case priority items now that we have a project
        this.fetchData()
      },
    })

    if (this.$route.query.title) {
      this.title = this.$route.query.title
    } else {
      this.title = "Security Event Triage"
    }

    if (this.$route.query.description) {
      this.description = this.$route.query.description
    }

    // We'll call fetchData after project is resolved

    this.$watch(
      (vm) => [vm.project, vm.title, vm.description],
      () => {
        var queryParams = {
          project: this.project ? this.project.name : null,
          title: this.title,
          description: this.description,
        }
        Object.keys(queryParams).forEach((key) => (queryParams[key] ? {} : delete queryParams[key]))
        router.replace({
          query: queryParams,
        })
      }
    )
  },
}
</script>
