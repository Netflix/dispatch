<template>
  <v-navigation-drawer v-model="showCreateEdit" app clipped right width="500">
    <template v-slot:prepend>
      <v-list-item two-line>
        <v-list-item-content>
          <v-list-item-title v-if="id" class="title"> Edit </v-list-item-title>
          <v-list-item-title v-else class="title"> New </v-list-item-title>
          <v-list-item-subtitle>Plugin Instance</v-list-item-subtitle>
        </v-list-item-content>
        <v-btn icon color="info" :loading="loading" :disabled="!valid" @click="save()">
          <v-icon>save</v-icon>
        </v-btn>
        <v-btn icon color="secondary" @click="closeCreateEdit">
          <v-icon>close</v-icon>
        </v-btn>
      </v-list-item>
    </template>
    <v-card flat>
      <v-card-text>
        <v-form v-model="valid">
          <v-checkbox
            v-model="enabled"
            hint="Each plugin type can only ever have one enabled plugin. Existing enabled plugins will be de-activated."
            label="Enabled"
          />
          <v-jsf v-model="configuration" :schema="configuration_schema" :options="options" />
        </v-form>
      </v-card-text>
    </v-card>
  </v-navigation-drawer>
</template>

<script>
import VJsf from "@koumoul/vjsf"
import "@koumoul/vjsf/dist/main.css"
import { mapFields } from "vuex-map-fields"

import { mapActions, mapMutations } from "vuex"

export default {
  name: "PluginEditSheet",

  components: {
    VJsf,
  },

  data() {
    return {
      valid: false,
      options: {
        initialValidation: "all",
      },
    }
  },

  computed: {
    ...mapFields("plugin", [
      "selected.id",
      "selected.project",
      "selected.enabled",
      "selected.configuration",
      "selected.configuration_schema",
      "selected.loading",
      "selected.plugin",
      "dialogs.showCreateEdit",
    ]),
    ...mapFields("route", ["query"]),
  },

  methods: {
    ...mapActions("plugin", ["save", "closeCreateEdit"]),
    ...mapMutations("plugin", ["addConfigurationItem", "removeConfigurationItem"]),
  },

  created() {
    if (this.query.project) {
      this.project = { name: this.query.project }
    }
  },
}
</script>
