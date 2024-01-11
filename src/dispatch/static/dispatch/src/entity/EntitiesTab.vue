<template>
  <v-container>
    <v-row justify="center">
      <date-chip-group-relative
        class="pl-6 mt-6"
        label="Time Range"
        v-model="selectedDateTime"
        @update:model-value="onSelectedDateTimeChange"
      />
    </v-row>
    <v-row v-if="uniqueEntities.length >= 1">
      <v-col class="pl-6 mt-6" v-for="entity in uniqueEntities" :key="entity.id" cols="6">
        <entity-card :entity="entity" :count="entity.count" :selectedDateTime="selectedDateTime" />
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
  },
}
</script>
