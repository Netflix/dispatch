<template>
  <v-container fluid>
    <v-row v-if="entities.length >= 1">
      <v-col
        v-for="entity in entities"
        :key="entity.id"
        cols="6"
      >
        <entity-card :entity="entity" />
      </v-col>
    </v-row>
    <v-row v-else>
      <v-col cols="12">
        <v-card>
          <v-card-title>No entities found</v-card-title>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import EntityCard from "@/entity/EntityCard.vue"

export default {
  name: "EntitiesTab",
  components: {
    EntityCard,
  },
  props: {
    selected: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      headers: [
        { text: "Entity Type", value: "entity_type" },
        { text: "Entity", value: "entity" },
      ],
    };
  },
  computed: {
    entities() {
      if (this.selected.signal_instances.length) {
        // Concatenate all the entities associated with each SignalInstance
        return this.selected.signal_instances.reduce((acc, curr) => {
          const entities = curr.entities.map((entity) => ({
            entity_type: entity.entity_type,
            value: entity.value,
            id: entity.id
          }));
          return acc.concat(entities);
        }, []);
      } else {
        return [];
      }
    },
  },
};
</script>
