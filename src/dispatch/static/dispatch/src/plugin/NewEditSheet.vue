<template>
  <v-navigation-drawer v-model="showCreateEdit" app clipped right width="500">
    <template v-slot:prepend>
      <v-list-item two-line>
        <v-list-item-content>
          <v-list-item-title v-if="id" class="title"> Edit </v-list-item-title>
          <v-list-item-title v-else class="title"> New </v-list-item-title>
          <v-list-item-subtitle>Plugin Instance</v-list-item-subtitle>
        </v-list-item-content>
        <v-btn icon color="info" :loading="loading" @click="save()">
          <v-icon>save</v-icon>
        </v-btn>
        <v-btn icon color="secondary" @click="closeCreateEdit">
          <v-icon>close</v-icon>
        </v-btn>
      </v-list-item>
    </template>
    <v-card flat>
      <v-card-text>
        <v-container grid-list-md>
          <v-layout wrap>
            <v-flex xs12>
              <span class="subtitle-2">Plugin Configuration</span>
              <v-checkbox
                v-model="enabled"
                hint="Each plugin type can only ever have one enabled plugin. Existing enabled plugins will be de-activated."
                label="Enabled"
              />
            </v-flex>
            <v-flex xs12>
              <v-form v-model="valid">
                <v-jsf v-model="model" :schema="configuration_schema" />
              </v-form>
            </v-flex>
          </v-layout>
        </v-container>
      </v-card-text>
    </v-card>
  </v-navigation-drawer>
</template>

<script>
import VJsf from "@koumoul/vjsf"
import "@koumoul/vjsf/dist/main.css"
import { mapFields, mapMultiRowFields } from "vuex-map-fields"
import { mapActions, mapMutations } from "vuex"

export default {
  name: "PluginEditSheet",

  components: {
    VJsf,
  },

  data() {
    return {
      valid: false,
      model: {},
    }
  },

  computed: {
    ...mapFields("plugin", [
      "selected.id",
      "selected.project",
      "selected.enabled",
      "selected.configuration_schema",
      "selected.loading",
      "selected.plugin",
      "dialogs.showCreateEdit",
    ]),
    ...mapFields("route", ["query"]),
    ...mapMultiRowFields("plugin", ["selected.configuration"]),
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
