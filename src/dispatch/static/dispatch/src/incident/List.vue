<template>
  <div v-if="items.length">
    <edit-sheet />
    <v-divider></v-divider>
    <v-list>
      <v-list-group no-action>
        <template v-slot:activator>
          <v-list-item>
            <v-list-item-content>
              <v-list-item-title>Incidents ({{ items.length }})</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </template>
        <v-list-item>
          <v-list-item-content>
            <v-data-table :headers="headers" :items="tableItems" hide-default-footer>
              <template v-slot:item.incident_priority.name="{ item }">
                <incident-priority :priority="item.incident_priority.name" />
              </template>
              <template v-slot:item.status="{ item }">
                <incident-status :status="item.status" />
              </template>
              <template v-slot:item.cost="{ item }">{{ item.cost | toUSD }}</template>
              <template v-slot:item.commander="{ item }">
                <individual :individual="item.commander" />
              </template>
              <template v-slot:item.reporter="{ item }">
                <individual :individual="item.reporter" />
              </template>
              <template v-slot:item.reported_at="{ item }">{{
                item.reported_at | formatDate
              }}</template>
              <template v-slot:item.data-table-actions="{ item }">
                <v-menu bottom left>
                  <template v-slot:activator="{ on }">
                    <v-btn icon v-on="on">
                      <v-icon>mdi-dots-vertical</v-icon>
                    </v-btn>
                  </template>
                  <v-list>
                    <v-list-item @click="showEditSheet(item)">
                      <v-list-item-title>Edit / View</v-list-item-title>
                    </v-list-item>
                  </v-list>
                </v-menu>
              </template>
            </v-data-table>
          </v-list-item-content>
        </v-list-item>
      </v-list-group>
    </v-list>
  </div>
</template>
<script>
import { mapActions } from "vuex"

import EditSheet from "@/incident/EditSheet.vue"
import IncidentPriority from "@/incident/IncidentPriority.vue"
import IncidentStatus from "@/incident/IncidentStatus"
import Individual from "@/individual/Individual.vue"

export default {
  name: "IncidentList",

  components: {
    EditSheet,
    IncidentPriority,
    IncidentStatus,
    Individual
  },

  data() {
    return {
      headers: [
        { text: "Name", value: "name", align: "left", width: "10%" },
        { text: "Title", value: "title", sortable: false },
        { text: "Status", value: "status", width: "10%" },
        { text: "Type", value: "incident_type.name" },
        //{ text: "Priority", value: "incident_priority.name", width: "10%" },
        { text: "Cost", value: "cost" },
        { text: "Commander", value: "commander", sortable: false },
        { text: "Reported At", value: "reported_at" },
        { text: "", value: "data-table-actions", sortable: false, align: "end" }
      ]
    }
  },

  computed: {
    tableItems: function() {
      return this.items.map(x => x.content)
    }
  },

  props: {
    items: {
      default: null,
      type: Array
    }
  },

  methods: {
    ...mapActions("incident", ["showEditSheet"])
  }
}
</script>
