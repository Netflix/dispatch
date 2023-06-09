<template>
  <v-data-iterator
    :items="signalInstances"
    :items-per-page="1"
    :footer-props="{
      'items-per-page-options': [1, 5, 10],
    }"
  >
    <template v-slot:default="props">
      <v-row v-for="item in props.items" :key="item.id">
        <div style="width: 100%">
          <new-raw-signal-viewer :item="item" />
        </div>
      </v-row>
    </template>
  </v-data-iterator>
</template>

<script>
import CaseApi from "@/case/api"
import NewRawSignalViewer from "@/signal/NewRawSignalViewer.vue"

export default {
  name: "SignalInstanceCardViewer",
  components: {
    NewRawSignalViewer,
  },
  props: {
    caseId: {
      type: Number,
    },
  },
  data() {
    return {
      menu: false,
      workflowRunDialog: false,
      signalInstances: [],
    }
  },
  methods: {
    fetchSignalInstances(caseId) {
      return CaseApi.getAllSignalInstances(caseId).then((response) => {
        console.log(response)
        this.signalInstances = response.data.instances.flat()
      })
    },
  },
  watch: {
    caseId(newCaseId) {
      this.fetchSignalInstances(newCaseId)
    },
  },
  created() {
    this.fetchSignalInstances(this.caseId)
  },
}
</script>
