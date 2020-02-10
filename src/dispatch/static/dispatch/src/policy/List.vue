<template>
  <v-layout wrap>
    <div class="headline">
      Services
    </div>
    <v-spacer />
    <div class="subtile">
      More
    </div>
    <v-flex xs12>
      <v-layout column>
        <v-flex>
          <v-list
            two-line
            class="elevation-2"
          >
            <v-layout
              v-for="item in items"
              :key="item.content.id"
            >
              <v-flex xs3>
                <v-list-item>
                  <v-list-item-action>
                    <v-icon>fingerprint</v-icon>
                  </v-list-item-action>
                  <v-list-item-content>
                    <v-list-item-title>{{ item.content.name }}</v-list-item-title>
                    <v-list-item-subtitle>Name</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
              </v-flex>
              <v-flex xs3>
                <v-list-item>
                  <v-list-item-action>
                    <v-icon>build</v-icon>
                  </v-list-item-action>
                  <v-list-item-content>
                    <v-list-item-title>{{ item.content.type }}</v-list-item-title>
                    <v-list-item-subtitle>Type</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
              </v-flex>
              <v-flex xs3>
                <v-list-item>
                  <v-list-item-action>
                    <v-icon>my_location</v-icon>
                  </v-list-item-action>
                  <v-list-item-content>
                    <v-list-item-title>{{ item.content.external_id }}</v-list-item-title>
                    <v-list-item-subtitle>External Identifier</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
              </v-flex>
              <v-flex xs3>
                <v-list-item>
                  <v-list-item-action>
                    <v-icon>collections_bookmark</v-icon>
                  </v-list-item-action>
                  <v-list-item-content>
                    <v-list-item-title>{{ item.content.terms }}</v-list-item-title>
                    <v-list-item-subtitle>Associated Terms</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
              </v-flex>
            </v-layout>
          </v-list>
        </v-flex>
      </v-layout>
    </v-flex>
  </v-layout>
</template>

<script>
export default {
  name: "ServiceList",
  props: {
    items: {
      type: Array,
      default: null
    }
  },
  data() {
    return {}
  }
}
</script>
