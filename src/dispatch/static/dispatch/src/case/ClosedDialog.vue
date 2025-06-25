<template>
  <v-dialog v-model="showClosedDialog" persistent max-width="800px">
    <v-card>
      <v-card-title>
        <span class="text-h5">Close Cases</span>
      </v-card-title>
      <v-card-text>
        Closed cased require a resolution reason and a resolution summary.
      </v-card-text>
      <v-card-actions>
        <v-container>
          <v-row>
            <v-col cols="12" sm="6">
              <v-select
                v-model="resolutionReason"
                label="Resolution Reason"
                :items="$store.state.case_management.resolutionReasons"
                hint="The general reason why a given case was resolved."
                :menu-props="{ contentClass: 'resolution-menu' }"
              >
                <template #item="{ item, props }">
                  <v-list-item v-bind="props">
                    <template #title>
                      <div class="d-flex align-center justify-space-between">
                        {{ item.title }}
                        <v-tooltip location="right">
                          <template #activator="{ props: tooltipProps }">
                            <v-icon
                              v-bind="tooltipProps"
                              icon="mdi-information"
                              size="small"
                              class="ml-2"
                            />
                          </template>
                          <span>{{
                            $store.state.case_management.resolutionTooltips[item.title]
                          }}</span>
                        </v-tooltip>
                      </div>
                    </template>
                  </v-list-item>
                </template>
              </v-select>
            </v-col>
            <v-col cols="12">
              <v-textarea
                v-model="resolution"
                label="Resolution"
                hint="Description of the actions taken to resolve the case."
                clearable
              />
            </v-col>
            <v-btn color="blue en-1" variant="text" @click="closeClosedDialog()"> Cancel </v-btn>
            <v-btn
              color="red en-1"
              variant="text"
              :loading="loading"
              @click="
                saveBulk({
                  resolution_reason: resolutionReason,
                  resolution: resolution,
                  status: 'Closed',
                })
              "
            >
              Close
            </v-btn>
          </v-row>
        </v-container>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

export default {
  name: "CaseClosedDialog",

  data() {
    return {
      resolutionReason: "False Positive",
      resolution: "Description of the actions taken to resolve the case.",
    }
  },

  computed: {
    ...mapFields("case_management", [
      "dialogs.showClosedDialog",
      "selected.loading",
      "selected.project",
    ]),
  },

  methods: {
    ...mapActions("case_management", ["closeClosedDialog", "saveBulk", "resetSelected"]),
  },
}
</script>

<style scoped>
.resolution-menu {
  max-width: 300px;
}

:deep(.v-list-item) {
  padding: 8px 16px;
}

:deep(.v-select__content) {
  max-width: 300px;
}

/* Lighten tooltip info icons */
:deep(.v-tooltip .v-icon) {
  color: #cccccc !important;
}

/* Alternative approach - target the icon directly */
:deep(.mdi-information) {
  color: #b0b0b0 !important;
}
</style>
