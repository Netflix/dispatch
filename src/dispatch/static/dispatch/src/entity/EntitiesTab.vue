<template>
  <v-container fill-height fluid>
    <v-row justify="center" align="center" v-if="entities.length >= 1">
      <date-chip-group-relative
        class="mt-6"
        label="Time Range"
        v-model="selectedDateTime"
        @input="onSelectedDateTimeChange"
      />
      <entity-type-create-dialog></entity-type-create-dialog>
      <v-col v-for="entity in entities" :key="entity.id" cols="6">
        <entity-card :entity="entity" :selectedDateTime="selectedDateTime" />
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
import EntityCard from "@/entity/EntityCard.vue";
import DateChipGroupRelative from "@/components/DateChipGroupRelative.vue";
import EntityTypeCreateDialog from "@/entity_type/EntityTypeCreateDialog.vue";

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
            id: entity.id,
          }));
          return acc.concat(entities);
        }, []);
      } else {
        return [];
      }
    },
  },
  methods: {
    onSelectedDateTimeChange(newValue) {
      this.selectedDateTime = newValue;
    },
  },
};
</script>
