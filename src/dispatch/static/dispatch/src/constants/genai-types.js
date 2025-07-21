// GenAI Type constants - shared between frontend and backend
export const GENAI_TYPES = {
  1: "Tag Recommendation",
  2: "Incident Summary",
  3: "Signal Analysis",
  4: "Conversation Summary",
  5: "Tactical Report Summary",
}

// Reverse mapping for easy lookup - generated programmatically
export const GENAI_TYPE_IDS = Object.fromEntries(
  Object.entries(GENAI_TYPES).map(([id, name]) => [name, parseInt(id)])
)

// Helper functions
export const getGenaiTypeName = (typeId) => {
  return GENAI_TYPES[typeId] || `Unknown Type (${typeId})`
}

export const getGenaiTypeId = (typeName) => {
  return GENAI_TYPE_IDS[typeName]
}

export const getGenaiTypeOptions = () => {
  return Object.entries(GENAI_TYPES).map(([value, text]) => ({
    value: parseInt(value),
    text: text,
  }))
}
