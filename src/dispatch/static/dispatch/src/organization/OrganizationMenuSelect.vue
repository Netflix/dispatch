<template>
  <v-autocomplete
    v-model="organization"
    :items="items"
    :menu-props="{ maxHeight: '400' }"
    label="Organization"
    item-title="name"
    return-object
    hide-details
    :loading="loading"
    density="comfortable"
  >
    <template #item="data">
      <v-list-item v-bind="data.props" :title="null" density="comfortable">
        <v-list-item-title>{{ data.item.raw.name }}</v-list-item-title>
        <v-list-item-subtitle :title="data.item.raw.description">
          {{ data.item.raw.description }}
        </v-list-item-subtitle>
      </v-list-item>
    </template>
  </v-autocomplete>
</template>

<script>
import OrganizationApi from "@/organization/api"

export default {
  name: "OrganizationMenuSelect",

  props: {
    modelValue: {
      type: Object,
      default: function () {
        return {}
      },
    },
  },

  data() {
    return {
      loading: false,
      items: [],
    }
  },

  computed: {
    organization: {
      get() {
        return this.modelValue
      },
      set(value) {
        this.$emit("update:modelValue", value)
      },
    },
  },

  created() {
    this.error = null
    this.loading = "error"
    let filterOptions = {
      itemsPerPage: 50,
      sortBy: ["name"],
      descending: [false],
    }

    OrganizationApi.getAll(filterOptions).then((response) => {
      this.items = response.data.items
      this.loading = false
    })
  },
}
</script>
