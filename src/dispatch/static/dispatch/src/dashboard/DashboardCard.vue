<template>
  <v-card :loading="loading" outlined elevation="0">
    <v-card-title>{{ title }}</v-card-title>
    <apexchart :type="type" height="250" :options="localOptions" :series="series"></apexchart>
  </v-card>
</template>

<script>
import VueApexCharts from "vue-apexcharts"
export default {
  name: "DashboardCard",

  components: {
    apexchart: VueApexCharts
  },

  props: {
    loading: {
      type: [String, Boolean],
      default: function() {
        return false
      }
    },
    type: {
      type: String,
      default: function() {
        return "bar"
      }
    },
    options: {
      type: Object,
      required: true
    },
    series: {
      type: Array[Object],
      required: true
    },
    title: {
      type: String,
      required: true
    }
  },

  data() {
    return {
      localOptions: JSON.parse(JSON.stringify(this.options))
    }
  },
  watch: {
    options: function(newVal, oldVal) {
      this.localOptions = { ...this.localOptions, ...newVal }
    },
    "$vuetify.theme.dark": function(newValue) {
      this.localOptions = {
        ...this.localOptions,
        ...{
          theme: {
            mode: newValue ? "dark" : "light"
          }
        }
      }
    }
  }
}
</script>
