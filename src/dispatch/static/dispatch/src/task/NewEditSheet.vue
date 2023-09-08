<template>
  <v-form @submit.prevent v-slot="{ isValid }">
    <v-navigation-drawer v-model="showCreateEdit" app clipped location="right" width="500">
      <template #prepend>
        <v-list-item lines="two">
          <v-list-item-title v-if="id" class="text-h6"> Edit </v-list-item-title>
          <v-list-item-title v-else class="text-h6"> New </v-list-item-title>
          <v-list-item-subtitle>Task</v-list-item-subtitle>

          <v-btn
            icon
            variant="text"
            color="info"
            :loading="loading"
            :disabled="!isValid.value"
            @click="save()"
          >
            <v-icon>save</v-icon>
          </v-btn>
          <v-btn icon variant="text" color="secondary" @click="closeCreateEdit()">
            <v-icon>close</v-icon>
          </v-btn>
        </v-list-item>
      </template>
      <v-card flat>
        <v-card-text>
          <v-container grid-list-md>
            <v-layout wrap>
              <v-flex xs12>
                <v-textarea
                  v-model="description"
                  label="Description"
                  hint="The task's description."
                  clearable
                  required
                  name="description"
                />
              </v-flex>
              <v-flex xs12>
                <project-select v-model="project" />
              </v-flex>
              <v-flex xs12>
                <v-select
                  v-model="status"
                  label="Status"
                  :items="statuses"
                  hint="The incident's current status"
                />
              </v-flex>
              <v-flex xs12>
                <incident-select
                  v-model="incident"
                  label="Incident"
                  hint="The tasks associated incident"
                  clearable
                  required
                  name="incident"
                  :rules="[rules.required]"
                />
              </v-flex>
              <v-flex xs12>
                <participant-select
                  v-model="owner"
                  label="Owner"
                  hint="The tasks current owner"
                  clearable
                  required
                  name="owner"
                  :rules="[rules.required]"
                />
              </v-flex>
              <v-flex xs12>
                <assignee-combobox
                  v-model="assignees"
                  label="Assignees"
                  hint="The tasks current assignees"
                  clearable
                  required
                  name="assignees"
                  :rules="[rules.required]"
                />
              </v-flex>
              <v-flex xs12>
                <v-row>
                  <v-col cols="6">
                    <date-time-picker-menu label="Resolved At" v-model="resolved_at" />
                  </v-col>
                  <v-col cols="6">
                    <date-time-picker-menu label="Resolve By" v-model="resolve_by" />
                  </v-col>
                </v-row>
              </v-flex>
            </v-layout>
          </v-container>
        </v-card-text>
      </v-card>
    </v-navigation-drawer>
  </v-form>
</template>

<script>
import { required } from "@/util/form"
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

import ProjectSelect from "@/project/ProjectSelect.vue"
import IncidentSelect from "@/incident/IncidentSelect.vue"
import ParticipantSelect from "@/incident/ParticipantSelect.vue"
import AssigneeCombobox from "@/task/AssigneeCombobox.vue"
import DateTimePickerMenu from "@/components/DateTimePickerMenu.vue"

export default {
  setup() {
    return {
      rules: { required },
    }
  },
  name: "TaskNewEditSheet",

  components: {
    IncidentSelect,
    AssigneeCombobox,
    ParticipantSelect,
    ProjectSelect,
    DateTimePickerMenu,
  },

  data() {
    return {
      statuses: ["Open", "Resolved"],
    }
  },

  computed: {
    ...mapFields("task", [
      "selected.status",
      "selected.owner",
      "selected.assignees",
      "selected.description",
      "selected.creator",
      "selected.project",
      "selected.resolved_at",
      "selected.resolve_by",
      "selected.incident",
      "selected.id",
      "selected.loading",
      "dialogs.showCreateEdit",
    ]),
  },

  methods: {
    ...mapActions("task", ["save", "closeCreateEdit"]),
  },

  created() {
    if (this.$route.query.project) {
      this.project = { name: this.$route.query.project }
    }
  },
}
</script>
