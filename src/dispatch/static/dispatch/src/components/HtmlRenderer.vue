<template>
  <div v-if="isHtml" v-html="sanitizedContent" class="html-content" />
  <div v-else class="plain-text-content">
    {{ content }}
  </div>
</template>

<script setup>
import { computed } from "vue"
import DOMPurify from "dompurify"

const props = defineProps({
  content: {
    type: String,
    default: "",
  },
})

// Check if content contains HTML tags
const isHtml = computed(() => {
  if (!props.content) return false
  return /<[^>]+>/.test(props.content)
})

// Sanitize HTML content to prevent XSS attacks
const sanitizedContent = computed(() => {
  if (!props.content) return ""

  // Configure DOMPurify to allow common formatting tags
  const config = {
    ALLOWED_TAGS: [
      "p",
      "br",
      "strong",
      "b",
      "em",
      "i",
      "u",
      "s",
      "strike",
      "h1",
      "h2",
      "h3",
      "h4",
      "h5",
      "h6",
      "ul",
      "ol",
      "li",
      "blockquote",
      "pre",
      "code",
      "a",
    ],
    ALLOWED_ATTR: ["href", "target", "rel"],
    ALLOW_DATA_ATTR: false,
  }

  return DOMPurify.sanitize(props.content, config)
})
</script>

<style lang="scss" scoped>
.html-content {
  // TipTap-like styling for consistency
  :deep(> * + *) {
    margin-top: 0.75em;
  }

  :deep(h1) {
    font-size: 1.75em;
    font-weight: bold;
    margin-top: 1.5em;
    margin-bottom: 0.5em;
  }

  :deep(h2) {
    font-size: 1.5em;
    font-weight: bold;
    margin-top: 1.25em;
    margin-bottom: 0.5em;
  }

  :deep(h3) {
    font-size: 1.25em;
    font-weight: bold;
    margin-top: 1em;
    margin-bottom: 0.5em;
  }

  :deep(h4, h5, h6) {
    font-size: 1em;
    font-weight: bold;
    margin-top: 0.75em;
    margin-bottom: 0.5em;
  }

  :deep(strong, b) {
    font-weight: bold;
  }

  :deep(em, i) {
    font-style: italic;
  }

  :deep(u) {
    text-decoration: underline;
  }

  :deep(s, strike) {
    text-decoration: line-through;
  }

  :deep(code) {
    background-color: rgba(97, 97, 97, 0.1);
    color: #616161;
    padding: 0.2em 0.4em;
    border-radius: 4px;
    font-family: monospace;
    font-size: 0.9em;
  }

  :deep(pre) {
    background-color: #f5f5f5;
    border-radius: 5px;
    padding: 1em;
    overflow-x: auto;

    code {
      background: none;
      padding: 0;
      color: #333;
    }
  }

  :deep(blockquote) {
    border-left: 4px solid #ddd;
    padding-left: 1em;
    margin-left: 0;
    font-style: italic;
    color: #666;
  }

  :deep(ul, ol) {
    padding-left: 1.5em;
  }

  :deep(li) {
    margin-bottom: 0.25em;
  }

  :deep(a) {
    color: #1976d2;
    text-decoration: underline;

    &:hover {
      color: #1565c0;
    }
  }
}

.plain-text-content {
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>
