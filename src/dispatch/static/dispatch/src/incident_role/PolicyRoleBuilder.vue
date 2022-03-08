<template>
  <v-card class="grow" elevation="0">
    <v-card-title>
      <v-row>
        <v-col>
          {{ label }}
          <v-tooltip bottom>
            <template v-slot:activator="{ on, attrs }">
              <v-btn icon color="info" v-bind="attrs" v-on="on" @click="add()">
                <v-icon> mdi-playlist-plus </v-icon>
              </v-btn>
            </template>
            <span>Create {{ label }} Policy</span>
          </v-tooltip>
        </v-col>
        <v-col cols="1" align="end">
          <v-tooltip bottom>
            <template v-slot:activator="{ on, attrs }">
              <v-btn icon color="info" v-bind="attrs" v-on="on" :loading="loading" @click="save()">
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
        <draggable
          class="grow"
          v-model="policies"
          @update="onUpdate"
          @start="drag = true"
          @end="drag = false"
        >
          <v-expansion-panel v-for="(policy, idx) in policies" :key="policy.id">
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
                    <tag-filter-auto-complete
                      label="Tags"
                      :project="project"
                      v-model="policy.tags"
                    />
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
                    <service-select-new
                      label="Target Service"
                      :project="project"
                      v-model="policy.service"
                    ></service-select-new>
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
                <v-list-item>
                  <v-list-item-content>
                    <v-btn color="primary" @click="remove(idx)"> Delete Policy </v-btn>
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
import draggable from "vuedraggable"

import IncidentRoleApi from "@/incident_role/api"

import IncidentTypeCombobox from "@/incident_type/IncidentTypeCombobox.vue"
import IncidentPriorityCombobox from "@/incident_priority/IncidentPriorityCombobox.vue"
import TagFilterAutoComplete from "@/tag/TagFilterAutoComplete.vue"
import ServiceSelectNew from "@/service/ServiceSelectNew.vue"

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
    TagFilterAutoComplete,
    ServiceSelectNew,
  },

  data() {
    return {
      policies: [],
      loading: false,
    }
  },

  methods: {
    add: function () {
      this.policies.push({
        role: this.label,
        project: this.project,
        enabled: false,
        service: null,
        incident_priorities: [],
        incident_types: [],
        tags: [],
      })
    },
    remove: function (idx) {
      this.policies.splice(idx, 1)
    },
    save: function () {
      this.loading = true
      IncidentRoleApi.updateRole(this.label, this.project.name, { policies: this.policies })
        .then((response) => {
          this.$store.commit(
            "notification_backend/addBeNotification",
            { text: "Role policies successfully updated.", type: "success" },
            { root: true }
          )
          this.policies = response.data.policies
        })
        .finally(() => {
          this.loading = false
        })
    },
    get: function () {
      IncidentRoleApi.getRolePolicies(this.label, this.project.name).then((response) => {
        this.policies = response.data.policies
      })
    },
    onUpdate() {
      // update the order attr
      this.policies.forEach((policy, idx) => {
        policy.order = idx + 1
      })
    },
  },

  created() {
    this.get()
    this.$watch(
      (vm) => [vm.project],
      () => {
        this.get()
      }
    )
  },
}
</script>
