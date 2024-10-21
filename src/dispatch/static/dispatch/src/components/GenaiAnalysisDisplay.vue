<template>
  <div>
    <h2>GenAI Analysis</h2>
    <div v-if="analysis && Object.keys(analysis).length > 0">
      <div v-for="(value, key) in analysis" :key="key" class="analysis-item">
        <h3>
          <b>{{ key }}</b>
        </h3>
        <div v-if="isObject(value)">
          <!-- Render each sub-value with formatText to handle links and code formatting -->
          <span v-for="(subValue, subKey) in value" :key="subKey" v-html="formatText(subValue)" />
        </div>
        <span v-else v-html="formatText(value)" />
      </div>
    </div>
    <div v-else>
      <p>A GenAI analysis does not exist for this case.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps } from "vue"
import DOMPurify from "dompurify"

// Define the `analysis` prop
defineProps({
  analysis: {
    type: Object,
    required: false,
    default: null,
  },
})

// Helper function to check if a value is an object
function isObject(value) {
  return typeof value === "object" && value !== null
}

// Function to format text, converting <URL|text> format to clickable links and wrapping `code` with <code> tags
function formatText(text) {
  if (typeof text !== "string") return text

  // Convert <URL|text> format to clickable links
  let formattedText = text.replace(/<([^|]+)\|([^>]+)>/g, '<a href="$1" target="_blank">$2</a>')

  // Convert `code` format to <code>code</code> for inline code styling
  formattedText = formattedText.replace(/`([^`]+)`/g, "<code>$1</code>")

  // Sanitize the formatted text to avoid XSS
  return DOMPurify.sanitize(formattedText)
}
</script>

<style scoped>
h2 {
  margin-bottom: 1rem;
  font-size: 1.5em;
}

.analysis-item h3 {
  margin-top: 1em;
}

a {
  color: #1a73e8;
  text-decoration: underline;
}

code {
  font-family: monospace;
  background-color: #f5f5f5;
  padding: 0.2em 0.4em;
  border-radius: 4px;
}
</style>
