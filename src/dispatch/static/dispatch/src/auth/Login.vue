<template>
  <ValidationObserver v-slot="{ invalid, validated }">
    <v-card class="mx-auto ma-4" max-width="600" flat outlined :loading="loading">
      <v-card-title> Login </v-card-title>
      <v-card-text>
        <v-container>
          <v-row>
            <v-col cols="12" md="12">
              <ValidationProvider name="Email" rules="required|email" immediate>
                <v-text-field
                  v-model="email"
                  label="Email"
                  slot-scope="{ errors, valid }"
                  :error-messages="errors"
                  :success="valid"
                />
              </ValidationProvider>
            </v-col>
            <v-col cols="12" md="12">
              <ValidationProvider name="Password" rules="required" immediate>
                <v-text-field
                  v-model="password"
                  :type="'password'"
                  label="Password"
                  slot-scope="{ errors, valid }"
                  :error-messages="errors"
                  :success="valid"
                />
              </ValidationProvider>
            </v-col>
          </v-row>
        </v-container>
      </v-card-text>
      <v-card-actions>
        <v-list-item two-line>
          <v-list-item-content v-if="registrationEnabled">
            <v-list-item-subtitle>
              Don't have a account?
              <router-link :to="{ name: 'BasicRegister' }"> Register </router-link>
            </v-list-item-subtitle>
          </v-list-item-content>
          <v-row align="center" justify="end">
            <v-btn
              color="info"
              :loading="loading"
              :disabled="invalid || !validated"
              @click="basicLogin({ email: email, password: password })"
            >
              Login
              <template v-slot:loader>
                <v-progress-linear indeterminate color="white" />
              </template>
            </v-btn>
          </v-row>
        </v-list-item>
      </v-card-actions>
    </v-card>
  </ValidationObserver>
</template>

<script>
import { mapActions } from "vuex"
import { mapFields } from "vuex-map-fields"
import { ValidationObserver, ValidationProvider, extend } from "vee-validate"
import { required, email } from "vee-validate/dist/rules"
const registrationEnabled =
  import.meta.env.VITE_DISPATCH_AUTH_REGISTRATION_ENABLED === "false" ? false : true

extend("email", email)

extend("required", {
  ...required,
  message: "This field is required",
})

export default {
  components: {
    ValidationProvider,
    ValidationObserver,
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
