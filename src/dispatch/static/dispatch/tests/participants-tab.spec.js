/**
 * @vitest-environment jsdom
 */

import Vuex from "vuex"
import { describe, expect, it, vi } from "vitest"
import { createLocalVue, mount } from "@vue/test-utils"
import CaseParticipantsTab from "src/case/ParticipantsTab.vue"

vi.mock("vuex-map-fields", () => ({
  getterType: vi.fn(),
  mapFields: vi.fn(),
}))

const localVue = createLocalVue()
localVue.use(Vuex)

describe("CaseParticipantsTab", () => {
  let store
  let state

  beforeEach(() => {
    state = {
      case_management: {
        selected: {
          participants: [
            {
              id: 1,
              individual: {
                name: "John Doe",
                weblink: "https://example.com/john-doe",
              },
              participant_roles: [
                { role: "Participant", renounced_at: null },
                { role: "Reporter", renounced_at: "2022-01-01T00:00:00.000Z" },
              ],
              team: "Team A",
              location: "Location A",
            },
            {
              id: 2,
              individual: {
                name: "Jane Doe",
                weblink: "https://example.com/jane-doe",
              },
              participant_roles: [{ role: "Assignee", renounced_at: null }],
              team: "Team B",
              location: "Location B",
            },
          ],
        },
      },
    }

    store = new Vuex.Store({ state })
  })

  it("renders the correct number of participants", () => {
    const wrapper = mount(CaseParticipantsTab, { store, localVue })
    const participants = wrapper.vm.$store.state.case_management.selected.participants
    expect(participants).to.have.lengthOf(2)
  })

  it("displays only active roles", () => {
    const wrapper = mount(CaseParticipantsTab, { store, localVue })
    const participantListItems = wrapper.findAll("v-list-item-title").wrappers
    participantListItems.forEach((participantListItem, index) => {
      const participant = state.case_management.selected.participants[index]
      const activeRoles = participant.participant_roles
        .filter((role) => !role.renounced_at)
        .map((role) => role.role)
        .join(", ")
      expect(participantListItem.text()).to.include(activeRoles)
    })
  })

  it("does not display renounced roles", () => {
    const wrapper = mount(CaseParticipantsTab, { store, localVue })
    const participantListItems = wrapper.findAll("v-list-item-title").wrappers
    participantListItems.forEach((participantListItem, index) => {
      const participant = state.case_management.selected.participants[index]
      const renouncedRoles = participant.participant_roles
        .filter((role) => typeof role.renounced_at === "string" && role.renounced_at.length)
        .map((role) => role.role)
        .join(", ")
      expect(participantListItem.text()).to.not.include(renouncedRoles)
    })
  })
})
