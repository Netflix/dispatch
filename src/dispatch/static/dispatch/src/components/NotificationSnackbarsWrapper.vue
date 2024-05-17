<template>
  <v-snackbar
    v-model="notification.show"
    :timeout="notification.timeout"
    :color="notification.type"
    @update:model-value="setSeen(notification.index)"
  >
    <span class="text-center">{{ notification.text }}</span>
  </v-snackbar>
</template>

<script>
import { mapActions } from "vuex"
import { mapFields } from "vuex-map-fields"

export default {
  name: "NotificationSnackbarsWrapper",

  computed: {
    ...mapFields("notification_backend", ["notifications"]),
    notificationQueue: function () {
      const indexed = this.notifications.map((o, i) => {
        return {
          index: i,
          ...o,
        }
      })
      return indexed.filter((o) => o.show === true)
    },
    queueLength: function () {
      return this.notificationQueue.length
    },
    hasPending: function () {
      return this.queueLength > 0
    },
  },

  watch: {
    notificationQueue: {
      deep: true,
      handler: function () {
        if (!this.notification.show && this.hasPending) {
          const newNot = this.notificationQueue.shift()
          this.$nextTick(() => (this.notification = { ...newNot }))
        }
      },
    },
  },

  data() {
    return {
      notification: {},
    }
  },

  created() {
    this.reset()
  },

  methods: {
    ...mapActions("notification_backend", [
      "removeBackendNotification",
      "setBackendNotificationSeen",
    ]),
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
        timeout: undefined,
      }
    },
    showNext() {
      if (!this.notification.show && this.hasPending) {
        const newNot = this.notificationQueue.shift()
        this.$nextTick(() => (this.notification = { ...newNot }))
      } else {
        this.reset()
      }
    },
  },
}
</script>

<style scoped>
.text-center {
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
