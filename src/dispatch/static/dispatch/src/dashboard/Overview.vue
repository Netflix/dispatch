<template>
  <v-container fluid grid-list-xl>
    <v-layout row wrap>
      <!-- Widgets-->
      <v-flex lg3 sm6 xs12>
        <v-menu
          ref="menu"
          v-model="menu"
          :close-on-content-click="false"
          :return-value.sync="dateRangeText"
          transition="scale-transition"
          offset-y
          min-width="290px"
        >
          <template v-slot:activator="{ on }">
            <v-text-field
              v-model="dateRangeText"
              label="Date Range"
              prepend-icon="event"
              readonly
              v-on="on"
            ></v-text-field>
          </template>
          <v-date-picker v-model="dates" type="month" range>
            <v-spacer></v-spacer>
            <v-btn text color="primary" @click="menu = false">Cancel</v-btn>
            <v-btn text color="primary" @click="$refs.menu.save(date)">OK</v-btn>
          </v-date-picker>
        </v-menu>
      </v-flex>
      <v-flex lg2 sm3 xs12> </v-flex>
      <v-flex lg2 sm3 xs12> </v-flex>
      <v-flex lg3 sm6 xs12>
        <stat-widget icon="domain" :title="totalIncidents | toNumberString" supTitle="Incidents" />
      </v-flex>
      <v-flex lg3 sm6 xs12>
        <stat-widget icon="attach_money" :title="totalCost | toUSD" supTitle="Total Cost" />
      </v-flex>
      <v-flex lg3 sm6 xs12>
        <stat-widget icon="show_chart" :title="avgCost | toUSD" supTitle="Avg Cost" />
      </v-flex>
      <v-flex lg3 sm6 xs12>
        <stat-widget
          icon="watch_later"
          :title="totalHours | toNumberString"
          supTitle="Total Hours"
        />
      </v-flex>
      <!-- Widgets Ends -->
      <!-- Statistics -->
      <v-flex lg6 sm6 xs12>
        <incident-type-bar-chart-card
          v-model="groupedItems"
          :loading="loading"
        ></incident-type-bar-chart-card>
      </v-flex>
      <v-flex lg6 sm6 xs12>
        <incident-priority-bar-chart-card
          v-model="groupedItems"
          :loading="loading"
        ></incident-priority-bar-chart-card>
      </v-flex>
      <v-flex lg6 sm6 xs12>
        <incident-cost-bar-chart-card
          v-model="groupedItems"
          :loading="loading"
        ></incident-cost-bar-chart-card>
      </v-flex>
      <v-flex lg6 sm6 xs12>
        <incident-forecast-card></incident-forecast-card>
      </v-flex>
      <v-flex lg6 sm6 xs12>
        <incident-active-time-card
          v-model="groupedItems"
          :loading="loading"
        ></incident-active-time-card>
      </v-flex>
      <v-flex lg6 sm6 xs12>
        <incident-resolve-time-card
          v-model="groupedItems"
          :loading="loading"
        ></incident-resolve-time-card>
      </v-flex>
      <!-- Statistics Ends -->
    </v-layout>
  </v-container>
</template>

<script>
import { remove, groupBy, sortBy, sumBy, map } from "lodash"
import subMonths from "date-fns/subMonths"
import differenceInHours from "date-fns/differenceInHours"
import { parseISO } from "date-fns"

import IncidentApi from "@/incident/api"
import StatWidget from "@/components/StatWidget.vue"
import IncidentTypeBarChartCard from "@/incident/IncidentTypeBarChartCard.vue"
import IncidentActiveTimeCard from "@/incident/IncidentActiveTimeCard.vue"
import IncidentResolveTimeCard from "@/incident/IncidentResolveTimeCard.vue"
import IncidentCostBarChartCard from "@/incident/IncidentCostBarChartCard.vue"
import IncidentPriorityBarChartCard from "@/incident/IncidentPriorityBarChartCard.vue"
import IncidentForecastCard from "@/incident/IncidentForecastCard.vue"
export default {
  name: "IncidentDashboard",

  components: {
    StatWidget,
    IncidentTypeBarChartCard,
    IncidentResolveTimeCard,
    IncidentActiveTimeCard,
    IncidentCostBarChartCard,
    IncidentPriorityBarChartCard,
    IncidentForecastCard
  },

  data() {
    return {
      tab: null,
      loading: false,
      menu: false,
      items: [],
      dates: []
    }
  },

  methods: {
    fetchData() {
      this.loading = true
      IncidentApi.getAll({
        itemsPerPage: -1,
        sortBy: ["reported_at"],
        fields: ["reported_at", "reported_at"],
        ops: [">=", "<="],
        values: this.queryDates,
        descending: [true]
      }).then(response => {
        this.loading = false

        // ignore all simulated incidents
        this.items = remove(sortBy(response.data.items, "reported_at"), function(item) {
          return item.incident_type.name !== "Simulation"
        })
      })
    }
  },

  mounted: function() {
    this.dates = this.defaultDates
  },

  computed: {
    queryDates() {
      // adjust for same month
      if
      return map(this.dates, function(item) {
        return parseISO(item).toISOString()
      })
    },
    defaultDates() {
      return [this.defaultStart, this.defaultEnd]
    },
    today() {
      let now = new Date()
      return new Date(now.getFullYear(), now.getMonth(), 1)
    },
    defaultStart() {
      return subMonths(this.today, 6)
        .toISOString()
        .substr(0, 10)
    },
    defaultEnd() {
      return this.today.toISOString().substr(0, 10)
    },
    dateRangeText() {
      return this.dates.join(" ~ ")
    },
    incidentsByYear() {
      return groupBy(this.items, function(item) {
        return parseISO(item.reported_at).getYear()
      })
    },
    incidentsByMonth() {
      return groupBy(this.items, function(item) {
        return parseISO(item.reported_at).toLocaleString("default", { month: "short" })
      })
    },
    incidentsByQuarter() {
      return groupBy(this.items, function(item) {
        return "Q" + Math.floor(parseISO(item.reported_at).getMonth() + 3) / 3
      })
    },
    groupedItems() {
      return this.incidentsByMonth
    },
    totalIncidents() {
      return this.items.length
    },
    totalCost() {
      return sumBy(this.items, "cost")
    },
    avgCost() {
      return this.totalCost / this.totalIncidents
    },
    totalHours() {
      return sumBy(this.items, function(item) {
        let endTime = new Date().toISOString()
        if (item.stable_at) {
          endTime = item.stable_at
        }
        return differenceInHours(parseISO(endTime), parseISO(item.reported_at))
      })
    }
  },

  watch: {
    dates: function() {
      this.fetchData()
    }
  },

  created() {
    this.fetchData()
    //this.selectedMonth = this.months[0]
  }
}
</script>
