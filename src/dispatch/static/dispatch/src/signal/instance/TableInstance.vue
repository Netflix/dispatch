<template>
  <v-container fluid>
    <v-row no-gutters>
      <v-col>
        <div class="text-h5">Signals</div>
      </v-col>
    </v-row>
    <v-row no-gutters class="pb-3" align="center">
      <v-col cols="auto" class="pr-4"><div class="text">Group by:</div></v-col>
      <v-col cols="auto" class="pr-4">
        <v-btn
          :class="activeView === 'triggers' ? 'selectedViewButton' : 'viewButton'"
          @click="setActiveView('triggers')"
        >
          <v-icon>mdi-broadcast</v-icon>
          <div class="pl-1">Triggers</div>
        </v-btn>
      </v-col>
      <!--      todo (amats) we should have routes to allow navigation to a certain tab via link-->
      <v-col cols="auto" class="pr-4">
        <v-btn
          :class="activeView === 'entities' ? 'selectedViewButton' : 'viewButton'"
          @click="setActiveView('entities')"
        >
          <v-icon>mdi-cube-outline</v-icon>
          <div class="pl-1">Entities</div>
        </v-btn>
      </v-col>
      <v-col cols="auto" class="pr-4">
        <v-btn
          :class="activeView === 'snoozes' ? 'selectedViewButton' : 'viewButton'"
          @click="setActiveView('snoozes')"
        >
          <v-icon>mdi-bell-off</v-icon>
          <div class="pl-1">Snoozes</div>
        </v-btn>
      </v-col>
      <v-col class="text-right" style="padding-right: 4px">
        <table-filter-dialog />
      </v-col>
    </v-row>
    <table-instance-triggers v-if="activeView === 'triggers'" />
    <table-signal-entities v-if="activeView === 'entities'" />
    <table-filter-snoozes v-if="activeView === 'snoozes'" />
  </v-container>
</template>

<script>
import TableFilterDialog from "@/signal/TableFilterDialog.vue"
import TableInstanceTriggers from "@/signal/instance/TableInstanceTriggers.vue"
import TableSignalEntities from "@/entity/TableSignalEntities.vue"
import TableFilterSnoozes from "@/signal/filter/TableFilterSnoozes.vue"

export default {
  name: "SignalInstanceTable",

  components: {
    TableFilterDialog,
    TableInstanceTriggers,
    TableSignalEntities,
    TableFilterSnoozes,
  },

  data() {
    return {
      activeView: "triggers",
    }
  },

  computed: {},

  methods: {
    /**
     * Set the active view and update the UI accordingly.
     * @param view: The view to set as active ('triggers', 'entities', or 'snoozes').
     */
    setActiveView(view) {
      this.activeView = view
    },
  },
}
</script>

<style>
@import "@/styles/index.scss";

.viewButton {
  background-color: rgb(var(--v-theme-background2));
  color: rgb(var(--v-theme-anchor));
  box-shadow: 0 0 0 0;
}

.selectedViewButton {
  background-color: rgb(var(--v-theme-gray7));
  color: rgb(var(--v-theme-gray0));
  box-shadow: 0 0 0 0;
}
</style>
