<template>
  <v-skeleton-loader :loading="isLoading" type="table" height="500px">
    <v-row>
      <v-col cols="3">
        <template v-if="!signalInstances.length">
          No example signals are currently available for this definition.
        </template>
        <v-virtual-scroll v-else :items="signalInstances" height="800" item-height="50">
          <template v-slot="{ item, index }">
            <v-list-item class="mb-n1">
              <v-list-item-content>
                <v-list-item-subtitle>
                  <b>{{ index + 1 }} </b> {{ item.created_at }}</v-list-item-subtitle
                >
              </v-list-item-content>
              <v-list-item-action>
                <v-btn icon @click="updateEditorValue(item)">
                  <v-icon small>mdi-arrow-right</v-icon>
                </v-btn>
              </v-list-item-action>
            </v-list-item>
            <v-divider v-if="index < signalInstances.length - 1"></v-divider>
          </template>
        </v-virtual-scroll>
        <template v-else> </template>
      </v-col>
      <v-divider vertical></v-divider>
      <v-col cols="9">
        <new-raw-signal-viewer v-if="selectedSignalInstance" :item="selectedSignalInstance" />
      </v-col>
    </v-row>
  </v-skeleton-loader>
</template>

<script>
import SignalInstanceTab from "@/signal/SignalInstanceTab.vue"
import NewRawSignalViewer from "@/signal/NewRawSignalViewer.vue"
import CaseApi from "@/case/api"

export default {
  name: "SignalInstanceCardViewer",
  components: {
    NewRawSignalViewer,
    SignalInstanceTab,
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
      selectedSignalInstance: null, // add this line
      isLoading: true,
    }
  },
  methods: {
    fetchSignalInstances(caseId) {
      this.isLoading = true
      return CaseApi.getAllSignalInstances(caseId).then((response) => {
        this.signalInstances = response.data.instances.flat()
        this.updateEditorValue(this.signalInstances[0])
        this.isLoading = false
      })
    },
    updateEditorValue(instance) {
      console.log(instance)
      this.selectedSignalInstance = instance
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
