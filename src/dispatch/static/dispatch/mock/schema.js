const schema = {
  type: "object",
  properties: {
    user: {
      type: "array",
      minItems: 5,
      maxItems: 10,
      items: {
        type: "object",
        properties: {
          id: {
            type: "string",
            faker: "random.uuid"
          },
          first_name: {
            type: "string",
            faker: "name.firstName"
          },
          last_name: {
            type: "string",
            faker: "name.lastName"
          },
          avatar: {
            type: "string",
            faker: "image.avatar"
          },
          email: {
            type: "string",
            faker: {
              "internet.email": [false, false, "gmail.com"]
            }
          }
        },
        required: ["id", "first_name", "last_name", "email"]
      }
    },
    email: {
      type: "array",
      minItems: 5,
      maxItems: 10,
      items: {
        type: "object",
        properties: {
          id: {
            type: "string",
            faker: "random.uuid"
          },
          user_id: {
            type: "string",
            faker: "name.firstName"
          },
          title: {
            type: "string",
            faker: "name.lastName"
          },
          content: {
            type: "string",
            faker: "image.avatar"
          },
          to: {
            type: "string",
            faker: "internet.email"
          }
        },
        required: ["id", "first_name", "last_name", "email"]
      }
    }
  },
  required: ["user", "email"]
}

module.exports = schema
