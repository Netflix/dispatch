<template>
  <v-select
    v-model="incident_priorities"
    :items="items"
    item-text="name"
    :menu-props="{ maxHeight: '400' }"
    label="Priority"
    return-object
    :loading="loading"
  />
</template>

<script>
import IncidentPriorityApi from "@/incident_priority/api"
import _ from "lodash"
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
        return _.cloneDeep(this.value)
      },
      set(value) {
        this.$emit("input", value)
      }
    }
  },

  created() {
    this.error = null
    this.loading = true
    IncidentPriorityApi.getAll().then(response => {
      this.items = response.data.items
      this.loading = false
    })
  }
}
</script>
