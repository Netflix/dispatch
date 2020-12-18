<template>
  <v-autocomplete
    v-model="participant"
    :items="items"
    item-text="name"
    :search-input.sync="search"
    :menu-props="{ maxHeight: '400' }"
    :label="label"
    :loading="loading"
    chips
    cache-items
    return-object
  >
    <template v-slot:no-data>
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title>
            No indivduals matching "
            <strong>{{ search }}</strong
            >".
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </template>
  </v-autocomplete>
</template>

<script>
import IndividualApi from "@/individual/api"
import { map } from "lodash"
export default {
  name: "ParticipantSelect",
  props: {
    value: {
      type: Object,
      default: function() {
        return {}
      }
    },
    label: {
      type: String,
      default: function() {
        return "Participant"
      }
    }
  },

  data() {
    return {
      loading: false,
      items: [],
      search: null
    }
  },

  computed: {
    participant: {
      get() {
        if (!this.value) return
        return this.value
      },
      set(value) {
        let wrapped = value
        if (!("individual" in wrapped)) {
          wrapped = { individual: wrapped }
        }
        this.$emit("input", wrapped)
        this.search = null
      }
    }
  },

  watch: {
    search(val) {
      val && val !== this.select && this.querySelections(val)
    },
    value(val) {
      if (!val) return
      console.log(val)
      this.items.push.apply(
        this.items,
        map(val, function(item) {
          console.log(item)
          return item["individual"]
        })
      )
    }
  },

  methods: {
    querySelections(v) {
      this.loading = "error"
      // Simulated ajax query
      IndividualApi.getAll({ q: v }).then(response => {
        this.items = response.data.items
        this.loading = false
      })
    }
  },

  mounted() {
    this.error = null
    this.loading = "error"
    IndividualApi.getAll().then(response => {
      this.items = response.data.items
      this.loading = false
    })
  }
}
</script>
