<template>
  <v-layout wrap>
    <div class="headline">
      Terms
    </div>
    <v-flex xs12>
      <v-layout column>
        <v-flex>
          <v-list
            two-line
            class="elevation-2"
          >
            <v-list-group
              v-for="item in items"
              :key="item.content.id"
              no-action
            >
              <template v-slot:activator>
                <v-list-item>
                  <v-layout>
                    <v-flex xs3>
                      <v-list-item>
                        <v-list-item-action>
                          <v-icon>fa fa-adjust</v-icon>
                        </v-list-item-action>
                        <v-list-item-content>
                          <v-list-item-title>
                            <div class="text-uppercase">
                              {{ item.content.source }}
                            </div>
                          </v-list-item-title>
                          <v-list-item-subtitle>Source</v-list-item-subtitle>
                        </v-list-item-content>
                      </v-list-item>
                    </v-flex>
                    <v-flex xs9>
                      <v-list-item>
                        <v-list-item-content>
                          <v-list-item-title>{{ item.content.text }}</v-list-item-title>
                          <v-list-item-subtitle>Text</v-list-item-subtitle>
                        </v-list-item-content>
                      </v-list-item>
                    </v-flex>
                  </v-layout>
                </v-list-item>
              </template>
              <v-card
                v-for="description in item.content.descriptions"
                :key="description.id"
              >
                <v-card-title primary-title>
                  <div>{{ description.text }}</div>
                </v-card-title>
              </v-card>
            </v-list-group>
          </v-list>
        </v-flex>
      </v-layout>
    </v-flex>
  </v-layout>
</template>
<script>
export default {
  name: "SearchList",
  props: {
    items: {
      default: null,
      type: Array,
      showMore: false
    }
  }
}
</script>
