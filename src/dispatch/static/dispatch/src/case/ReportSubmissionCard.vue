<template>
  <ValidationObserver v-slot="{ invalid, validated }">
    <v-card class="mx-auto ma-4" max-width="600" flat variant="outlined" :loading="loading">
      <v-card-text>
        <p class="text-h4 text--primary">
          Open a Case
          <v-tooltip location="bottom">
            <template #activator="{ on }">
              <v-btn icon variant="text" v-on="on" @click="copyView">
                <v-icon>mdi-content-copy</v-icon>
              </v-btn>
            </template>
            <span>Copy current fields as template.</span>
          </v-tooltip>
        </p>
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
            <v-icon size="small">open_in_new</v-icon>
          </a>
        </p>
        <v-form>
          <v-container grid-list-md>
            <v-layout wrap>
              <v-flex xs12>
                <ValidationProvider name="Title" rules="required" immediate>
                  <v-textarea
                    v-model="title"
                    slot-scope="{ errors, valid }"
                    :error-messages="errors"
                    :success="valid"
                    label="Title"
                    hint="A brief explanatory title. You can change this later."
                    clearable
                    auto-grow
                    rows="2"
                    required
                  />
                </ValidationProvider>
              </v-flex>
              <v-flex xs12>
                <ValidationProvider name="Description" rules="required" immediate>
                  <v-textarea
                    v-model="description"
                    slot-scope="{ errors, valid }"
                    :error-messages="errors"
                    :success="valid"
                    label="Description"
                    hint="A summary of what you know so far. It's all right if this is incomplete."
                    clearable
                    auto-grow
                    rows="3"
                    required
                  />
                </ValidationProvider>
              </v-flex>
              <v-flex xs12>
                <project-select v-model="project" />
              </v-flex>
              <v-flex xs12>
                <case-type-select :project="project" v-model="case_type" />
              </v-flex>
              <v-flex xs12>
                <case-priority-select :project="project" v-model="case_priority" />
              </v-flex>
              <v-flex xs12>
                <tag-filter-auto-complete :project="project" v-model="tags" label="Tags" />
              </v-flex>
            </v-layout>
            <template>
              <v-btn
                color="info"
                variant="flat"
                :loading="loading"
                :disabled="invalid || !validated"
                @click="report()"
              >
                Submit
                <template #loader>
                  <v-progress-linear indeterminate color="white" />
                </template>
              </v-btn>
            </template>
          </v-container>
        </v-form>
      </v-card-text>
    </v-card>
  </ValidationObserver>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import { ValidationObserver, ValidationProvider, extend } from "vee-validate"
import { required } from "vee-validate/dist/rules"
import router from "@/router"
import CaseTypeSelect from "@/case/type/CaseTypeSelect.vue"
import CasePrioritySelect from "@/case/priority/CasePrioritySelect.vue"
import ProjectSelect from "@/project/ProjectSelect.vue"
import DocumentApi from "@/document/api"
import TagFilterAutoComplete from "@/tag/TagFilterAutoComplete.vue"

extend("required", {
  ...required,
  message: "This field is required",
})

export default {
  name: "ReportSubmissionCard",

  components: {
    ValidationProvider,
    ValidationObserver,
    CaseTypeSelect,
    CasePrioritySelect,
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
    ...mapFields("case_management", [
      "selected.case_priority",
      "selected.case_type",
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
      this.$copyText(window.location).then(
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
    ...mapActions("case_management", ["report", "get", "resetSelected"]),
  },

  created() {
    if (this.$route.query.project) {
      this.project = { name: this.$route.query.project }
    }

    if (this.$route.query.case_type) {
      this.case_type = { name: this.$route.query.case_type }
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

    if (this.$route.query.tag) {
      if (Array.isArray(this.$route.query.tag)) {
        this.tags = this.$route.query.tag.map(function (t) {
          return { name: t }
        })
      } else {
        this.tags = [{ name: this.$route.query.tag }]
      }
    }
  },
}
</script>
