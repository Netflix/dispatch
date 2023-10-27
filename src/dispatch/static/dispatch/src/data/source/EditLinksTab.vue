<template>
  <v-container>
    <v-card>
      <div class="d-flex">
        <v-text-field
          v-model="q"
          append-inner-icon="mdi-magnify"
          label="Search"
          single-line
          hide-details
          append-icon="mdi-plus"
          @click:append="addNew"
          clearable
        />
      </div>
      <v-data-table :headers="headers" :items="links" :search="q">
        <template #item.name="{ item }">
          <v-text-field
            v-model="editedItem.name"
            :hide-details="true"
            density="compact"
            placeholder="Name"
            single-line
            v-if="item.id === editedItem.id"
          />
          <v-text-field
            v-model="editedItem.href"
            :hide-details="true"
            density="compact"
            placeholder="Link"
            single-line
            v-if="item.id === editedItem.id"
          />
          <span v-else
            ><a :href="item.href">
              <b>{{ item.name }}</b></a
            ></span
          >
        </template>
        <template #item.description="{ item }">
          <v-text-field
            v-model="editedItem.description"
            :hide-details="true"
            density="compact"
            placeholder="Description"
            single-line
            v-if="item.id === editedItem.id"
          />
          <span v-else>{{ item.description }}</span>
        </template>
        <template #item.actions="{ item }">
          <div v-if="item.id === editedItem.id">
            <v-icon class="mr-3" @click="close"> mdi-window-close </v-icon>
            <v-icon @click="save"> mdi-content-save </v-icon>
          </div>
          <div v-else>
            <v-icon class="mr-3" @click="editItem(item)"> mdi-pencil </v-icon>
            <v-icon @click="deleteItem(item)"> mdi-delete </v-icon>
          </div>
        </template>
      </v-data-table>
    </v-card>
  </v-container>
</template>

<script>
import { mapFields } from "vuex-map-fields"
export default {
  name: "SourceEditUsefulLinksTab",

  computed: {
    ...mapFields("source", ["selected.links", "selected.loading"]),
  },
  data: () => ({
    q: "",
    headers: [
      {
        title: "Name",
        key: "name",
        sortable: true,
      },
      {
        title: "Description",
        key: "description",
        sortable: false,
      },
      { title: "Actions", key: "actions", sortable: false, width: "100px" },
    ],
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

  methods: {
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
      this.editedItem.id = addObj.id
      this.editedIndex = 0
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
