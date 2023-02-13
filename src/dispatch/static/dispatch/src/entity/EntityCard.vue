<template>
    <v-card elevation="1" outlined class="position-relative">
      <v-list-item-action class="position-absolute right-5">
        <v-list-item-icon @click="openSignalInstanceTab">
          <v-icon>mdi-open-in-new</v-icon>
        </v-list-item-icon>
      </v-list-item-action>
      <v-card-title>{{ entity.entity_type.name }}</v-card-title>
      <v-card-text style="font-size: 18px">{{ entity.value }}</v-card-text>
      <v-divider></v-divider>
      <v-hover>
        <template v-slot:default="{ hover }">
          <v-card
            color="red lighten-5"
            outlined
            rounded="xl"
            class="d-flex align-center mx-4 mt-3 mb-3"
            :elevation="hover ? 2 : 0"
            @click="openSignalInstanceTab"
          >
            <v-card-text class="d-flex align-center">
              <v-progress-linear
                v-if="isLoading"
                height="3"
                color="red lighten-1"
                indeterminate
              ></v-progress-linear>
              <span v-else>
                <span v-if="signalInstanceCount > 1">
                  Seen in <span v-bind:class="{ 'font-weight-bold': signalInstanceCount > 5 }">{{ signalInstanceCount }}</span> other signals
                </span>
                <span v-else>
                  First time this entity has been seen in a signal
                </span>
              </span>
            </v-card-text>
          </v-card>
        </template>
      </v-hover>
      <v-hover>
        <template v-slot:default="{ hover }">
          <v-card
            color="red lighten-5"
            outlined
            rounded="xl"
            class="d-flex align-center mx-4 mt-3 mb-3"
            :elevation="hover ? 2 : 0"
          >
            <v-card-text class="d-flex align-center">
              <v-progress-linear
                v-if="isLoading"
                height="3"
                color="red lighten-1"
                indeterminate
              ></v-progress-linear>
              <span v-else>
                <span v-if="caseCount > 1">
                  Seen in <span v-bind:class="{ 'font-weight-bold': caseCount > 5 }">{{ caseCount }}</span> other cases
                </span>
                <span v-else>
                  First time this entity has been seen in a case
                </span>
              </span>
            </v-card-text>
          </v-card>
        </template>
      </v-hover>
      <v-dialog v-model="dialog" max-width="1080">
        <template v-slot:activator="{ on }"></template>
        <signal-instance-tab :inputSignalInstances="signalInstances" />
      </v-dialog>
    </v-card>
  </template>

  <script>
  import SignalInstanceTab from "@/signal/SignalInstanceTab.vue";
  import EntityApi from "@/entity/api"

  export default {
    name: "EntityCard",
    props: {
      entity: {
        type: Object,
        required: true,
      },
    },
    components: {
      "signal-instance-tab": SignalInstanceTab,
    },
    data() {
      return {
        caseCount: null,
        signalInstanceCount: null,
        isLoading: true,
        dialog: false,
        signalInstances: [],
      };
    },
    async mounted() {
      const casePromise = EntityApi.getCasesCount(this.entity.id).then((response) => response.data);
        const signalPromise = EntityApi.getSignalInstances(this.entity.id).then((response) => response.data);

        const [casesResponse, signalResponse] = await Promise.all([
            casePromise,
            signalPromise,
        ]);
        this.caseCount = casesResponse.cases.length;
        console.log(this.caseCount)
        this.signalInstanceCount = signalResponse.instances.length;
        this.isLoading = false;
    },
    methods: {
      async getSignalInstances() {
        this.signalInstances = await EntityApi.getSignalInstances(this.entity.id).then((response) => response.data.instances);
      },
      async openSignalInstanceTab() {
        await this.getSignalInstances();
        this.dialog = true;
        this.$nextTick(() => {
            this.$refs.signalInstanceTab = this.signalInstances;
         });
      },
    },
  };
  </script>
