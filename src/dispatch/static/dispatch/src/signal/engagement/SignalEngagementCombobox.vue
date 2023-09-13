<template>
  <v-row no-gutters align="center">
    <v-col cols="12" sm="11">
      <base-combobox
        :value="value"
        :label="label"
        :api="signalEngagementApi"
        :project="project"
        v-model="engagements"
      >
        <template #selection="{ attr, item, selected }">
          <v-menu origin="overlap">
            <template #activator="{ props }">
              <v-chip
                v-bind="props"
                :model-value="selected"
                pill
                closable
                @click:close="remove(item)"
              >
                {{ item ? item.name : "Unknown" }}
              </v-chip>
            </template>
            <v-card>
              <v-list dark>
                <v-list-item>
                  <v-list-item-avatar color="teal">
                    <span class="text-white">{{ initials(item) }}</span>
                  </v-list-item-avatar>

                  <v-list-item-title>{{ item ? item.name : "Unknown" }}</v-list-item-title>
                  <v-list-item-subtitle>{{ item ? item.type : "Unknown" }}</v-list-item-subtitle>

                  <v-list-item-action>
                    <v-btn icon variant="text">
                      <v-icon>mdi-close-circle</v-icon>
                    </v-btn>
                  </v-list-item-action>
                </v-list-item>
              </v-list>
              <v-list>
                <v-list-item>
                  <v-list-item-action>
                    <v-icon>mdi-text-box</v-icon>
                  </v-list-item-action>
                  <v-list-item-subtitle>
                    {{ item ? item.description : "Unknown" }}
                  </v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-card>
          </v-menu>
        </template>
      </base-combobox>
    </v-col>
    <v-col cols="12" sm="1">
      <signal-engagement-create-dialog
        v-model="createdItem"
        :project="project"
        :signalDefinition="signalDefinition"
      />
    </v-col>
  </v-row>
</template>

<script>
import BaseCombobox from "@/components/BaseCombobox.vue"
import SignalEngagementApi from "@/signal/engagement/api"
import SignalEngagementCreateDialog from "@/signal/engagement/SignalEngagementCreateDialog.vue"

export default {
  name: "SignalEngagementCombobox",
  components: {
    BaseCombobox,
    SignalEngagementCreateDialog,
  },
  props: {
    value: {
      type: Array,
      default: () => [],
    },
    label: {
      type: String,
      default: "Add Engagment(s)",
    },
    project: {
      type: Object,
      required: true,
    },
    signalDefinition: {
      type: Object,
      required: false,
    },
  },
  data() {
    return {
      signalEngagementApi: SignalEngagementApi,
      createdItem: null,
      items: [],
    }
  },
  computed: {
    engagements: {
      get() {
        return this.value
      },
      set(value) {
        this.$emit("input", value)
      },
    },
  },

  watch: {
    createdItem: function (newVal) {
      this.items.push(newVal)
      this.engagements.push(newVal)
    },
  },

  methods: {
    // ...
    initials(item) {
      if (!item) {
        return "Unknown"
      }
      return this.$options.filters.initials(item.name)
    },
    remove(item) {
      this.engagements.splice(this.engagements.indexOf(item), 1)
    },
  },
}
</script>
