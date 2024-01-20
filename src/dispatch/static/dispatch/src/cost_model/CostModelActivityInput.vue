<template>
  <cost-model-activity-dialog @update:model-value="addActivity($event)" />
  <v-container>
    <v-row no-gutter align="center">
      <span class="text-subtitle-1"> Cost Model Activity </span>
      <v-spacer />

      <v-tooltip location="bottom">
        <template #activator="{ props }">
          <v-btn size="small" icon variant="text" @click="createActivityShow()" v-bind="props">
            <v-icon>mdi-plus</v-icon>
          </v-btn>
        </template>
        <span>Add Activity</span>
      </v-tooltip>
    </v-row>
    <span v-for="(activity, activity_idx) in activities" :key="activity_idx">
      <v-row align="center" dense>
        <v-col cols="12" sm="4">
          <v-tooltip location="bottom">
            <template #activator="{ props }">
              <v-btn
                size="small"
                icon
                variant="text"
                @click="removeActivity(activity_idx)"
                v-bind="props"
              >
                <v-icon>mdi-minus</v-icon>
              </v-btn>
            </template>
            <span>Remove Activity</span>
          </v-tooltip>
          <span>
            <v-chip class="short" size="small" :color="project.color">
              {{ activity.plugin_event.plugin.title.substring(0, 20) }}
            </v-chip>
          </span>
        </v-col>

        <v-col cols="12" sm="4">
          <span>
            <v-chip class="short" size="small" :color="project.color">
              {{ activity.plugin_event.name.substring(0, 20) }}
            </v-chip>
          </span>
        </v-col>

        <v-col cols="12" sm="4">
          <v-text-field
            label="Response Time (sec)"
            @update:model-value="itemChanged()"
            v-model="activity.response_time_seconds"
            type="text"
          />
        </v-col>
      </v-row>
    </span>
  </v-container>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import { cloneDeep } from "lodash"
import CostModelActivityDialog from "@/cost_model/CostModelActivityDialog.vue"

export default {
  name: "CostModelActivityInput",

  components: {
    CostModelActivityDialog,
  },
  data() {
    return {}
  },
  props: {
    modelValue: {
      type: Array,
      default: function () {
        return []
      },
    },
  },

  computed: {
    ...mapFields("cost_model", ["selected", "selected.project"]),
    activities: {
      get() {
        return cloneDeep(this.modelValue)
      },
    },
  },

  methods: {
    ...mapActions("cost_model", ["createActivityShow"]),

    addActivity(activity) {
      for (let i = 0; i < this.activities.length; i++) {
        if (this.activities[i].plugin_event.id == activity.plugin_event.id) {
          this.$store.commit(
            "notification_backend/addBeNotification",
            {
              text: "Failed to add cost model activity. Please ensure all plugin events are unique for each cost model.",
            },
            { root: true }
          )
          return
        }
      }
      this.activities.push(cloneDeep(activity))
      this.$emit("update:modelValue", this.activities)
    },
    removeActivity(activity_idx) {
      this.activities.splice(activity_idx, 1)
      this.$emit("update:modelValue", this.activities)
    },
    itemChanged() {
      this.$emit("update:modelValue", this.activities)
    },
  },
}
</script>
