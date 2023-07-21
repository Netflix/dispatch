<template>
  <div class="participant-chips">
    <!-- Display Visible Participants -->
    <div v-for="(participant, index) in visibleParticipants" :key="index" class="chip-container">
      <v-menu v-model="menu" bottom rounded offset-y>
        <template v-slot:activator="{ on }">
          <v-btn icon v-on="on">
            <v-avatar
              size="40"
              color="black"
              :class="chipClasses(participant.individual.name)"
              :style="{ zIndex: calculateZIndex(index) }"
              v-on="on"
            >
              <span class="white--text">{{ participant.individual.name | initials }}</span>
            </v-avatar>
          </v-btn>
        </template>
        <v-card width="300">
          <v-list dark>
            <v-list-item v-if="participant.individual">
              <v-list-item-avatar class="highlighted-chip">
                <span class="white--text">{{ participant.individual.name | initials }}</span>
              </v-list-item-avatar>
              <v-list-item-content>
                <v-list-item-title>{{ participant.individual.name }}</v-list-item-title>
                <v-list-item-subtitle>{{
                  participant.participant_roles | activeRoles
                }}</v-list-item-subtitle>
              </v-list-item-content>
              <v-list-item-action>
                <v-btn icon @click="menu = false">
                  <v-icon>mdi-close-circle</v-icon>
                </v-btn>
              </v-list-item-action>
            </v-list-item>
          </v-list>
          <v-list>
            <v-list-item>
              <v-list-item-action>
                <v-icon>mdi-email</v-icon>
              </v-list-item-action>
              <v-list-item-subtitle>{{ participant.individual.email }}</v-list-item-subtitle>
            </v-list-item>

            <v-list-item v-if="participant.individual.company">
              <v-list-item-action>
                <v-icon>business</v-icon>
              </v-list-item-action>
              <v-list-item-subtitle>{{ participant.individual.company }}</v-list-item-subtitle>
            </v-list-item>
            <v-list-item v-if="participant.department">
              <v-list-item-action>
                <v-icon>groups</v-icon>
              </v-list-item-action>
              <v-list-item-subtitle>{{ participant.department }}</v-list-item-subtitle>
            </v-list-item>
            <v-list-item v-if="participant.team">
              <v-list-item-action>
                <v-icon>group</v-icon>
              </v-list-item-action>
              <v-list-item-subtitle>{{ participant.team }}</v-list-item-subtitle>
            </v-list-item>
            <v-list-item v-if="participant.location">
              <v-list-item-action>
                <v-icon>mdi-map-marker</v-icon>
              </v-list-item-action>
              <v-list-item-subtitle>{{ participant.location }}</v-list-item-subtitle>
            </v-list-item>

            <v-list-item
              v-if="participant.individual.weblink"
              :href="participant.individual.weblink"
              target="_blank"
            >
              <v-list-item-action>
                <v-icon>open_in_new</v-icon>
              </v-list-item-action>
              <v-list-item-subtitle>External Profile</v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </v-card>
      </v-menu>
    </div>

    <v-dialog v-model="participantDialogVisible" max-width="800">
      <v-card>
        <v-card-title>Other Participants</v-card-title>
        <v-divider></v-divider>
        <div class="ml-2">
          <div v-if="hiddenParticipants && hiddenParticipants.length">
            <span v-for="participant in hiddenParticipants" :key="participant.id">
              <v-list-item :href="participant.individual.weblink" target="_blank">
                <v-list-item-content>
                  <v-list-item-title ref="participants">
                    {{ participant.individual.name }} ({{
                      participant.participant_roles | activeRoles
                    }})
                  </v-list-item-title>
                  <v-list-item-subtitle>
                    {{ participant.team }} - {{ participant.location }}
                  </v-list-item-subtitle>
                </v-list-item-content>
                <v-list-item-action>
                  <v-list-item-icon>
                    <v-icon>open_in_new</v-icon>
                  </v-list-item-icon>
                </v-list-item-action>
              </v-list-item>
              <v-divider />
            </span>
          </div>
          <div v-else>
            <p class="text-center">No participant data available.</p>
          </div>
        </div>
      </v-card>
    </v-dialog>
    <!-- Display Hidden Participants Chip -->
    <div v-if="hiddenParticipants.length" class="chip-container">
      <v-btn icon @click="participantDialogVisible = true">
        <v-avatar size="32" color="grey lighten-3">
          <span class="grey--text">+{{ hiddenParticipants.length }}</span>
        </v-avatar>
      </v-btn>
    </div>

    <!-- Add new participant button, saving for future release -->
    <!-- <v-tooltip bottom>
      <template v-slot:activator="{ on, attrs }">
        <v-btn
          small
          icon
          outlined
          elevation="1"
          color="grey lighten-2"
          class="ml-4 plus-btn"
          @click="addParticipant"
          v-bind="attrs"
          v-on="on"
        >
          <v-icon small dense color="black">mdi-plus</v-icon>
        </v-btn>
      </template>
      <span>Add new participant</span>
    </v-tooltip>

    <v-dialog v-model="addParticipantDialog" max-width="600">
      <v-card>
        <v-card-title>Add Case Participant</v-card-title>
        <v-card-text>
          By adding a new participant, they gain access to all Case resources. They'll also be able
          to view the case, even when visibility is restricted.
        </v-card-text>
        <v-card-text> <new-participant-select /> </v-card-text>
        <v-btn class="ml-6 mb-4" small color="info" elevation="1"> Submit </v-btn>
      </v-card>
    </v-dialog> -->
  </div>
</template>

<script>
import NewParticipantSelect from "@/case/NewParticipantSelect.vue"

export default {
  components: { NewParticipantSelect },
  name: "ParticipantChips",
  props: {
    participants: {
      type: Array,
      required: true,
    },
    highlightedParticipants: {
      type: Array,
      default: () => [],
    },
  },
  computed: {
    calculateZIndex() {
      return (index) => 1000 - index
    },
    visibleParticipants() {
      return this.orderedParticipants.slice(0, 1)
    },
    hiddenParticipants() {
      return this.orderedParticipants.slice(1)
    },
    orderedParticipants() {
      const assignee = this.participants.find((participant) =>
        this.highlightedParticipants.includes(participant.individual.name)
      )
      const otherParticipants = this.participants.filter(
        (participant) => !this.highlightedParticipants.includes(participant.individual.name)
      )

      if (assignee) {
        return [assignee, ...otherParticipants]
      } else {
        return this.participants
      }
    },
  },
  data() {
    return {
      addParticipantDialog: false,
      hoverIndex: -1,
      participantDialogVisible: false,
    }
  },
  methods: {
    openAddParticipantDialog() {
      this.addParticipantDialog = true
    },
    addParticipant() {
      this.openAddParticipantDialog()
    },
    chipClasses(name) {
      console.log("GOT NAME: %O", name)
      console.log("GOT: %O", this.highlightedParticipants)
      console.log(this.highlightedParticipants.includes(name))
      return {
        bordered: true,
        "highlighted-chip": this.highlightedParticipants.includes(name),
      }
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
  margin-right: -3px;
  transition: all 0.2s ease-in-out;
}

.border {
  border: 4px solid rgba(255, 0, 0, 0.87);
  border-radius: 50%;
}

.plus-btn {
  vertical-align: middle;
}

.bordered {
  border: 2px solid white !important;
}

.highlighted-chip {
  background: linear-gradient(45deg, #5252ff 0%, #fad0c4 99%, #fad0c4 100%) !important;
}
</style>
