<template>
  <v-container>
    <v-row v-if="uniqueEntities.length >= 1">
      <v-row justify="center">
        <date-chip-group-relative
          class="pl-6 mt-6"
          label="Time Range"
          v-model="selectedDateTime"
          @input="onSelectedDateTimeChange"
        />
      </v-row>
      <v-col class="pl-6 mt-6" v-for="entity in uniqueEntities" :key="entity.id" cols="6">
        <entity-card :entity="entity" :count="entity.count" :selectedDateTime="selectedDateTime" />
      </v-col>
    </v-row>
    <div v-else>
      <v-row justify="center">
        <v-card class="mt-16 pb-16" elevation="0" width="400px">
          <v-btn disabled class="ml-4" color="grey lighten-5" elevation="0">
            <v-icon color="grey darken-1"> mdi-drawing-box </v-icon>
          </v-btn>
          <v-card-title>Add your first entity type</v-card-title>
          <v-card-subtitle
            >Entity Types extract valuable information from your raw signal data. They automatically
            identify and correlate entities across various signals and cases.
          </v-card-subtitle>
          <v-row>
            <!-- New Button -->
            <v-btn color="info" plain text small class="ml-4"
              >Learn more <v-icon small class="ml-2 mr-1"> mdi-arrow-right </v-icon></v-btn
            >
          </v-row>
          <v-row class="pt-6 pb-6">
            <!-- New Button -->
            <v-btn color="info" elevation="1" small @click="showEntityTypeDialog" class="ml-7"
              ><v-icon small class="ml-n1 mr-1"> mdi-plus </v-icon>Add an entity type</v-btn
            >
            <entity-type-create-dialog
              ref="entityTypeDialog"
              :signalDefinition="signalDef"
            ></entity-type-create-dialog>
          </v-row>
        </v-card>
      </v-row>
    </div>
  </v-container>
</template>

<script>
import EntityCard from "@/entity/EntityCard.vue"
import EntityTypeCreateDialog from "@/entity_type/EntityTypeCreateDialog.vue"
import DateChipGroupRelative from "@/components/DateChipGroupRelative.vue"

export default {
  name: "EntitiesTab",
  components: {
    EntityCard,
    EntityTypeCreateDialog,
    DateChipGroupRelative,
  },
  props: {
    selected: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      selectedDateTime: 30,
    }
  },
  computed: {
    signalDef() {
      if (this.selected.signal_instances.length) {
        console.log("GOT DEF %O", this.selected.signal_instances[0])
        return this.selected.signal_instances[0].signal
      }
    },
    uniqueEntities() {
      const uniqueEntities = {}

      if (this.selected.signal_instances.length) {
        this.selected.signal_instances.forEach((instance) => {
          instance.entities.forEach((entity) => {
            const key = `${entity.entity_type}_${entity.value}`

            if (uniqueEntities[key]) {
              uniqueEntities[key].count++
            } else {
              uniqueEntities[key] = {
                ...entity,
                count: 1,
              }
            }
          })
        })
      }

      return Object.values(uniqueEntities)
    },
  },
  methods: {
    onSelectedDateTimeChange(newValue) {
      this.selectedDateTime = newValue
    },
    showEntityTypeDialog() {
      this.$refs.entityTypeDialog.openDialog()
    },
  },
}
</script>

<style scoped>
.v-btn {
  text-transform: none !important;
  /* color: rgb(39, 39, 39) !important; */
  font-weight: bold !important;
  letter-spacing: normal !important;
}
</style>
