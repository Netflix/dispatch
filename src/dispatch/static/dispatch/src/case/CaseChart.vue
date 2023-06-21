<template>
  <div>
    <apexchart type="area" height="350" :options="chartOptions" :series="series"></apexchart>
  </div>
</template>

<script>
import VueApexCharts from "vue-apexcharts"

export default {
  name: "NewCaseChart",
  components: {
    apexchart: VueApexCharts,
  },
  data() {
    return {
      series: [
        {
          name: "Low",
          data: [31, 40, 28, 51, 42, 109, 100, 42, 109, 100, 20, 9],
        },
        // {
        //   name: "Medium",
        //   data: [11, 32, 45, 32, 34, 52, 41],
        // },
        // {
        //   name: "High",
        //   data: [8, 20, 17, 9, 30, 21, 41],
        // },
        // {
        //   name: "Critical",
        //   data: [2, 4, 2, 12, 8, 6, 18],
        // },
      ],
      chartOptions: {
        chart: {
          height: 350,
          type: "area",
          toolbar: {
            show: false,
          },
        },
        dataLabels: {
          enabled: false,
        },
        legend: {
          show: false,
        },
        xaxis: {
          type: "string",
          categories: [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
          ],
        },
        yaxis: {
          show: false,
        },
        tooltip: {
          x: {
            format: "dd/MM/yy HH:mm",
          },
        },
        stroke: {
          curve: "smooth",
          width: 2, // adjust this value to make the lines thinner or thicker
          colors: ["black"],
        },

        fill: {
          type: "gradient",
          gradient: {
            shadeIntensity: 1,
            opacityFrom: 0.9,
            opacityTo: 0.1,
            stops: [0, 100],
            colorStops: [
              {
                offset: 0,
                color: "blue",
                opacity: 0.1,
              },
              {
                offset: 33,
                color: "purple",
                opacity: 0.1,
              },
              {
                offset: 66,
                color: "pink",
                opacity: 0.4,
              },
              {
                offset: 100,
                color: "white",
                opacity: 0.5,
              },
              {
                offset: 100,
                color: "white",
                opacity: 0.1,
              },
            ],
          },
        },
      },
    }
  },
}
</script>
