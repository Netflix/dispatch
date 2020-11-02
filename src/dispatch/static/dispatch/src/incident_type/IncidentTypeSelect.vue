<template>
  <v-select
    v-model="incident_type"
    :items="items"
    :menu-props="{ maxHeight: '400' }"
    item-text="name"
    label="Type"
    return-object
    :loading="loading"
  >
    <template v-slot:item="data">
      <template>
        <v-list-item-content>
          <v-list-item-title v-text="data.item.name"></v-list-item-title>
          <v-list-item-subtitle v-text="data.item.description"></v-list-item-subtitle>
        </v-list-item-content>
      </template>
    </template>
  </v-select>
</template>

<script>
import IncidentTypeApi from "@/incident_type/api"
import { cloneDeep } from "lodash"
export default {
  name: "IncidentTypeSelect",

  props: {
    value: {
      type: Object,
      default: function() {
        return {}
      }
    }
  },

  data() {
    return {
      loading: false,
      items: []
    }
  },

  computed: {
    incident_type: {
      get() {
        return cloneDeep(this.value)
      },
      set(value) {
        this.$emit("input", value)
      }
    }
  },

  created() {
    this.error = null
    this.loading = true
    IncidentTypeApi.getAll({ itemsPerPage: 50, sortBy: ["name"], descending: [false] }).then(
      response => {
        this.items = response.data.items
        this.loading = false
      }
    )
  }
}
</script>
