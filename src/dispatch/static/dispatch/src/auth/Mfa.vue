<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="6" lg="4">
        <v-card class="elevation-12">
          <v-card-title class="text-center text-h5 py-4">
            Multi-Factor Authentication
          </v-card-title>
          <v-card-text>
            <div class="text-center">
              <!-- Show spinner while loading -->
              <v-progress-circular
                v-if="loading"
                indeterminate
                color="primary"
                size="64"
                class="mb-4"
              ></v-progress-circular>

              <!-- Status message with icon -->
              <v-alert
                v-if="status"
                :type="alertType"
                :icon="statusIcon"
                class="mb-4"
                border="left"
              >
                {{ statusMessage }}
              </v-alert>

              <!-- Retry button only shown when denied or expired -->
              <v-btn v-if="canRetry" color="primary" @click="verifyMfa" :loading="loading">
                Retry Verification
              </v-btn>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue"
import { useRoute } from "vue-router"
import authApi from "@/auth/api"

/* eslint-disable no-unused-vars */
enum MfaChallengeStatus {
  PENDING = "pending",
  APPROVED = "approved",
  DENIED = "denied",
  EXPIRED = "expired",
}

const route = useRoute()
const status = ref<MfaChallengeStatus | null>(null)
const loading = ref(false)

const statusMessage = computed(() => {
  switch (status.value) {
    case MfaChallengeStatus.APPROVED:
      return "MFA verification successful. This window will close shortly."
    case MfaChallengeStatus.DENIED:
      return "MFA verification denied. Please try again."
    case MfaChallengeStatus.EXPIRED:
      return "MFA challenge has expired. Please request a new one."
    case MfaChallengeStatus.PENDING:
      return "Verifying your authentication..."
    case null:
      return "Initializing verification..."
    default:
      return "An unknown error occurred."
  }
})

const statusIcon = computed(() => {
  switch (status.value) {
    case MfaChallengeStatus.APPROVED:
      return "mdi-check-circle"
    case MfaChallengeStatus.DENIED:
      return "mdi-close-circle"
    case MfaChallengeStatus.EXPIRED:
      return "mdi-clock-alert"
    case MfaChallengeStatus.PENDING:
      return "mdi-progress-clock"
    default:
      return "mdi-alert"
  }
})

const alertType = computed(() => {
  switch (status.value) {
    case MfaChallengeStatus.APPROVED:
      return "success"
    case MfaChallengeStatus.DENIED:
    case MfaChallengeStatus.EXPIRED:
      return "error"
    case MfaChallengeStatus.PENDING:
    case null:
      return "info"
    default:
      return "warning"
  }
})

const canRetry = computed(() => {
  return status.value === MfaChallengeStatus.DENIED || status.value === MfaChallengeStatus.EXPIRED
})

const verifyMfa = async () => {
  loading.value = true
  status.value = MfaChallengeStatus.PENDING

  try {
    const challengeId = route.query.challenge_id as string
    const projectId = parseInt(route.query.project_id as string)
    const action = route.query.action as string

    if (!challengeId || !projectId || !action) {
      throw new Error("Missing required parameters")
    }

    const response = await authApi.verifyMfa({
      challenge_id: challengeId,
      project_id: projectId,
      action: action,
    })

    status.value = response.data.status as MfaChallengeStatus
    if (status.value === MfaChallengeStatus.APPROVED) {
      setTimeout(() => window.close(), 5000) // Close window after 5 seconds
    }
  } catch (error) {
    console.error("MFA verification failed:", error)
    status.value = MfaChallengeStatus.DENIED
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  verifyMfa()
})
</script>
