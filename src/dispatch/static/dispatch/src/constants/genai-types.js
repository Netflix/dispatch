// GenAI Type constants - shared between frontend and backend
export const GENAI_TYPES = {
  1: "Tag Recommendation",
  2: "Incident Summary",
  3: "Signal Analysis",
  4: "Conversation Summary",
  5: "Tactical Report Summary",
}

// Helper functions
export const getGenaiTypeName = (typeId) => {
  return GENAI_TYPES[typeId] || `Unknown Type (${typeId})`
}

export const getGenaiTypeOptions = () => {
  return Object.entries(GENAI_TYPES).map(([value, text]) => ({
    value: parseInt(value),
    text: text,
  }))
}
