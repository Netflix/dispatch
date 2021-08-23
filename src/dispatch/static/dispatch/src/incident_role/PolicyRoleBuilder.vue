<template>
  <v-card class="grow" elevation="0">
    <v-card-title>
      <v-row>
        <v-col>
          {{ label }}
          <v-tooltip bottom>
            <template v-slot:activator="{ on, attrs }">
              <v-btn icon color="info" v-bind="attrs" v-on="on" @click="addPolicy()">
                <v-icon> mdi-playlist-plus </v-icon>
              </v-btn>
            </template>
            <span>Create {{ label }} Policy</span>
          </v-tooltip>
        </v-col>
        <v-col cols="1" align="end">
          <v-tooltip bottom>
            <template v-slot:activator="{ on, attrs }">
              <v-btn icon color="info" v-bind="attrs" v-on="on" @click="savePolicies()">
                <v-icon> save </v-icon>
              </v-btn>
            </template>
            <span>Save {{ label }} Policies</span>
          </v-tooltip>
        </v-col>
      </v-row>
    </v-card-title>
    <v-card-text v-if="policies.length">
      <v-expansion-panels>
        <draggable class="grow" v-model="policies" @start="drag = true" @end="drag = false">
          <v-expansion-panel v-for="policy in policies" :key="policy.id">
            <v-expansion-panel-header>
              <v-row align="center" justify="center">
                <v-col cols="1">
                  <v-icon> mdi-drag-horizontal-variant </v-icon>
                </v-col>
                <v-col cols="1">
                  <v-chip v-if="policy.enabled" dark color="green" small label>Enabled</v-chip>
                  <v-chip v-if="!policy.enabled" dark small label>Disabled</v-chip>
                </v-col>
                <v-col>
                  {{ policy.role }} - <span v-if="policy.service">{{ policy.service.name }}</span>
                </v-col>
              </v-row>
            </v-expansion-panel-header>
            <v-expansion-panel-content>
              <v-list dense>
                <v-list-item>
                  <v-list-item-content>
                    <tag-filter-combobox label="Tags" :project="project" v-model="policy.tags" />
                  </v-list-item-content>
                </v-list-item>
                <v-list-item>
                  <v-list-item-content>
                    <incident-priority-combobox
                      :project="project"
                      v-model="policy.incident_priorities"
                    />
                  </v-list-item-content>
                </v-list-item>
                <v-list-item>
                  <v-list-item-content>
                    <incident-type-combobox :project="project" v-model="policy.incident_types" />
                  </v-list-item-content>
                </v-list-item>
                <v-list-item>
                  <v-list-item-content>
                    <service-select
                      label="Target Service"
                      :project="project"
                      v-model="policy.service"
                    ></service-select>
                  </v-list-item-content>
                </v-list-item>
                <v-list-item>
                  <v-list-item-content>
                    <v-checkbox
                      v-model="policy.enabled"
                      label="Enabled"
                      hint="Check this if you would like this policy to be considered when resolving the role."
                    />
                  </v-list-item-content>
                </v-list-item>
              </v-list>
            </v-expansion-panel-content>
          </v-expansion-panel>
        </draggable>
      </v-expansion-panels>
    </v-card-text>
    <v-card-text v-else>
      <v-row justify="center"> No {{ label }} policies have been defined. </v-row>
    </v-card-text>
  </v-card>
</template>

<script>
import { cloneDeep } from "lodash"
import draggable from "vuedraggable"

import IncidentTypeCombobox from "@/incident_type/IncidentTypeCombobox.vue"
import IncidentPriorityCombobox from "@/incident_priority/IncidentPriorityCombobox.vue"
import TagFilterCombobox from "@/tag/TagFilterCombobox.vue"
import ServiceSelect from "@/service/ServiceSelect.vue"

export default {
  name: "RolePolicyBuilder",

  props: {
    value: {
      type: Array,
      default: function () {
        return []
      },
    },
    label: {
      type: String,
      default: null,
    },
    project: {
      type: [Object],
      default: null,
    },
  },

  components: {
    draggable,
    IncidentTypeCombobox,
    IncidentPriorityCombobox,
    TagFilterCombobox,
    ServiceSelect,
  },

  computed: {
    policies: {
      get() {
        return cloneDeep(this.value)
      },
    },
  },

  methods: {
    addPolicy: function () {
      this.policies.push({ role: this.label })
    },
  },
}
</script>
