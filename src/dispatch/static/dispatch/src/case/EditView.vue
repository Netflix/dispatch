<template>
  <v-row no-gutters>
    <v-col cols="6" md="4">
      <case-table-condensed />
    </v-col>
    <v-col cols="12" sm="6" md="8" style="border-left: 1px solid #dddddd">
      <v-card flat>
        <ValidationObserver v-slot="{}">
          <template>
            <v-list-item two-line>
              <project-picker-menu v-model="project" />
              <v-list-item-content>
                <v-list-item-title class="title">
                  {{ name }} -
                  <span v-if="titleEdit">
                    <v-text-field v-model="title" clearable />
                  </span>
                  <span class="text-truncate" v-else>
                    {{ title }}
                  </span>
                </v-list-item-title>
                <v-list-item-subtitle>
                  <v-btn icon><v-icon>mdi-calendar</v-icon></v-btn> Reported -
                  {{ reported_at | formatRelativeDate }}
                </v-list-item-subtitle>
              </v-list-item-content>
              <v-toolbar flat dense>
                <v-spacer />
                <v-checkbox
                  v-model="visibility"
                  label="Restricted"
                  color="red"
                  value="Restricted"
                  hide-details
                  dense
                ></v-checkbox>
                <v-btn icon>
                  <v-icon>mdi-account-circle-outline</v-icon>
                </v-btn>
                <v-tooltip bottom>
                  <template v-slot:activator="{ on }">
                    <v-btn
                      @click="showEscalateDialog(selected)"
                      color="error"
                      :disabled="status != 'New' && status != 'Triage'"
                      icon
                      v-on="on"
                    >
                      <v-icon>error_outline</v-icon>
                    </v-btn>
                  </template>
                  <span>Escalate</span>
                </v-tooltip>
                <v-btn icon color="secondary" @click="closeEditSheet">
                  <v-icon>close</v-icon>
                </v-btn>
              </v-toolbar>
            </v-list-item>
            <v-divider />
          </template>
          <v-tabs color="primary" vertical v-model="tab">
            <v-tooltip bottom>
              <template v-slot:activator="{ on }">
                <v-tab v-on="on" key="details"> <v-icon>mdi-information-outline</v-icon> </v-tab>
              </template>
              <span>Details</span>
            </v-tooltip>
            <v-tooltip bottom>
              <template v-slot:activator="{ on }">
                <v-tab v-on="on" key="resources">
                  <v-icon>mdi-file-document-multiple</v-icon>
                </v-tab>
              </template>
              <span>Resources</span>
            </v-tooltip>
            <v-tooltip bottom>
              <template v-slot:activator="{ on }">
                <v-tab v-on="on" key="timeline"> <v-icon>mdi-timeline-clock-outline</v-icon></v-tab>
              </template>
              <span>Timeline</span>
            </v-tooltip>
            <v-tabs-items v-model="tab">
              <v-tab-item key="details">
                <case-details-tab />
              </v-tab-item>
              <v-tab-item key="resources">
                <case-resources-tab />
              </v-tab-item>
              <v-tab-item key="timeline">
                <case-timeline-tab />
              </v-tab-item>
            </v-tabs-items>
          </v-tabs>
        </ValidationObserver>
      </v-card>
    </v-col>
  </v-row>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import { ValidationObserver } from "vee-validate"

import ProjectPickerMenu from "@/project/ProjectPickerMenu.vue"
import CaseDetailsTab from "@/case/DetailsTab.vue"
import CaseResourcesTab from "@/case/ResourcesTab.vue"
import CaseTimelineTab from "@/case/TimelineTab.vue"
import CaseTableCondensed from "@/case/TableCondensed.vue"

export default {
  name: "CaseEditSheet",

  components: {
    CaseDetailsTab,
    CaseResourcesTab,
    CaseTimelineTab,
    CaseTableCondensed,
    ProjectPickerMenu,
    ValidationObserver,
  },

  data() {
    return {
      tab: null,
      titleEdit: false,
    }
  },

  computed: {
    ...mapFields("case_management", [
      "selected",
      "selected.id",
      "selected.name",
      "selected.title",
      "selected.project",
      "selected.visibility",
      "selected.reported_at",
      "selected.assignee",
      "selected.status",
      "selected.loading",
      "dialogs.showEditSheet",
    ]),
  },

  created() {
    this.fetchDetails()
  },

  watch: {
    "$route.params.name": function () {
      this.fetchDetails()
    },
  },

  methods: {
    fetchDetails() {
      this.getDetails({ name: this.$route.params.name })
    },
    ...mapActions("case_management", [
      "save",
      "getDetails",
      "closeEditSheet",
      "showEscalateDialog",
    ]),
  },
}
</script>
