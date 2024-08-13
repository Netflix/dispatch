<template>
  <div>
    <h1>MFA Flow</h1>
    <p v-if="status">Status: {{ status }}</p>
    <button @click="verifyMfa" :disabled="status === 'approved'">Verify MFA</button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue"
import { useRoute, useRouter } from "vue-router"
import { useStore } from "vuex"
import authApi from "@/auth/api"

const route = useRoute()
const router = useRouter()
const store = useStore()

const status = ref<string | null>(null)

// Get the current user's ID from the Vuex store
const currentUserEmail = computed(() => store.state.auth.currentUser)

const verifyMfa = async () => {
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
      user_id: 12480, // TODO(whsel): fetch this
    })

    status.value = response.status
    if (response.status === "approved") {
      // Redirect to appropriate page or close the window
      window.close()
    }
  } catch (error) {
    console.error("MFA verification failed:", error)
    status.value = "error"
  }
}

onMounted(() => {
  // You can auto-verify if needed
  // verifyMfa()
})
</script>
