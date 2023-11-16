<template>
  <v-form @submit.prevent="basicLogin({ email, password })" v-slot="{ isValid }">
    <v-card class="mx-auto ma-4" max-width="600" variant="outlined" :loading="loading">
      <v-card-title> Login </v-card-title>
      <v-card-text>
        <v-container>
          <v-row>
            <v-col cols="12" md="12">
              <v-text-field
                v-model="email"
                label="Email"
                name="Email"
                :rules="[rules.required, rules.email]"
              />
            </v-col>
            <v-col cols="12" md="12">
              <v-text-field
                v-model="password"
                type="password"
                label="Password"
                name="Password"
                :rules="[rules.required]"
              />
            </v-col>
          </v-row>
        </v-container>
      </v-card-text>
      <v-card-actions>
        <div v-if="registrationEnabled" class="text-subheader-2 pl-4 text-medium-emphasis">
          Don't have a account?
          <router-link :to="{ name: 'BasicRegister' }"> Register </router-link>
        </div>
        <v-spacer />
        <v-btn
          type="submit"
          color="info"
          variant="elevated"
          :loading="loading"
          :disabled="!isValid.value"
        >
          Login
          <template #loader>
            <v-progress-linear indeterminate color="white" />
          </template>
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-form>
</template>

<script>
import { required, email } from "@/util/form"
import { mapActions } from "vuex"
import { mapFields } from "vuex-map-fields"

const registrationEnabled =
  import.meta.env.VITE_DISPATCH_AUTH_REGISTRATION_ENABLED === "false" ? false : true

export default {
  setup() {
    return {
      rules: { required, email },
    }
  },
  data() {
    return {
      email: "",
      password: "",
      registrationEnabled: registrationEnabled,
    }
  },
  computed: {
    ...mapFields("auth", ["loading"]),
  },
  methods: {
    ...mapActions("auth", ["basicLogin"]),
  },
}
</script>

<style scoped></style>
