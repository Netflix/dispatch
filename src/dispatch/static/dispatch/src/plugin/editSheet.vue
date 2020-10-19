<template>
  <v-navigation-drawer v-model="showEdit" app clipped right width="500">
    <template v-slot:prepend>
      <v-list-item two-line>
        <v-list-item-content>
          <v-list-item-title class="title">Edit</v-list-item-title>
          <v-list-item-subtitle>Plugin</v-list-item-subtitle>
        </v-list-item-content>
        <v-btn icon color="primary" :loading="loading" @click="save()">
          <v-icon>save</v-icon>
        </v-btn>
        <v-btn icon color="secondary" @click="closeEdit">
          <v-icon>close</v-icon>
        </v-btn>
      </v-list-item>
    </template>
    <v-card flat>
      <v-card-text>
        <v-container grid-list-md>
          <v-layout wrap>
            <v-flex xs12>
              <span class="subtitle-2">Details</span>
            </v-flex>
            <v-flex xs12>
              <v-text-field v-model="title" disabled label="Title" hint="A name for your plugin." />
            </v-flex>
            <v-flex xs12>
              <v-text-field v-model="slug" disabled label="Slug" hint="A slug for your plugin." />
            </v-flex>
            <v-flex xs12>
              <v-text-field
                v-model="type"
                disabled
                label="Plugin"
                hint="Plugin that will help with resolution."
              />
            </v-flex>
            <v-flex xs12>
              <v-textarea
                v-model="description"
                disabled
                label="Description"
                hint="A description for your plugin."
              />
            </v-flex>
            <v-flex xs12>
              <v-checkbox
                v-model="enabled"
                hint="Each plugin type can only ever have one enabled plugin. Existing enabled plugins will be de-activated."
                label="Enabled"
              />
            </v-flex>
          </v-layout>
        </v-container>
      </v-card-text>
    </v-card>
  </v-navigation-drawer>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

export default {
  name: "PluginEditSheet",

  components: {},

  computed: {
    ...mapFields("plugin", [
      "selected.title",
      "selected.slug",
      "selected.type",
      "selected.id",
      "selected.description",
      "selected.enabled",
      "selected.loading",
      "dialogs.showEdit"
    ])
  },

  methods: {
    ...mapActions("plugin", ["save", "closeEdit"])
  }
}
</script>
