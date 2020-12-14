<template>
  <div class="pl-5">
    <div v-if="status == 'Active'">
      <v-tooltip bottom>
        <template v-slot:activator="{ on, attrs }">
          <v-badge bordered color="error" slot="activator" dot left offset-x="-10" offset-y="12">
            {{ status }}
            <v-btn icon x-small v-bind="attrs" v-on="on" @click="joinIncident(id)">
              <v-icon>
                person_addded
              </v-icon>
            </v-btn>
          </v-badge>
        </template>
        <span>Join Incident</span>
      </v-tooltip>
    </div>
    <div v-if="status == 'Stable'" class="mr-10">
      <v-badge bordered color="warning" slot="activator" dot left offset-x="-10" offset-y="12">
        {{ status }}
      </v-badge>
      <v-tooltip bottom>
        <template v-slot:activator="{ on, attrs }">
          <v-btn icon v-bind="attrs" v-on="on" @click="joinIncident(id)">
            <v-icon>
              mdi-account-plus
            </v-icon>
          </v-btn>
        </template>
        <span>Join Incident</span>
      </v-tooltip>
    </div>
    <div v-if="status == 'Closed'">
      <v-badge bordered color="success" dot left offset-x="-10" offset-y="12">
        {{ status }}
      </v-badge>
    </div>
  </div>
</template>

<script>
import { mapActions } from "vuex"

export default {
  name: "IncidentStatus",

  props: {
    status: {
      type: String,
      required: true
    },
    id: {
      type: Number,
      required: true
    }
  },

  methods: {
    ...mapActions("incident", ["joinIncident"])
  }
}
</script>
