<template>
  <div class="participant-chips">
    <div v-for="(participant, index) in participants" :key="index" class="chip-container">
      <v-chip
        pill
        small
        class="name-chip"
        :class="{ expand: index === hoverIndex }"
        @mouseover="hoverIndex = index"
        @mouseleave="hoverIndex = -1"
      >
        <v-avatar class="avatar ml-2">
          <span class="black--text">{{ participant.individual.name | initials }}</span>
        </v-avatar>
        <span class="full-name black--text mr-4 ml-n6">{{ participant.individual.name }}</span>
      </v-chip>
    </div>
    <v-tooltip bottom>
      <template v-slot:activator="{ on, attrs }">
        <v-btn icon class="ml-4 plus-btn" @click="addParticipant" v-bind="attrs" v-on="on">
          <v-icon>mdi-plus</v-icon>
        </v-btn>
      </template>
      <span>Add new participant</span>
    </v-tooltip>
  </div>
</template>

<script>
export default {
  name: "ParticipantChips",
  props: {
    participants: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      hoverIndex: -1,
    }
  },
  methods: {
    addParticipant() {
      // Method to handle adding a new participant
    },
    initials(name) {
      return name
        .split(" ")
        .map((n) => n[0])
        .join("")
        .toUpperCase()
    },
  },
}
</script>

<style scoped>
.chip-container {
  display: inline-block;
  margin-right: -10px;
  transition: all 0.2s ease-in-out;
}

.plus-btn {
  vertical-align: middle;
}

.name-chip.v-chip,
.name-chip.expand.v-chip,
.name-chip .v-avatar {
  background: linear-gradient(
    45deg,
    #ff9a9e 0%,
    #fad0c4 99%,
    #fad0c4 100%
  ) !important; /* Gradient background with increased specificity and important! keyword */
}

.name-chip .avatar span {
  transition: opacity 0.2s ease-in-out; /* Add transition for smooth fade effect */
}

.name-chip .avatar {
  transition: opacity 0.2s ease-in-out; /* Add transition for smooth fade effect */
}

.name-chip.expand .avatar {
  opacity: 0; /* Hide avatar when chip is expanded */
}

.name-chip.expand .avatar span {
  opacity: 0; /* Hide initials when chip is expanded */
}

.name-chip {
  border-radius: 50%;
  width: 40px;
  height: 40px;
  padding: 0;
  justify-content: center;
  overflow: hidden;
  transition: all 0.2s ease-in-out;
  background: linear-gradient(
    45deg,
    #ff9a9e 0%,
    #fad0c4 99%,
    #fad0c4 100%
  ); /* Gradient background */
  color: white; /* Set the text color to white for better visibility against the gradient background */
}

.name-chip.expand {
  border-radius: 28px;
  width: auto;
  padding: 0 12px;
  background: linear-gradient(
    45deg,
    #ff9a9e 0%,
    #fad0c4 99%,
    #fad0c4 100%
  ); /* Gradient background */
}

.avatar {
  width: 40px;
  height: 40px;
  background: transparent; /* Make the avatar background transparent so the chip's gradient shows through */
}

.full-name {
  opacity: 0;
  transition: opacity 0.2s ease-in-out 0.2s;
  white-space: nowrap;
}

.name-chip.expand .full-name {
  opacity: 1;
}
</style>
