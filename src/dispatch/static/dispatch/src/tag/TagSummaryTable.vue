<template>
  <div>
    <new-edit-sheet />
    <v-data-table :headers="headers" :items="items" hide-default-footer>
      <template v-slot:item.discoverable="{ item }">
        <v-simple-checkbox v-model="item.discoverable" disabled />
      </template>
      <template v-slot:item.project.name="{ item }">
        <v-chip small :color="item.project.color" text-color="white">
          {{ item.project.name }}
        </v-chip>
      </template>
      <template v-slot:item.tag_type.name="{ item }">
        {{ item.tag_type.name }}
      </template>
      <template v-slot:item.data-table-actions="{ item }">
        <v-menu bottom left>
          <template v-slot:activator="{ on }">
            <v-btn icon v-on="on">
              <v-icon>mdi-dots-vertical</v-icon>
            </v-btn>
          </template>
          <v-list>
            <v-list-item @click="createEditShow(item)">
              <v-list-item-title>View / Edit</v-list-item-title>
            </v-list-item>
            <v-list-item @click="removeShow(item)">
              <v-list-item-title>Delete</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>
      </template>
    </v-data-table>
  </div>
</template>

<script>
import { mapActions } from "vuex"
import NewEditSheet from "@/tag/NewEditSheet.vue"
export default {
  name: "TagSummaryTable",

  components: {
    NewEditSheet,
  },
  data() {
    return {
      headers: [
        { text: "Name", value: "name", sortable: true },
        { text: "Description", value: "description", sortable: false },
        { text: "Type", value: "tag_type.name", sortable: true },
        { text: "Source", value: "source", sortable: true },
        { text: "Project", value: "project.name", sortable: true },
        { text: "Discoverable", value: "discoverable", sortable: true },
        { text: "", value: "data-table-actions", sortable: false, align: "end" },
      ],
    }
  },

  props: {
    items: {
      default: function () {
        return []
      },
      type: Array,
    },
    loading: {
      default: function () {
        return false
      },
      type: [String, Boolean],
    },
  },

  methods: {
    ...mapActions("tag", ["createEditShow", "removeShow"]),
  },
}
</script>
