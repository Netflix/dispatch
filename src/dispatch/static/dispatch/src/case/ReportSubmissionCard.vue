<template>
  <v-form ref="form" @submit.prevent>
    <v-card
      class="mx-auto ma-4"
      max-width="600"
      variant="outlined"
      title="          Open a Case"
      :loading="loading"
    >
      <template #append>
        <v-tooltip location="bottom">
          <template #activator="{ props }">
            <v-btn icon variant="text" v-bind="props" @click="copyView">
              <v-icon>mdi-content-copy</v-icon>
            </v-btn>
          </template>
          <span>Copy current fields as template.</span>
        </v-tooltip>
      </template>
      <v-card-text>
        <p>
          Cases are meant to triage events that do not raise to the level of incidents, but can be
          escalated to incidents if necessary. If you suspect a security issue and need help, please
          fill out this form to the best of your abilities.
        </p>
        <p v-if="project_faq">
          If you have additional questions, such as whether to open a case or report an incident,
          please check out the following FAQ document:
          <a :href="project_faq.weblink" target="_blank" style="text-decoration: none">
            {{ project_faq.name }}
            <v-icon size="small">mdi-open-in-new</v-icon>
          </a>
        </p>
        <v-container>
          <v-row>
            <v-col cols="12">
              <v-textarea
                v-model="title"
                label="Title"
                hint="A brief explanatory title. You can change this later."
                clearable
                auto-grow
                rows="2"
                required
                name="Title"
                :rules="[rules.required]"
              />
            </v-col>
            <v-col cols="12">
              <v-textarea
                v-model="description"
                label="Description"
                hint="A summary of what you know so far. It's all right if this is incomplete."
                clearable
                auto-grow
                rows="3"
                required
                name="Description"
                :rules="[rules.required]"
              />
            </v-col>
            <v-col cols="12">
              <project-select v-model="project" excludeDisabled />
            </v-col>
            <v-col cols="12">
              <case-type-select :project="project" v-model="case_type" />
            </v-col>
            <v-col cols="12">
              <case-priority-select :project="project" v-model="case_priority" />
            </v-col>
          </v-row>
        </v-container>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
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

import router from "@/router"
import CaseTypeSelect from "@/case/type/CaseTypeSelect.vue"
import CasePrioritySelect from "@/case/priority/CasePrioritySelect.vue"
import ProjectSelect from "@/project/ProjectSelect.vue"
import DocumentApi from "@/document/api"
import ProjectApi from "@/project/api"
import AuthApi from "@/auth/api"
import SearchUtils from "@/search/utils"
import CaseTypeApi from "@/case/type/api"

export default {
  setup() {
    return {
      rules: { required },
    }
  },
  name: "ReportSubmissionCard",

  components: {
    CaseTypeSelect,
    CasePrioritySelect,
    ProjectSelect,
  },

  data() {
    return {
      isSubmitted: false,
      project_faq: null,
      formIsValid: false,
      titleValid: false,
      descriptionValid: false,
      projectValid: false,
      caseTypeValid: false,
      casePriorityValid: false,
    }
  },

  computed: {
    ...mapFields("case_management", [
      "selected.case_priority",
      "selected.case_type",
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
  },

  methods: {
    getFAQ() {
      if (this.project) {
        DocumentApi.getAll({
          filter: JSON.stringify({
            and: [
              {
                field: "resource_type",
                op: "==",
                value: "dispatch-faq-reference-document",
              },
              {
                model: "Project",
                field: "name",
                op: "==",
                value: this.project.name,
              },
            ],
          }),
        }).then((response) => {
          if (response.data.items.length) {
            this.project_faq = response.data.items[0]
          }
        })
      }
    },
    copyView: function () {
      let store = this.$store
      navigator.clipboard.writeText(window.location).then(
        function () {
          store.commit(
            "notification_backend/addBeNotification",
            {
              text: "View copied to clipboard.",
            },
            { root: true }
          )
        },
        function () {
          store.commit(
            "notification_backend/addBeNotification",
            {
              text: "Failed to copy view to clipboard.",
              color: "red",
            },
            { root: true }
          )
        }
      )
    },
    checkFormValidity() {
      this.formIsValid = this.titleValid && this.descriptionValid
    },
    ...mapActions("case_management", ["report", "get", "resetSelected"]),
  },

  created() {
    if (this.$route.query.project) {
      let params = {
        filter: { field: "name", op: "==", value: this.$route.query.project },
      }
      // get full project object from api
      ProjectApi.getAll(params).then((response) => {
        if (response.data.items.length && !this.project) {
          this.project = response.data.items[0]
        }
      })
    } else if (this.projects.length && !this.project) {
      this.project = this.projects[0].project
    } else {
      // if no user projects stored yet, get the default project for the user
      // if no default user project, then get the default project for the organization
      AuthApi.getUserInfo().then((response) => {
        if (this.project) {
          // if the user has already selected something, exit
          return
        }
        let default_user_project = response.data.projects.filter((v) => v.default === true)
        if (default_user_project.length) {
          this.project = default_user_project[0].project
        } else if (this.default_project) {
          this.project = this.default_project
        } else {
          let default_params = {
            filter: { field: "default", op: "==", value: true },
          }
          ProjectApi.getAll(default_params).then((response) => {
            if (response.data.items.length && !this.project) {
              this.project = response.data.items[0]
            }
          })
        }
      })
    }

    if (this.$route.query.case_type) {
      let filterOptions = {
        q: "",
        sortBy: ["name"],
        descending: [false],
        itemsPerPage: this.numItems,
      }

      if (this.project) {
        filterOptions = {
          filters: {
            project: [this.project],
            name: [this.$route.query.case_type],
            enabled: ["true"],
          },
          ...filterOptions,
        }
      }

      filterOptions = SearchUtils.createParametersFromTableOptions({ ...filterOptions })
      CaseTypeApi.getAll(filterOptions).then((response) => {
        if (response.data.items.length > 0) {
          this.case_type = response.data.items[0]
        } else {
          this.case_type = this.$route.query.case_type
        }
      })
    }

    if (this.$route.query.case_priority) {
      this.case_priority = { name: this.$route.query.case_priority }
    }

    this.getFAQ()
    this.$watch(
      (vm) => [vm.project],
      () => {
        this.getFAQ()
      }
    )

    this.$watch(
      (vm) => [vm.project, vm.case_priority, vm.case_type],
      () => {
        var queryParams = {
          project: this.project ? this.project.name : null,
          case_priority: this.case_priority ? this.case_priority.name : null,
          case_type: this.case_type ? this.case_type.name : null,
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
