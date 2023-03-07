<template>
  <v-container>
    <v-row justify="center">
      <date-chip-group-relative
        class="pl-6 mt-6"
        label="Time Range"
        v-model="selectedDateTime"
        @input="onSelectedDateTimeChange"
      />
    </v-row>
    <v-row v-if="entities.length >= 1">
      <v-col class="pl-6 mt-6" v-for="entity in entities" :key="entity.id" cols="6">
        <entity-card :entity="entity" :selectedDateTime="selectedDateTime" />
      </v-col>
    </v-row>
    <div v-else>
      <p class="text-center">No entity data available.</p>
    </div>
  </v-container>
</template>

<script>
import EntityCard from "@/entity/EntityCard.vue"
import DateChipGroupRelative from "@/components/DateChipGroupRelative.vue"

export default {
  name: "EntitiesTab",
  components: {
    EntityCard,
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
    entities() {
      if (this.selected.signal_instances.length) {
        // Concatenate all the entities associated with each SignalInstance
        return this.selected.signal_instances.reduce((acc, curr) => {
          const entities = curr.entities.map((entity) => ({
            entity_type: entity.entity_type,
            value: entity.value,
            id: entity.id,
          }))
          return acc.concat(entities)
        }, [])
      } else {
        return []
      }
    },
  },
  methods: {
    onSelectedDateTimeChange(newValue) {
      this.selectedDateTime = newValue
    },
  },
}
</script>
