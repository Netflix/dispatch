<template>
  <div class="participant-chips">
    <div v-for="(participant, index) in orderedParticipants" :key="index" class="chip-container">
      <v-menu v-model="menu" bottom right transition="scale-transition" origin="top left">
        <template v-slot:activator="{ on }">
          <v-chip pill small :class="chipClasses(participant.individual.name)" v-on="on">
            <v-avatar class="avatar ml-1">
              <span class="white--text">{{ participant.individual.name | initials }}</span>
            </v-avatar>
            <span class="full-name white--text mr-4 ml-n6">{{ participant.individual.name }}</span>
          </v-chip>
        </template>
        <v-card width="300">
          <v-list dark>
            <v-list-item v-if="participant.individual">
              <v-list-item-avatar :class="chipClasses(participant.individual.name)">
                <span class="white--text">{{ participant.individual.name | initials }}</span>
              </v-list-item-avatar>
              <v-list-item-content>
                <v-list-item-title>{{ participant.individual.name }}</v-list-item-title>
                <v-list-item-subtitle>{{ participant.individual.email }}</v-list-item-subtitle>
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
            <v-list-item v-if="participant.location">
              <v-list-item-action>
                <v-icon>mdi-map-marker</v-icon>
              </v-list-item-action>
              <v-list-item-subtitle>{{ participant.location }}</v-list-item-subtitle>
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
    <v-tooltip bottom>
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
    </v-dialog>
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
        "name-chip": true,
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
  margin-right: -10px;
  transition: all 0.2s ease-in-out;
}

.plus-btn {
  vertical-align: middle;
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
  width: 35px;
  height: 35px;
  padding: 0;
  justify-content: center;
  overflow: hidden;
  transition: all 0.2s ease-in-out;

  color: white; /* Set the text color to white for better visibility against the gradient background */
}

.name-chip.expand {
  border-radius: 28px;
  width: auto;
  padding: 0 12px;
}

.avatar {
  width: 35px;
  height: 35px;
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

.highlighted-chip {
  background: linear-gradient(45deg, #5252ff 0%, #fad0c4 99%, #fad0c4 100%) !important;
}
</style>
