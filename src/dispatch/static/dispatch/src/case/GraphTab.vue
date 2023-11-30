<script setup lang="ts">
import { VueFlow, isNode, useVueFlow, MarkerType } from "@vue-flow/core"
import { Background } from "@vue-flow/background"
import { Controls } from "@vue-flow/controls"
import { MiniMap } from "@vue-flow/minimap"
import { ref, watchEffect } from "vue"
import { forceSimulation, forceLink, forceManyBody, forceCenter } from "d3-force"
import SignalInstanceNode from "@/signal/SignalInstanceNode.vue"

// Define props
const props = defineProps({
  signalInstances: {
    type: Array,
    required: true,
  },
})

/**
 * useVueFlow provides all event handlers and store properties
 * You can pass the composable an object that has the same properties as the VueFlow component props
 */
const { onPaneReady, onNodeDragStop, onConnect, addEdges, setTransform, toObject } = useVueFlow()

// Elements array
const elements = ref([])

/**
 * Create our elements
 */
watchEffect(() => {
  // Clear existing elements
  let elementsTemp = []

  const uniqueEntities = {} // Create an object to store unique entities

  // Check if signalInstances is not null
  if (props.signalInstances && props.signalInstances.length > 0) {
    // Loop through all instances
    props.signalInstances.forEach((instance, index) => {
      // Create node for the signal instance
      const instanceNode = {
        id: instance.raw.id,
        type: "signal",
        label: instance.signal.name,
        data: instance.raw,
        position: { x: 100 * (index + 1), y: 100 * (index + 1) },
        class: "light",
      }

      // Push instance node to elements array
      elementsTemp.push(instanceNode)

      // Loop through all entities of current signal instance
      instance.entities.forEach((entity, entityIndex) => {
        // Check if entity is not already in uniqueEntities
        if (!uniqueEntities[entity.id]) {
          const entityNode = {
            id: `${entity.id}`,
            label: entity.value,
            position: { x: 100 * (index + 1) + 100, y: 100 * entityIndex + 100 },
            class: "dark",
            type: "output",
          }

          // Add entity to uniqueEntities
          uniqueEntities[entity.id] = entityNode

          // Push entity node to elements array
          elementsTemp.push(entityNode)
        }
      })
    })

    // Create a new force simulation
    const simulation = forceSimulation(elementsTemp.filter(isNode))
      .force(
        "link",
        forceLink(elementsTemp.filter((el) => !isNode(el)))
          .id((d) => d.id)
          .distance(200) // This increases the link distance
      )
      .force("charge", forceManyBody().strength(-900)) // This decreases the charge strength
      .force("center", forceCenter())

    // Run the simulation for a certain number of steps
    for (let i = 0; i < 3; ++i) simulation.tick()

    // After the simulation, the positions of the nodes will be updated
    // You can assign these positions to your Vue Flow nodes
    elementsTemp = elementsTemp.map((el) => {
      if (isNode(el)) {
        // If el is a node, update its position with the position calculated by the simulation
        const d = simulation.find(el.x, el.y)
        return { ...el, position: { x: d.x, y: d.y } }
      } else {
        // If el is not a node (i.e., it's an edge), don't change it
        return el
      }
    })

    // Loop through all instances again to create edges
    props.signalInstances.forEach((instance) => {
      instance.entities.forEach((entity) => {
        // Create edge between instance node and entity node
        const edge = {
          id: `${instance.raw.id}-${entity.id}`,
          source: instance.raw.id,
          target: `${entity.id}`,
          markerEnd: MarkerType.ArrowClosed,
        }

        // Push edge to elements array
        elementsTemp.push(edge)
      })
    })

    // Finally update elements.value with the new positions
    elements.value = elementsTemp
  }
})

/**
 * This is a Vue Flow event-hook which can be listened to from anywhere you call the composable, instead of only on the main component
 *
 * onPaneReady is called when viewpane & nodes have visible dimensions
 */
onPaneReady(({ fitView }) => {
  fitView()
})

onNodeDragStop((e) => console.log("drag stop", e))

/**
 * onConnect is called when a new connection is created.
 * You can add additional properties to your new edge (like a type or label) or block the creation altogether
 */
onConnect((params) => addEdges(params))

const dark = ref(false)

/**
 * toObject transforms your current graph data to an easily persist-able object
 */
// eslint-disable-next-line no-unused-vars
function logToObject() {
  return console.log(toObject())
}

/**
 * Resets the current viewpane transformation (zoom & pan)
 */
// eslint-disable-next-line no-unused-vars
function resetTransform() {
  return setTransform({ x: 0, y: 0, zoom: 1 })
}

// eslint-disable-next-line no-unused-vars
function toggleClass() {
  return (dark.value = !dark.value)
}

function openSignalViewer(signalInstance) {
  // Here you can open the signal viewer with the signalInstance data
  console.log("Opening viewer for signal instance", signalInstance)
}
</script>

<template>
  <VueFlow
    :nodes="elements"
    :class="{ dark }"
    class="basicflow"
    :default-viewport="{ zoom: 1.5 }"
    :min-zoom="0.2"
    :max-zoom="4"
  >
    <template #node-signal="signalInstanceNodeProps">
      <SignalInstanceNode v-bind="signalInstanceNodeProps" @open-viewer="openSignalViewer" />
    </template>
    <Background :pattern-color="dark ? '#FFFFFB' : '#aaa'" gap="8" />
    <MiniMap />
    <Controls />
  </VueFlow>
</template>

<style>
/* import the necessary styles for Vue Flow to work */
@import "@vue-flow/core/dist/style.css";

/* import the default theme, this is optional but generally recommended */
@import "@vue-flow/core/dist/theme-default.css";

.basicflow {
  width: 100%;
  height: 78vh;
}
</style>
