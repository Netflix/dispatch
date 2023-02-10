<template>
    <v-card flat tile>
      <v-app-bar color="white" flat>
        <v-toolbar-title class="subtitle-2"> Entity Configuration </v-toolbar-title>
        <v-spacer></v-spacer>
        <v-tooltip max-width="250px" bottom>
          <template v-slot:activator="{ on, attrs }">
            <v-icon v-bind="attrs" v-on="on"> help_outline </v-icon>
          </template>
          Dispatch will attempt to locate entities that match the given criteria. Global entities cannot be selected, since they are applied to all signals.
        </v-tooltip>
      </v-app-bar>
      <v-card-text>
        <v-row no-gutters>
          <v-col cols="12">
            <entity-combobox label="Entities" v-model="entity"></entity-combobox>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </template>

  <script>
  import { cloneDeep } from "lodash"
  import EntityCombobox from "@/entity/EntityFilterCombobox.vue"

  export default {
    name: "SignalEntityRuleCard",

    props: {
      value: {
        type: Object,
        default: function () {
          return {
            id: null,
            window: 600,
            entity: [],
          }
        },
      },
    },

    components: {
      EntityCombobox,
    },

    computed: {
      window: {
        get() {
          return this.value ? cloneDeep(this.value.window) : 600
        },
        set(value) {
          this.$emit("input", { id: this.id, window: value, entities: this.entities })
        },
      },
      entities: {
        get() {
          return this.value ? cloneDeep(this.value.entities) : []
        },
        set(value) {
          this.$emit("input", { id: this.id, window: this.window, entities: value })
        },
      },
      id: {
        get() {
          return this.value ? cloneDeep(this.value.id) : null
        },
      },
    },
  }
  </script>
