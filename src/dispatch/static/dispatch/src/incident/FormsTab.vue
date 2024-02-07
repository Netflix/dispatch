<template>
  <new-edit-dialog />
  <delete-dialog />
  <div>
    <v-menu anchor="bottom end">
      <template #activator="{ props }">
        <v-btn v-bind="props" color="info" class="ml-6"> Create New </v-btn>
      </template>
      <div>
        <v-list>
          <template v-for="form_type in form_types">
            <v-list-item
              :key="form_type.id"
              v-if="form_type.enabled"
              @click="createShow(form_type.id)"
            >
              <v-list-item-title>{{ form_type.name }}</v-list-item-title>
            </v-list-item>
          </template>
        </v-list>
      </div>
    </v-menu>
  </div>
  <v-data-table
    :headers="headers"
    :items="items"
    :items-per-page="-1"
    disable-pagination
    hide-default-footer
    class="ml-6 pr-6"
  >
    <template #item.created_at="{ item }">
      <v-tooltip location="bottom">
        <template #activator="{ props }">
          <span v-bind="props">{{ formatRelativeDate(item.created_at) }}</span>
        </template>
        <span>{{ formatDate(item.created_at) }}</span>
      </v-tooltip>
    </template>
    <template #item.updated_at="{ item }">
      <v-tooltip location="bottom">
        <template #activator="{ props }">
          <span v-bind="props">{{ formatRelativeDate(item.updated_at) }}</span>
        </template>
        <span>{{ formatDate(item.updated_at) }}</span>
      </v-tooltip>
    </template>
    <template #item.form_type="{ item }">
      <span v-if="item.form_type">{{ item.form_type.name }}</span>
    </template>
    <template #item.creator="{ item }">
      <participant v-if="item.creator" :participant="convertToParticipant(item.creator)" />
      <span v-else>(anonymous)</span>
    </template>
    <template #item.data-table-actions="{ item }">
      <v-menu location="right" origin="overlap">
        <template #activator="{ props }">
          <v-btn icon variant="text" v-bind="props">
            <v-icon>mdi-dots-vertical</v-icon>
          </v-btn>
        </template>
        <v-list>
          <v-list-item @click="editShow(item)">
            <v-list-item-title>View / Edit</v-list-item-title>
          </v-list-item>
          <v-list-item @click="showDeleteDialog(item)">
            <v-list-item-title>Delete</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </template>
    <template #bottom />
  </v-data-table>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import { formatRelativeDate, formatDate } from "@/filters"
import NewEditDialog from "@/forms/EditForm.vue"
import DeleteDialog from "@/forms/DeleteDialog.vue"
import Participant from "@/incident/Participant.vue"

export default {
  name: "IncidentFormsTab",
  components: { NewEditDialog, DeleteDialog, Participant },
  props: {},
  data() {
    return {
      menu: false,
      headers: [
        { title: "Type", value: "form_type" },
        { title: "Status", value: "status" },
        { title: "Creator", value: "creator" },
        { title: "Created At", value: "created_at" },
        { title: "Updated At", value: "updated_at" },
        { title: "Attorney Status", value: "attorney_status" },
        { title: "", key: "data-table-actions", sortable: false, align: "end" },
      ],
    }
  },
  setup() {
    return { formatRelativeDate, formatDate }
  },
  computed: {
    ...mapFields("forms", [
      "form_types",
      "table.loading",
      "table.rows.items",
      "incident_id",
      "project_id",
      "table.options.filters",
    ]),
    ...mapFields("incident", { selected_incident: "selected", project: "selected.project" }),
  },
  methods: {
    ...mapActions("forms", ["getAll", "createShow", "editShow", "showDeleteDialog"]),
    convertToParticipant(individual) {
      return {
        individual: {
          name: individual.name,
          email: individual.email,
        },
      }
    },
    getFormsData() {
      if (this.selected_incident) {
        this.incident_id = this.selected_incident.id
      }
      if (this.project) {
        this.project_id = this.project.id
      }
      this.getAll()
    },
  },
  created() {
    this.getFormsData()

    this.$watch(
      (vm) => [vm.project, vm.selected_incident, vm.project],
      () => {
        this.getFormsData()
      }
    )
  },
}
</script>
