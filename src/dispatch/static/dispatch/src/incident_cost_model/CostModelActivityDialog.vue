<template>
  <v-dialog v-model="showActivity" persistent max-width="800px" return-object>
    <v-form ref="form" v-model="valid">
      <v-card>
        <v-card-title>
          <v-list-item lines="two">
            <v-list-item-title class="text-h6"> New </v-list-item-title>
            <v-list-item-subtitle>Incident Cost Model Activity </v-list-item-subtitle>
          </v-list-item>
        </v-card-title>
        <v-card-text>
          <v-container>
            <div>Assign the response time for a given plugin event.</div>
          </v-container>
        </v-card-text>
        <v-card-text>
          <v-spacer />
          <v-row align="center" dense>
            <v-col cols="12" sm="4">
              <v-tooltip location="bottom" text="idk">
                <template #activator="{ props }">
                  <plugin-instance-combobox
                    :model-value="plugin"
                    @update:model-value="setPlugin($event)"
                    :project="project"
                    label="Plugin"
                    required
                    v-bind="props"
                  />
                </template>

                <span>Select Plugin</span>
              </v-tooltip>
            </v-col>

            <v-col cols="12" sm="5">
              <v-tooltip location="bottom">
                <template #activator="{ props }">
                  <span v-bind="props">
                    <plugin-event-combobox
                      :model-value="event"
                      @update:model-value="setPluginEvent($event)"
                      :plugin="plugin"
                      label="Plugin Event"
                      :disabled="!plugin"
                      required
                      :rules="[required_valid_plugin_event]"
                    />
                  </span>
                </template>

                <span v-if="plugin">Select Plugin Events</span>
                <span v-else>Please select a plugin first.</span>
              </v-tooltip>
            </v-col>

            <v-col cols="12" sm="2">
              <v-tooltip location="bottom">
                <template #activator="{ props }">
                  <v-text-field
                    v-model="response_time_seconds"
                    label="Response Time (sec)"
                    type="number"
                    placeholder="90"
                    clearable
                    required
                    min="1"
                    name="Reminder Interval"
                    v-bind="props"
                    :rules="[required_positive_int]"
                  />
                </template>

                <span> Activity effort measured in number of seconds. </span>
              </v-tooltip>
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn color="blue en-1" variant="text" @click="cancel()"> Cancel </v-btn>
          <v-btn color="red en-1" variant="text" @click="addCostModelActivity()" :disabled="!valid">
            Add Activity
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-form>
  </v-dialog>
</template>

<script>
import { mapActions } from "vuex"
import { mapFields } from "vuex-map-fields"
import PluginInstanceCombobox from "@/plugin/PluginInstanceCombobox.vue"
import PluginEventCombobox from "@/plugin/PluginEventCombobox.vue"

export default {
  name: "IncidentCostModelActivityDialog",
  components: {
    PluginInstanceCombobox,
    PluginEventCombobox,
  },

  data() {
    return {
      enabled: true,
      event: null,
      plugin: null,
      response_time_seconds: 300,
      valid: false,
      required_positive_int: (value) => {
        if (!value || value.length == 0) {
          return "This field is required."
        }
        if (value && value <= 0) {
          return "This field must be greater than 0."
        }
        return true
      },
      required_valid_plugin_event: (value) => {
        if (!value || value.length == 0) {
          return "This field is required."
        }
        if (!value.name) {
          return "Please select a valid plugin event"
        }
        return true
      },
    }
  },
  props: {
    modelValue: {
      type: Object,
      default: function () {
        return {}
      },
    },
    type: {
      type: String,
      default: null,
    },
  },
  computed: {
    ...mapFields("incident_cost_model", ["dialogs.showActivity", "selected.project"]),
  },
  methods: {
    ...mapActions("incident_cost_model", ["closeActivity", "save"]),

    addCostModelActivity() {
      let activity = {
        enabled: this.enabled,
        event: this.event,
        response_time_seconds: this.response_time_seconds,
      }

      this.$emit("update:modelValue", activity)
      this.closeActivity()
    },
    cancel() {
      this.closeActivity()
    },
    setPlugin(plugin) {
      this.event = null
      this.plugin = plugin
    },
    setPluginEvent(event) {
      this.event = event
    },
  },
}
</script>
