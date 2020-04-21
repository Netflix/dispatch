<template>
  <div class="container">
    <v-card>
      <v-card-title>
        Login
      </v-card-title>
      <v-card-text>
        <v-form>
          <v-container>
            <v-row>
              <v-col cols="12" md="12">
                <v-text-field v-model="email" label="E-mail" required> </v-text-field>
              </v-col>
              <v-col cols="12" md="12">
                <v-text-field
                  v-model="password"
                  :type="'password'"
                  label="Password"
                  required
                ></v-text-field>
              </v-col>
            </v-row>
            <p>Don't have a account? <a href="/register">Sign In</a></p>
          </v-container>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-btn color="primary" outlined @click="loginUser">Login</v-btn>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script>
import { mapFields } from "vuex-map-fields"

export default {
  methods: {
    loginUser: function() {
      this.$store.dispatch("account/basicLogin")
    }
  },
  computed: {
    ...mapFields("account", ["creds.email", "creds.password"])
  },
  mounted: function() {
    let token = localStorage.getItem("token")
    if (token) {
      this.$store.dispatch("account/loginWithToken", token)
    }
  }
}
</script>

<style scoped></style>
