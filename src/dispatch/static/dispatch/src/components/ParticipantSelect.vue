<template>
  <v-combobox
    :items="items"
    :label="labelProp"
    :loading="loading"
    v-model:search="search"
    clearable
    hide-selected
    item-title="individual.name"
    no-filter
    return-object
    chips
    v-model="participant"
    @update:modelValue="handleClear"
  >
    <template #no-data>
      <v-list-item>
        <v-list-item-title>
          No individuals matching "
          <strong>{{ search }}</strong
          >".
        </v-list-item-title>
      </v-list-item>
    </template>
    <template #item="{ props, item }">
      <v-list-item v-bind="props" :subtitle="item.raw.individual.email" />
    </template>
    <template #append-item v-if="items.length < total.value">
      <v-list-item @click="loadMore()">
        <v-list-item-subtitle> Load More </v-list-item-subtitle>
      </v-list-item>
    </template>
    <template #chip="data">
      <v-chip v-bind="data.props" pill>
        <template #prepend>
          <v-avatar color="teal" start> {{ initials(data.item.title) }} </v-avatar>
        </template>
        {{ data.item.title }}
      </v-chip>
    </template>
  </v-combobox>
</template>

<script>
import { ref, watch, toRefs, onMounted } from "vue"
import { initials } from "@/filters"
import { debounce } from "lodash"

import IndividualApi from "@/individual/api"

export default {
  name: "ParticipantSelect",
  props: {
    labelProp: {
      // Define the labelProp
      type: String,
      default: "Participant",
    },
    initialValue: {
      type: Object,
      default: () => ({}),
    },
  },
  setup(props) {
    const { labelProp } = toRefs(props) // toRefs make props reactive

    let loading = ref(false)
    let items = ref([])
    let numItems = ref(10)
    let participant = ref(null)
    let currentPage = ref(1)
    let total = ref(0)
    const search = ref(props.initialValue)

    let debouncedGetIndividualData = null

    const getIndividualData = async (searchVal, page = currentPage.value) => {
      loading.value = true
      let filterOptions = {
        q: searchVal,
        sortBy: ["name"],
        descending: [false],
        itemsPerPage: numItems.value * page,
      }

      await IndividualApi.getAll(filterOptions).then((response) => {
        items.value = response.data.items.map(function (x) {
          return { individual: x }
        })
        total.value = response.data.total
      })

      loading.value = false
    }

    onMounted(() => {
      debouncedGetIndividualData = debounce(getIndividualData, 300)
      if (props.initialValue && props.initialValue.id) {
        participant = { ...props.initialValue }
        search = props.initialValue.name
      }
    })

    const loadMore = async () => {
      currentPage.value++
      numItems.value += 10
      await debouncedGetIndividualData(search.value)
    }

    const handleClear = (newValue) => {
      if (!newValue) {
        items.value = []
        search.value = null
        participant.value = null
        numItems.value = 10
        currentPage.value = 1
      }
    }

    watch(search, async (newVal, oldVal) => {
      if (oldVal !== newVal) {
        numItems.value = 10
        await debouncedGetIndividualData(newVal)
      }
    })

    return {
      getIndividualData,
      handleClear,
      initials,
      items,
      loading,
      loadMore,
      participant,
      search,
      total,
    }
  },
}
</script>
