<template>
  <v-snackbar
    v-model="notification.show"
    :timeout="notification.timeout"
    :color="notification.type"
    @input="setSeen(notification.index)"
  >
    {{ notification.text }}
    <v-btn text @click="setSeen(notification.index)">Close</v-btn>
    <!--<template v-slot:action="{ attrs }">
      <v-btn text left v-bind="attrs" @click="remove(notification.index)">Delete</v-btn>
      <v-badge :value="queueLength > 1" :content="queueLength">
        <v-btn text v-bind="attrs" @click="setSeen(notification.index)">Close</v-btn>
      </v-badge>
    </template>-->
  </v-snackbar>
</template>

<script>
import { mapActions } from "vuex"
import { mapFields } from "vuex-map-fields"

export default {
  name: "NotificationSnackbarsWrapper",

  computed: {
    ...mapFields("notification", ["backendNotifications"]),
    notificationQueue: function() {
      const indexed = this.backendNotifications.map((o, i) => {
        return {
          index: i,
          ...o
        }
      })
      return indexed.filter(o => o.show === true)
    },
    queueLength: function() {
      return this.notificationQueue.length
    },
    hasPending: function() {
      return this.queueLength > 0
    }
  },

  watch: {
    notificationQueue: {
      deep: true,
      handler: function() {
        if (!this.notification.show && this.hasPending) {
          const newNot = this.notificationQueue.shift()
          this.$nextTick(() => (this.notification = { ...newNot }))
        }
      }
    }
  },

  data() {
    return {
      notification: {}
    }
  },

  created() {
    this.reset()
  },

  methods: {
    ...mapActions("notification", ["removeBackendNotification", "setBackendNotificationSeen"]),
    setSeen(i) {
      this.showNext()
      this.setBackendNotificationSeen(i)
    },
    remove(i) {
      this.setSeen(i)
      this.removeBackendNotification(i)
    },
    reset() {
      this.notification = {
        message: "",
        show: false,
        type: "",
        index: -1,
        timeout: undefined
      }
    },
    showNext() {
      if (!this.notification.show && this.hasPending) {
        const newNot = this.notificationQueue.shift()
        this.$nextTick(() => (this.notification = { ...newNot }))
      } else {
        this.reset()
      }
    }
  }
}
</script>
