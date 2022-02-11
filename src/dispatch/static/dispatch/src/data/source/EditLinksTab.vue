<template>
  <v-container grid-list-md>
    <div class="d-flex">
      <v-text-field
        v-model="search"
        append-icon="mdi-magnify"
        label="Search"
        dense
        outlined
        single-line
        hide-details
      ></v-text-field>
      <v-btn color="primary" rounded class="ml-2 white--text" @click="addNew">
        <v-icon dark>mdi-plus</v-icon>Add
      </v-btn>
    </div>
    <v-data-table
      :headers="headers"
      :items="links"
      :search="search"
      class="elevation-1"
      fixed-header
      height="350px"
    >
      <template v-slot:item.name="{ item }">
        <v-text-field
          v-model="editedItem.name"
          :hide-details="true"
          dense
          single-line
          v-if="item.id === editedItem.id"
        ></v-text-field>
        <span v-else
          ><a :href="item.href">
            <b>{{ item.name }}</b></a
          ></span
        >
      </template>
      <template v-slot:item.calories="{ item }">
        <v-text-field
          v-model="editedItem.calories"
          :hide-details="true"
          dense
          single-line
          v-if="item.id === editedItem.id"
        ></v-text-field>
        <span v-else>{{ item.calories }}</span>
      </template>
      <template v-slot:item.actions="{ item }">
        <div v-if="item.id === editedItem.id">
          <v-icon class="mr-3" @click="close"> mdi-window-close </v-icon>
          <v-icon @click="save"> mdi-content-save </v-icon>
        </div>
        <div v-else>
          <v-icon class="mr-3" @click="editItem(item)"> mdi-pencil </v-icon>
          <v-icon @click="deleteItem(item)"> mdi-delete </v-icon>
        </div>
      </template>
      <template v-slot:no-data>
        <v-btn color="primary" @click="initialize">Reset</v-btn>
      </template>
    </v-data-table>
  </v-container>
</template>

<script>
import { mapFields } from "vuex-map-fields"
export default {
  name: "SourceEditUsefulLinksTab",

  components: {},

  computed: {
    ...mapFields("source", ["selected.source", "selected.loading"]),
  },
  data: () => ({
    search: "",
    headers: [
      {
        text: "Name",
        value: "name",
        sortable: true,
      },
      {
        text: "Description",
        value: "description",
        sortable: false,
      },
      { text: "Actions", value: "actions", sortable: false, width: "100px" },
    ],
    links: [],
    editedIndex: -1,
    editedItem: {
      id: 0,
      name: "",
      description: "",
      href: "",
    },
    defaultItem: {
      id: 0,
      name: "New Item",
      description: "",
      href: "",
    },
  }),
  created() {
    this.initialize()
  },

  methods: {
    initialize() {
      this.links = [
        {
          id: 1,
          name: "LinkMe",
          description: "foobar",
          href: "https://go.netflix.com",
        },
        {
          id: 2,
          name: "LinkMe",
          description: "foobar",
          href: "https://go.netflix.com",
        },
      ]
    },

    editItem(item) {
      this.editedIndex = this.links.indexOf(item)
      this.editedItem = Object.assign({}, item)
    },

    deleteItem(item) {
      const index = this.links.indexOf(item)
      this.links.splice(index, 1)
    },

    close() {
      setTimeout(() => {
        this.editedItem = Object.assign({}, this.defaultItem)
        this.editedIndex = -1
      }, 300)
    },
    addNew() {
      const addObj = Object.assign({}, this.defaultItem)
      addObj.id = this.links.length + 1
      this.links.unshift(addObj)
    },
    save() {
      if (this.editedIndex > -1) {
        Object.assign(this.links[this.editedIndex], this.editedItem)
      }
      this.close()
    },
  },
}
</script>
