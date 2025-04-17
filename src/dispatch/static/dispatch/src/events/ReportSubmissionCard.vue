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
import CasePrioritySelect from "@/case/priority/CasePrioritySelect.vue"

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
      this.formIsValid = this.titleValid && this.descriptionValid
    },
    ...mapActions("case_management", ["report", "get", "resetSelected"]),
  },

  created() {
    this.event = true

    if (this.$route.query.title) {
      this.title = this.$route.query.title
    } else {
      this.title = "Security Event Triage"
    }

    if (this.$route.query.description) {
      this.description = this.$route.query.description
    }
    this.fetchData()

    this.$watch(
      (vm) => [vm.project, vm.title, vm.description],
      () => {
        var queryParams = {
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
