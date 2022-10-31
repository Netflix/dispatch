<template>
  <v-card flat tile>
    <v-app-bar color="white" flat>
      <v-toolbar-title class="subtitle-2"> Suppression Configuration </v-toolbar-title>
      <v-spacer></v-spacer>
      <v-tooltip max-width="250px" bottom>
        <template v-slot:activator="{ on, attrs }">
          <v-icon v-bind="attrs" v-on="on"> help_outline </v-icon>
        </template>
        Dispatch will attempt to suppress signals that match the given criteria.
      </v-tooltip>
    </v-app-bar>
    <v-card-text>
      <v-row no-gutters>
        <v-col cols="12">
          <tag-auto-complete label="Tags" v-model="tags"></tag-auto-complete>
        </v-col>
        <v-col cols="12">
          <date-time-picker-menu label="Expiration" v-model="expiration" />
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script>
import { cloneDeep } from "lodash"
import TagAutoComplete from "@/tag/TagFilterAutoComplete.vue"
import DateTimePickerMenu from "@/components/DateTimePickerMenu.vue"

export default {
  name: "SignalSuppressionRuleCard",

  props: {
    value: {
      type: Object,
      default: function () {
        return {
          id: null,
          expiration: null,
          tags: [],
        }
      },
    },
  },

  components: {
    TagAutoComplete,
    DateTimePickerMenu,
  },

  data() {
    return {}
  },

  computed: {
    expiration: {
      get() {
        return this.value ? cloneDeep(this.value.expiration) : null
      },
      set(value) {
        this.$emit("input", { id: this.id, expiration: value, tags: this.tags })
      },
    },
    tags: {
      get() {
        return this.value ? cloneDeep(this.value.tags) : []
      },
      set(value) {
        this.$emit("input", { id: this.id, expiration: this.expiration, tags: value })
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
