<template>
  <v-container fluid grid-list-xl>
    <v-layout row>
      <!-- Filters -->
      <v-flex lg2 sm3 xs6>
        <v-select
          v-model="selectedMonth"
          :items="months"
          label="Month"
          dense
          return-object
        ></v-select>
      </v-flex>
      <!-- Filters Ends-->
    </v-layout>
    <v-layout row wrap>
      <!-- Widgets-->
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
        <incident-priority-basic-bar-chart-card v-model="items" :loading="loading" />
      </v-flex>
      <v-flex lg6 sm6 xs12>
        <incident-type-basic-bar-chart-card v-model="items" :loading="loading" />
      </v-flex>
      <v-flex lg6 sm6 xs12>
        <incident-cost-basic-bar-chart-card v-model="items" :loading="loading" />
      </v-flex>
      <v-flex lg6 sm6 xs12>
        <incident-active-basic-bar-chart-card v-model="items" :loading="loading" />
      </v-flex>
      <v-flex lg6 sm6 xs12></v-flex>
      <!-- Statistics Ends -->
    </v-layout>
  </v-container>
</template>

<script>
import _ from "lodash"
import parseISO from "date-fns/parseISO"
import formatISO from "date-fns/formatISO"
import startOfMonth from "date-fns/startOfMonth"
import endOfMonth from "date-fns/endOfMonth"
import differenceInHours from "date-fns/differenceInHours"
import subMonths from "date-fns/subMonths"
import eachMonthOfInterval from "date-fns/eachMonthOfInterval"
import format from "date-fns/format"
import IncidentApi from "@/incident/api"
import IncidentPriorityBasicBarChartCard from "@/incident/IncidentPriorityBasicBarChartCard"
import IncidentTypeBasicBarChartCard from "@/incident/IncidentTypeBasicBarChartCard"
import IncidentCostBasicBarChartCard from "@/incident/IncidentCostBasicBarChartCard"
import IncidentActiveBasicBarChartCard from "@/incident/IncidentActiveBasicBarChartCard"
import StatWidget from "@/components/StatWidget.vue"
export default {
  name: "IncidentDashboard",

  components: {
    IncidentPriorityBasicBarChartCard,
    IncidentTypeBasicBarChartCard,
    IncidentCostBasicBarChartCard,
    IncidentActiveBasicBarChartCard,
    StatWidget
  },

  data() {
    return {
      tab: null,
      loading: false,
      items: [],
      selectedMonth: null
    }
  },

  methods: {
    fetchData() {
      this.loading = true
      let start = formatISO(startOfMonth(this.selectedMonth.value))
      let end = formatISO(endOfMonth(this.selectedMonth.value))
      IncidentApi.getAll({
        itemsPerPage: -1,
        sortBy: ["reported_at"],
        fields: ["reported_at", "reported_at"],
        ops: ["<=", ">="],
        values: [end, start],
        descending: [true]
      }).then(response => {
        this.loading = false

        // ignore all simulated incidents
        this.items = _.remove(_.sortBy(response.data.items, "reported_at"), function(item) {
          return item.incident_type.name !== "Simulation"
        })
      })
    }
  },

  computed: {
    months() {
      var monthsArr = eachMonthOfInterval({
        end: new Date(),
        start: subMonths(new Date(), 6)
      })

      var monthsSelect = []
      _.forEach(monthsArr, function(month) {
        monthsSelect.push({ text: format(month, "LLLL"), value: month })
      })

      return _.reverse(monthsSelect)
    },
    totalIncidents() {
      return this.items.length
    },
    totalCost() {
      return _.sumBy(this.items, "cost")
    },
    avgCost() {
      return this.totalCost / this.totalIncidents
    },
    totalHours() {
      return _.sumBy(this.items, function(item) {
        let endTime = new Date().toISOString()
        if (item.stable_at) {
          endTime = item.stable_at
        }
        return differenceInHours(parseISO(endTime), parseISO(item.reported_at))
      })
    }
  },

  watch: {
    selectedMonth: function() {
      this.fetchData()
    }
  },

  created() {
    this.selectedMonth = this.months[0]
  }
}
</script>
