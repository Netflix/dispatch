<template>
  <v-card class="mx-auto" max-width="500" style="margin-top: -64px;">
    <v-card-title>
      Dispatch - Register
    </v-card-title>
    <v-card-text>
      <v-form>
        <v-container>
          <v-row>
            <v-col cols="12" md="12">
              <v-text-field v-model="email" label="Email" required> </v-text-field>
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
        </v-container>
      </v-form>
    </v-card-text>
    <v-card-actions>
      <v-list-item two-line>
        <v-list-item-content>
          <v-list-item-subtitle>
            Have a account? <router-link to="/login">Login</router-link>
          </v-list-item-subtitle>
        </v-list-item-content>
        <v-row align="center" justify="end">
          <v-btn color="primary" v-on:click="registerUser">Register</v-btn>
        </v-row>
      </v-list-item>
    </v-card-actions>
  </v-card>
</template>

<script>
import { mapFields } from "vuex-map-fields"

export default {
  methods: {
    registerUser: function() {
      this.$store.dispatch("account/register")
    }
  },
  computed: {
    ...mapFields("account", ["creds.email", "creds.password"])
  }
}
</script>

<style scoped></style>
