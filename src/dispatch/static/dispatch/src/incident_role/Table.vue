<style scoped>
.v-expansion-panel--active::before {
  background-color: #e50914;
  display: block;
  content: "";
  position: absolute;
  top: 6px;
  bottom: 6px;
  left: -8px;
  width: 5px;
  opacity: 0.5 !important;
  border-radius: 0px 3px 3px 0px;
  transition: background-color 0.15s linear 0s;
}
</style>
<template>
  <v-layout wrap>
    <delete-dialog />
    <v-container>
      <v-row align="center" justify="space-between">
        <v-col class="grow">
          <settings-breadcrumbs v-model="breadCrumbProject" />
        </v-col>
        <v-col class="shrink">
          <v-btn color="info" class="mr-2" @click="createEditShow()"> New </v-btn>
        </v-col>
        <v-col class="shrink">
          <v-btn color="info" class="mr-2" @click="createEditShow()"> Save </v-btn>
        </v-col>
      </v-row>
      <v-row>
        <v-card class="grow" :loading="loading">
          <v-expansion-panels>
            <draggable class="grow" v-model="items" @start="drag = true" @end="drag = false">
              <v-expansion-panel v-for="policy in items" :key="policy.id">
                <v-expansion-panel-header>
                  <v-row align="center" justify="center">
                    <v-col cols="1">
                      <v-icon> mdi-drag-horizontal-variant </v-icon>
                    </v-col>
                    <v-col> {{ policy.role }} - {{ policy.service.name }} </v-col>
                  </v-row>
                </v-expansion-panel-header>
                <v-expansion-panel-content>
                  <v-container grid-list-md>
                    <v-layout wrap>
                      <v-flex xs12>
                        <v-select
                          label="Role Type"
                          v-model="policy.role"
                          :items="incidentRoleTypes"
                        />
                      </v-flex>
                      <v-flex xs12>
                        <tag-filter-combobox
                          label="Tags"
                          :project="project"
                          v-model="policy.tags"
                        />
                      </v-flex>
                      <v-flex xs12>
                        <incident-priority-combobox
                          :project="project"
                          v-model="policy.incident_priorities"
                        />
                      </v-flex>
                      <v-flex xs12>
                        <incident-type-combobox
                          :project="project"
                          v-model="policy.incident_types"
                        />
                      </v-flex>
                      <v-flex xs12>
                        <service-select
                          label="Target Service"
                          :project="project"
                          v-model="policy.service"
                        ></service-select>
                      </v-flex>
                      <v-flex xs12>
                        <v-checkbox
                          v-model="policy.enabled"
                          label="Enabled"
                          hint="Check this if you would like this policy to be considered when resolving the role."
                        />
                      </v-flex>
                    </v-layout>
                  </v-container>
                </v-expansion-panel-content>
              </v-expansion-panel>
            </draggable>
          </v-expansion-panels>
        </v-card>
      </v-row>
    </v-container>
  </v-layout>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import draggable from "vuedraggable"

import IncidentTypeCombobox from "@/incident_type/IncidentTypeCombobox.vue"
import IncidentPriorityCombobox from "@/incident_priority/IncidentPriorityCombobox.vue"
import TagFilterCombobox from "@/tag/TagFilterCombobox.vue"
import ServiceSelect from "@/service/ServiceSelect.vue"

import SettingsBreadcrumbs from "@/components/SettingsBreadcrumbs.vue"
import DeleteDialog from "@/incident_role/DeleteDialog.vue"

export default {
  name: "IncidentCostTypeTable",

  components: {
    draggable,
    DeleteDialog,
    IncidentTypeCombobox,
    IncidentPriorityCombobox,
    TagFilterCombobox,
    ServiceSelect,
    SettingsBreadcrumbs,
  },

  data() {
    return {
      incidentRoleTypes: ["Incident Commander", "Liasion", "Scribe"],
    }
  },

  computed: {
    ...mapFields("incident_role", ["table.rows.items", "table.loading"]),
    ...mapFields("route", ["query"]),
  },

  created() {
    this.breadCrumbProject = [{ name: this.query.project }]
    this.project = { name: this.query.project }

    this.getAll()

    this.$watch(
      (vm) => [vm.page],
      () => {
        this.getAll()
      }
    )

    this.$watch(
      (vm) => [vm.breadCrumbProject],
      () => {
        this.page = 1
        this.$router.push({ query: { project: this.breadCrumbProject[0].name } })
        this.getAll()
      }
    )
  },

  methods: {
    ...mapActions("incident_role", ["getAll"]),
  },
}
</script>
