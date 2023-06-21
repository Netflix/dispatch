<template>
  <v-container fluid>
    <v-row class="nowrap-row pb-4">
      <v-col v-for="(item, index) in displayedCases" :key="index" cols="auto">
        <case-card :_case="item"></case-card>
      </v-col>
    </v-row>
    <!-- <v-row class="mt-2" align="center" justify="center">
      <v-spacer></v-spacer>
      <span class="mr-4 grey--text"> Page {{ currentPage }} of {{ totalPages }} </span>
      <v-btn x-small fab dark color="gray darken-3" class="mr-1" @click="previousPage">
        <v-icon>mdi-chevron-left</v-icon>
      </v-btn>
      <v-btn x-small fab dark color="gray darken-3" class="ml-1" @click="nextPage">
        <v-icon>mdi-chevron-right</v-icon>
      </v-btn>
    </v-row> -->
  </v-container>
</template>

<script>
import CaseCard from "@/case/CaseCard.vue"

export default {
  name: "CaseCardIterator",
  components: {
    CaseCard,
  },
  props: {
    items: {
      type: Array,
      required: true,
    },
    itemsPerPage: {
      type: Number,
      default: 1,
    },
  },
  data() {
    return {
      itemsPerPageArray: [2],
      currentPage: 1,
    }
  },
  computed: {
    totalPages() {
      return Math.ceil(this.items.length / this.itemsPerPage)
    },
    displayedCases() {
      const startIndex = (this.currentPage - 1) * this.itemsPerPage
      const endIndex = startIndex + this.itemsPerPage
      return this.items.slice(startIndex, endIndex)
    },
  },
  methods: {
    nextPage() {
      if (this.currentPage + 1 <= this.totalPages) {
        this.currentPage += 1
      }
    },
    previousPage() {
      if (this.currentPage > 1) {
        this.currentPage -= 1
      }
    },
    updateItemsPerPage(number) {
      this.itemsPerPage = number
      this.currentPage = 1
    },
  },
}
</script>
