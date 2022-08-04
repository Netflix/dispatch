<template>
  <v-list>
    <v-list-item v-if="ticket" :href="ticket.weblink" target="_blank">
      <v-list-item-content>
        <v-list-item-title>Ticket</v-list-item-title>
        <v-list-item-subtitle>{{ ticket.description }}</v-list-item-subtitle>
      </v-list-item-content>
      <v-list-item-action>
        <v-list-item-icon>
          <v-icon>open_in_new</v-icon>
        </v-list-item-icon>
      </v-list-item-action>
    </v-list-item>
    <v-divider />
    <!-- <v-list-item v-if="storage" :href="storage.weblink" target="_blank"> -->
    <!--   <v-list-item-content> -->
    <!--     <v-list-item-title>Storage</v-list-item-title> -->
    <!--     <v-list-item-subtitle>{{ storage.description }}</v-list-item-subtitle> -->
    <!--   </v-list-item-content> -->
    <!--   <v-list-item-action> -->
    <!--     <v-list-item-icon> -->
    <!--       <v-icon>open_in_new</v-icon> -->
    <!--     </v-list-item-icon> -->
    <!--   </v-list-item-action> -->
    <!-- </v-list-item> -->
    <!-- <v-divider /> -->
    <!-- <span v-for="document in documents" :key="document.resource_id"> -->
    <!--   <v-list-item :href="document.weblink" target="_blank"> -->
    <!--     <v-list-item-content> -->
    <!--       <v-list-item-title>{{ document.resource_type | deslug }}</v-list-item-title> -->
    <!--       <v-list-item-subtitle>{{ document.description }}</v-list-item-subtitle> -->
    <!--     </v-list-item-content> -->
    <!--     <v-list-item-action> -->
    <!--       <v-list-item-icon> -->
    <!--         <v-icon>open_in_new</v-icon> -->
    <!--       </v-list-item-icon> -->
    <!--     </v-list-item-action> -->
    <!--   </v-list-item> -->
    <!--   <v-divider /> -->
    <!-- </span> -->
  </v-list>
</template>

<script>
import { mapFields } from "vuex-map-fields"

export default {
  name: "CaseResourcesTab",

  computed: {
    ...mapFields("case_management", [
      "selected.ticket",
      // "selected.storage",
      // "selected.documents",
    ]),
  },
}
</script>
