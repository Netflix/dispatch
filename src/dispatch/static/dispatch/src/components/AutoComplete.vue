<template>
  <v-autocomplete
    :items="items"
    :label="label"
    :loading="loading"
    clearable
    :item-title="title"
    :item-value="identifier"
    return-object
    :hide-no-data="false"
    v-model:search="search"
    v-model="selectedModel"
    @update:model-value="handleClear"
  >
    <template #no-data>
      <v-list-item v-if="!loading">
        <v-list-item-title>
          No {{ resource }} matching {{}}<strong>"{{ search }}".</strong>
        </v-list-item-title>
      </v-list-item>
    </template>
    <template #item="{ props, item }">
      <slot name="item" :props="props" :item="item">
        <v-list-item v-bind="props" :title="item.title" :subtitle="item.raw[subtitle]" />
      </slot>
    </template>
    <template #append-item v-if="items.length < total.value">
      <v-list-item @click="loadMore">
        <v-list-item-subtitle> Load More </v-list-item-subtitle>
      </v-list-item>
    </template>
  </v-autocomplete>
</template>

<script>
import { ref, watch, toRefs, onMounted } from "vue"
import { initials } from "@/filters"
import { debounce } from "lodash"
import API from "@/api"

export default {
  name: "AutoComplete",
  props: {
    resource: {
      type: String,
      required: true,
    },
    title: {
      type: String,
      default: "name",
    },
    identifier: {
      type: String,
      default: "id",
    },
    subtitle: {
      type: String,
      default: "description",
    },
    label: {
      type: String,
      default: "Select",
    },
    modelValue: {
      type: Object,
      default: () => ({}),
    },
  },
  emits: ["update:modelValue"],
  setup(props, { emit }) {
    const { resource, modelValue } = toRefs(props)

    let loading = ref(false)
    let items = ref([])
    let numItems = ref(10)
    let currentPage = ref(1)
    let total = ref(0)
    let selectedModel = ref(modelValue.value)
    let search = ref(modelValue.value ? modelValue.value[props.title.value] : "")

    let debouncedGetData = debounce((searchVal, page = currentPage.value) => {
      loading.value = true
      API.get(`/${resource.value}`, {
        params: {
          q: searchVal,
          sortBy: ["name"],
          descending: [false],
          itemsPerPage: numItems.value * page,
        },
      }).then((response) => {
        items.value = response.data.items
        total.value = response.data.total
        loading.value = false
      })
    }, 300)

    onMounted(() => {
      debouncedGetData(search.value)
    })

    const handleClear = (newValue) => {
      if (!newValue) {
        items.value = []
        search.value = ""
        selectedModel.value = null
        numItems.value = 10
        currentPage.value = 1
      }
    }

    const loadMore = () => {
      currentPage.value++
      numItems.value += 10
      debouncedGetData(search.value)
    }

    watch(search, (newVal, oldVal) => {
      if (oldVal !== newVal) {
        numItems.value = 10
        currentPage.value = 1
        debouncedGetData(newVal)
      }
    })

    watch(selectedModel, (newVal) => {
      emit(
        "update:modelValue",
        newVal
          ? items.value.find(
              (item) => item[props.identifier.value] == newVal[props.identifier.value]
            )
          : null
      )
    })

    watch(modelValue, (newValue) => {
      selectedModel.value = newValue
      search.value = newValue ? newValue[props.title] : ""
    })

    return {
      initials,
      items,
      loading,
      handleClear,
      loadMore,
      selectedModel,
      search,
      total,
    }
  },
}
</script>
