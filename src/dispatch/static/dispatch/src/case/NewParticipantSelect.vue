<template>
  <v-combobox
    :items="items"
    :label="label"
    :loading="loading"
    :search-input.sync="search"
    @update:search-input="getFilteredData()"
    cache-items
    no-filter
    return-object
    flat
    solo
    dense
    v-model="participant"
    style="max-width: 220px"
    hide-details
    class="rounded-xl hover-outline mx-n4"
  >
    <template v-slot:no-data>
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title>
            No individuals matching "
            <strong>{{ search }}</strong
            >".
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </template>
    <template v-slot:item="data">
      <CaseParticipant :participant="data.item" />
    </template>
    <template v-slot:selection="{ attr, on, item, selected }">
      <CaseParticipant :participant="item" />
    </template>
    <template v-slot:append-item>
      <v-list-item v-if="more" @click="loadMore()">
        <v-list-item-content>
          <v-list-item-subtitle> Load More </v-list-item-subtitle>
        </v-list-item-content>
      </v-list-item>
    </template>
  </v-combobox>
</template>

<script>
import { cloneDeep, debounce } from "lodash"

import CaseParticipant from "@/case/Participant.vue"
import SearchUtils from "@/search/utils"
import IndividualApi from "@/individual/api"

export default {
  name: "NewParticipantSelect",

  components: {
    CaseParticipant,
  },

  props: {
    value: {
      type: Object,
      default: function () {
        return null
      },
    },
    label: {
      type: String,
      default: function () {
        return ""
      },
    },
    project: {
      type: [Object],
    },
  },

  data() {
    return {
      loading: false,
      items: [],
      more: false,
      numItems: 5000,
      search: null,
    }
  },

  computed: {
    participant: {
      get() {
        return cloneDeep(this.value)
      },
      set(value) {
        this.$emit("input", value)
      },
    },
  },

  watch: {
    participant: {
      handler(newParticipant, oldParticipant) {
        console.log(newParticipant, oldParticipant)
        if (newParticipant !== oldParticipant) {
          this.$emit("participant-change", newParticipant)
        }
      },
      deep: true,
    },
  },

  created() {
    this.fetchData()
  },

  methods: {
    loadMore() {
      this.numItems = this.numItems + 5
      this.fetchData()
    },
    fetchData() {
      this.loading = "error"
      let filterOptions = {
        q: this.search,
        sortBy: ["name"],
        descending: [false],
        itemsPerPage: this.numItems,
      }
      console.log(this.project)

      if (this.project) {
        filterOptions = {
          ...filterOptions,
          filters: {
            project: [this.project],
          },
        }
        console.log(filterOptions)
        filterOptions = SearchUtils.createParametersFromTableOptions({ ...filterOptions })
      }

      IndividualApi.getAll(filterOptions).then((response) => {
        console.log("individual resp %O", response)
        this.items = response.data.items.map(function (x) {
          return { individual: x }
        })
        this.total = response.data.total

        if (this.items.length < this.total) {
          this.more = true
        } else {
          this.more = false
        }

        this.loading = false
      })
    },
    getFilteredData: debounce(function () {
      this.fetchData()
    }, 500),
  },
}
</script>

<style scoped>
.hover-outline {
  border: 1px dashed transparent;
  border-radius: 0px;
}

.hover-outline:hover {
  border: 1px dashed rgba(148, 148, 148, 0.87);
  border-radius: 0px;
}
</style>
