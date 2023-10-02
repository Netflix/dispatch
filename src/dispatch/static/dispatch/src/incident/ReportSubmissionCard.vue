<template>
  <v-form @submit.prevent="report()" v-slot="{ isValid }">
    <v-card class="mx-auto ma-4" max-width="600" flat variant="outlined" :loading="loading">
      <v-card-text>
        <p class="text-h4 text--primary">
          Report Incident
          <v-tooltip location="bottom">
            <template #activator="{ props }">
              <v-btn icon variant="text" v-bind="props" @click="copyView">
                <v-icon>mdi-content-copy</v-icon>
              </v-btn>
            </template>
            <span>Copy current fields as template.</span>
          </v-tooltip>
        </p>
        <p>
          If you suspect an incident and need help, please fill out this form to the best of your
          abilities.
        </p>
        <p v-if="project_faq">
          If you have additional questions, please check out the following FAQ document:
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
              <project-select v-model="project" />
            </v-col>
            <v-col cols="12">
              <incident-type-select :project="project" v-model="incident_type" />
            </v-col>
            <v-col cols="12">
              <incident-priority-select :project="project" v-model="incident_priority" />
            </v-col>
            <v-col cols="12">
              <tag-filter-auto-complete :project="project" v-model="tags" label="Tags" />
            </v-col>
          </v-row>
          <v-btn
            color="info"
            variant="flat"
            :loading="loading"
            :disabled="!isValid.value"
            type="submit"
          >
            Submit
            <template #loader>
              <v-progress-linear indeterminate color="white" />
            </template>
          </v-btn>
        </v-container>
      </v-card-text>
    </v-card>
  </v-form>
</template>

<script>
import { required } from "@/util/form"

import { mapActions } from "vuex"
import { mapFields } from "vuex-map-fields"
import { isNavigationFailure, NavigationFailureType } from "vue-router"

import router from "@/router"

import DocumentApi from "@/document/api"
import IncidentPrioritySelect from "@/incident/priority/IncidentPrioritySelect.vue"
import IncidentTypeSelect from "@/incident/type/IncidentTypeSelect.vue"
import ProjectSelect from "@/project/ProjectSelect.vue"
import TagFilterAutoComplete from "@/tag/TagFilterAutoComplete.vue"

export default {
  setup() {
    return {
      rules: { required },
    }
  },
  name: "ReportSubmissionCard",

  components: {
    IncidentTypeSelect,
    IncidentPrioritySelect,
    ProjectSelect,
    TagFilterAutoComplete,
  },

  data() {
    return {
      isSubmitted: false,
      project_faq: null,
    }
  },

  computed: {
    ...mapFields("incident", [
      "selected.incident_priority",
      "selected.incident_type",
      "selected.commander",
      "selected.title",
      "selected.tags",
      "selected.description",
      "selected.conversation",
      "selected.conference",
      "selected.visibility",
      "selected.storage",
      "selected.documents",
      "selected.loading",
      "selected.ticket",
      "selected.project",
      "selected.id",
    ]),
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
    ...mapActions("incident", ["report", "get", "resetSelected"]),
  },

  created() {
    if (this.$route.query.project) {
      this.project = { name: this.$route.query.project }
    }

    if (this.$route.query.incident_type) {
      this.incident_type = { name: this.$route.query.incident_type }
    }

    if (this.$route.query.incident_priority) {
      this.incident_priority = { name: this.$route.query.incident_priority }
    }

    if (this.$route.query.title) {
      this.title = this.$route.query.title
    }

    if (this.$route.query.description) {
      this.description = this.$route.query.description
    }

    if (this.$route.query.tag) {
      if (Array.isArray(this.$route.query.tag)) {
        this.tags = this.$route.query.tag.map(function (t) {
          return { name: t }
        })
      } else {
        this.tags = [{ name: this.$route.query.tag }]
      }
    }

    this.getFAQ()

    this.$watch(
      (vm) => [vm.project],
      () => {
        this.getFAQ()
      }
    )

    this.$watch(
      (vm) => [
        vm.project,
        vm.incident_priority,
        vm.incident_type,
        vm.title,
        vm.description,
        vm.tags,
      ],
      () => {
        var queryParams = {
          project: this.project ? this.project.name : null,
          incident_priority: this.incident_priority ? this.incident_priority.name : null,
          incident_type: this.incident_type ? this.incident_type.name : null,
          title: this.title,
          description: this.description,
          tag: this.tags ? this.tags.map((tag) => tag.name) : null,
        }
        Object.keys(queryParams).forEach((key) => (queryParams[key] ? {} : delete queryParams[key]))
        router
          .replace({
            query: queryParams,
          })
          .catch((err) => {
            // Updating the query fields also updates the URL.
            // Frequent updates to these fields throws navigation cancelled failures.
            if (isNavigationFailure(err, NavigationFailureType.cancelled)) {
              // resolve error
              return err
            }
            // rethrow error
            return Promise.reject(err)
          })
      }
    )
  },
}
</script>
