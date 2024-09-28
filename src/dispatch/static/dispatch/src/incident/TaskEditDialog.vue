<template>
  <v-dialog v-model="showEditTaskDialog" persistent max-width="750px">
    <v-form @submit.prevent v-slot="{ isValid }">
      <v-card>
        <v-card-title>
          <span class="text-h5">Edit Task</span>
        </v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12">
              <v-textarea
                v-model="description"
                auto-grow
                :rows="1"
                :max-rows="5"
                class="mt-3"
                label="Description"
                hint="Description of the task."
                clearable
                required
              />
            </v-col>
            <v-col cols="12">
              <v-select
                v-model="status"
                label="Status"
                :items="statuses"
                hint="The task's current status"
              />
            </v-col>
            <v-col cols="12">
              <participant-select
                v-model="owner"
                label="Owner"
                hint="The task's current owner"
                clearable
                required
                name="owner"
              />
            </v-col>
            <v-col cols="12">
              <assignee-combobox
                v-model="assignees"
                label="Assignee"
                hint="The tasks current assignee"
                clearable
                required
                name="assignees"
                :rules="[required_and_only_one]"
              />
            </v-col>
            <v-col cols="12" v-if="status == 'Resolved'">
              <date-time-picker-menu label="Resolved At" v-model="resolved_at" />
            </v-col>
            <v-col cols="12" v-else>
              <date-time-picker-menu label="Resolve By" v-model="resolve_by" />
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="closeNewTaskDialog()"> Cancel </v-btn>
          <v-btn
            :disabled="!isValid.value"
            color="green en-1"
            variant="text"
            @click="updateExistingTask()"
          >
            OK
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-form>
  </v-dialog>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

import ParticipantSelect from "@/components/ParticipantSelect.vue"
import AssigneeCombobox from "@/task/AssigneeCombobox.vue"
import DateTimePickerMenu from "@/components/DateTimePickerMenu.vue"

export default {
  name: "EditTaskDialog",

  components: {
    AssigneeCombobox,
    ParticipantSelect,
    DateTimePickerMenu,
  },

  data() {
    return {
      statuses: ["Open", "Resolved"],
      required_and_only_one: (value) => {
        if (!value || value.length == 0) {
          return "This field is required"
        }
        if (value && value.length > 1) {
          return "Only one is allowed"
        }
        return true
      },
    }
  },

  computed: {
    ...mapFields("incident", [
      "dialogs.showEditTaskDialog",
      "selected.currentTask.description",
      "selected.currentTask",
      "selected.currentTask.owner",
      "selected.currentTask.assignees",
      "selected.currentTask.resolved_at",
      "selected.currentTask.resolve_by",
      "selected.currentTask.status",
    ]),
  },

  methods: {
    ...mapActions("incident", ["closeNewTaskDialog", "updateExistingTask"]),
  },
}
</script>
