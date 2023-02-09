/**
 * @vitest-environment jsdom
 */

import { describe, expect, it, vi } from "vitest"
import { createLocalVue, shallowMount } from "@vue/test-utils"
import CaseParticipantsTab from "src/case/ParticipantsTab.vue"
import { activeRoles } from "src/filters"

describe("CaseParticipantsTab", () => {
  const localVue = createLocalVue()
  localVue.filter("activeRoles", activeRoles)

  vi.mock("vuex-map-fields", () => ({
    getterType: vi.fn(),
    mapFields: vi.fn(),
  }))

  const participants = [
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
  ]

  const computed = {
    participants: () => participants,
  }

  it("assert if there's participants that we render them", () => {
    const wrapper = shallowMount(CaseParticipantsTab, { localVue, computed })
    const participantListItems = wrapper.findAll("v-list-item-title").wrappers
    expect(participantListItems).to.have.lengthOf(2)
  })

  it("displays active roles", () => {
    const wrapper = shallowMount(CaseParticipantsTab, { localVue, computed })
    const participantListItems = wrapper.findAll("v-list-item-title").wrappers
    console.log(participantListItems)

    participantListItems.forEach((participantListItem, index) => {
      const participant = participants[index]
      const activeRoles = participant.participant_roles
        .filter((role) => !role.renounced_at)
        .map((role) => role.role)
        .join(", ")

      console.log("test")
      console.log(activeRoles)
      console.log("test")
      console.log(participantListItem.text())

      expect(participantListItem.text()).to.include(activeRoles)
    })
  })

  it("does not display renounced roles", () => {
    const wrapper = shallowMount(CaseParticipantsTab, { localVue, computed })
    const participantListItems = wrapper.findAll("v-list-item-title").wrappers

    participantListItems.forEach((participantListItem, index) => {
      const participant = participants[index]
      const renouncedRoles = participant.participant_roles
        .filter((role) => role.renounced_at)
        .map((role) => role.role)
        .join(", ")

      if (renouncedRoles) {
        expect(participantListItem.text()).to.not.include(renouncedRoles)
      }
    })
  })
})
