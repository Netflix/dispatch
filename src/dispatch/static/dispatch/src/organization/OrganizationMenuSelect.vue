<template>
  <v-autocomplete
    v-model="organization"
    :items="items"
    :menu-props="{ maxHeight: '400' }"
    label="Organization"
    item-text="name"
    return-object
    hide-details
    :loading="loading"
    outlined
    dense
  >
    <template v-slot:item="data">
      <v-list-item-content>
        <v-list-item-title v-text="data.item.name" />
        <v-list-item-subtitle
          style="width: 200px"
          class="text-truncate"
          v-text="data.item.description"
        />
      </v-list-item-content>
    </template>
  </v-autocomplete>
</template>

<script>
import OrganizationApi from "@/organization/api"

export default {
  name: "OrganizationMenuSelect",

  props: {
    value: {
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
        return this.value
      },
      set(value) {
        this.$emit("input", value)
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
