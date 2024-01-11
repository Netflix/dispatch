<template>
  <v-form @submit.prevent="register({ email, password })" v-slot="{ isValid }">
    <v-card class="mx-auto ma-4" variant="outlined" max-width="600" flat :loading="loading">
      <v-card-title> Register </v-card-title>
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
        <div class="text-subheader-2 pl-4 text-medium-emphasis">
          Have an account? <router-link :to="{ name: 'BasicLogin' }"> Login </router-link>
        </div>
        <v-spacer />
        <v-btn
          type="submit"
          variant="elevated"
          color="info"
          :loading="loading"
          :disabled="!isValid.value"
        >
          Register
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
    }
  },
  computed: {
    ...mapFields("auth", ["loading"]),
  },
  methods: {
    ...mapActions("auth", ["register"]),
  },
}
</script>

<style scoped></style>
