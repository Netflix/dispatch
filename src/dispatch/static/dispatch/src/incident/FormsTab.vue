<template>
  <div>
    <v-menu anchor="bottom end">
      <template #activator="{ props }">
        <v-btn v-bind="props" color="info" class="ml-6"> Create New </v-btn>
      </template>
      <div>
        <v-list>
          <template v-for="form_type in form_types">
            <v-list-item :key="form_type.id" v-if="form_type.enabled" @click="blank(form_type)">
              <v-list-item-title>{{ form_type.name }}</v-list-item-title>
            </v-list-item>
          </template>
        </v-list>
      </div>
    </v-menu>
  </div>
  <v-data-table
    :headers="headers"
    :items="modelValue"
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
    <template #item.data-table-actions="{ item }">
      <v-menu location="right" origin="overlap">
        <template #activator="{ props }">
          <v-btn icon variant="text" v-bind="props">
            <v-icon>mdi-dots-vertical</v-icon>
          </v-btn>
        </template>
        <v-list>
          <v-list-item :to="{ name: 'FormsTableEdit', params: { name: item.id } }">
            <v-list-item-title>View / Edit</v-list-item-title>
          </v-list-item>
          <v-list-item :to="{ name: 'FormsTableDelete', params: { name: item.id } }">
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

export default {
  name: "InicdentFormsTab",
  props: {
    modelValue: {
      type: Array,
      default: function () {
        return [
          {
            id: 1,
            type: "Privacy Assessment",
            status: "Complete",
            creator: { name: "David Whittaker" },
            created_at: "2023-11-07T01:50Z",
          },
          {
            id: 2,
            type: "Materiality Assessment",
            status: "Draft",
            creator: { name: "Kyle Smith" },
            created_at: "2023-11-07T14:50Z",
          },
        ]
      },
    },
  },
  data() {
    return {
      menu: false,
      headers: [
        { title: "Type", value: "type" },
        { title: "Status", value: "status" },
        { title: "Creator", value: "creator.name" },
        { title: "Created At", value: "created_at" },
        { title: "", key: "data-table-actions", sortable: false, align: "end" },
      ],
    }
  },
  setup() {
    return { formatRelativeDate, formatDate }
  },
  computed: {
    ...mapFields("forms", ["form_types"]),
  },
  methods: {
    ...mapActions("forms", ["getAll"]),
    blank(form_type) {
      console.log(`**** Got form type ${JSON.stringify(form_type)}`)
    },
  },
  created() {
    this.getAll()
  },
}
</script>
