<template>
  <v-select
    v-model="incident_priorities"
    :items="items"
    item-text="name"
    :menu-props="{ maxHeight: '400' }"
    label="Priority"
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
import IncidentPriorityApi from "@/incident_priority/api"
import { cloneDeep } from "lodash"
export default {
  name: "IncidentPrioritySelect",
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
    incident_priorities: {
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
    IncidentPriorityApi.getAll({ sortBy: ["view_order"], descending: [false] }).then(response => {
      this.items = response.data.items
      this.loading = false
    })
  }
}
</script>
