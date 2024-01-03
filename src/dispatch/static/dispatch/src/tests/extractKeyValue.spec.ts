import { expect, describe, it } from "vitest"
import { extractKeyValue } from "@/util/jpath"

describe("extractKeyValue", () => {
  it("should correctly extract key-value pair", () => {
    const lineContent = '"name": "Sensitive Action"'
    const { key, value } = extractKeyValue(lineContent)

    expect(key).toBe("name")
    expect(value).toBe("Sensitive Action")
  })

  it("should correctly extract key-value pair with boolean value", () => {
    const lineContent = '"canary": false'
    const { key, value } = extractKeyValue(lineContent)

    expect(key).toBe("canary")
    expect(value).toBe(false)
  })

  it("should correctly extract key-value pair with date value", () => {
    const lineContent = '"start": "2023-11-15T20:10:01Z"'
    const { key, value } = extractKeyValue(lineContent)

    expect(key).toBe("start")
    expect(value).toBe("2023-11-15T20:10:01Z")
  })

  it("should correctly extract key-value pair with numeric value", () => {
    const lineContent = '"id": "1337"'
    const { key, value } = extractKeyValue(lineContent)

    expect(key).toBe("id")
    expect(value).toBe("1337")
  })

  it("should correctly extract key-value pair with empty string value", () => {
    const lineContent = '"empty": ""'
    const { key, value } = extractKeyValue(lineContent)

    expect(key).toBe("empty")
    expect(value).toBe("")
  })

  it("should correctly extract key-value pair with null value", () => {
    const lineContent = '"nullValue": null'
    const { key, value } = extractKeyValue(lineContent)

    expect(key).toBe("nullValue")
    expect(value).toBe(null)
  })

  it("should correctly extract key-value pair with special characters in key", () => {
    const lineContent = '"special@key!": "value"'
    const { key, value } = extractKeyValue(lineContent)

    expect(key).toBe("special@key!")
    expect(value).toBe("value")
  })

  it("should correctly extract key-value pair with special characters in value", () => {
    const lineContent = '"key": "special@value!"'
    const { key, value } = extractKeyValue(lineContent)

    expect(key).toBe("key")
    expect(value).toBe("special@value!")
  })

  it("should correctly extract key-value pair with spaces in key", () => {
    const lineContent = '"key with spaces": "value"'
    const { key, value } = extractKeyValue(lineContent)

    expect(key).toBe("key with spaces")
    expect(value).toBe("value")
  })

  it("should correctly extract key-value pair with spaces in value", () => {
    const lineContent = '"key": "value with spaces"'
    const { key, value } = extractKeyValue(lineContent)

    expect(key).toBe("key")
    expect(value).toBe("value with spaces")
  })

  it("should correctly extract key-value pair with object value", () => {
    const lineContent = '"details": {}'
    const { key, value } = extractKeyValue(lineContent)

    expect(key).toBe("details")
    expect(value).toEqual({})
  })

  it("should correctly extract key-value pair with array value", () => {
    const lineContent = '"asset": []'
    const { key, value } = extractKeyValue(lineContent)

    expect(key).toBe("asset")
    expect(value).toEqual([])
  })

  it("should correctly extract key-value pair with nested object value", () => {
    const lineContent = '"value": {"Api": "sendcommand", "ServiceName": "ssm"}'
    const { key, value } = extractKeyValue(lineContent)

    expect(key).toBe("value")
    expect(value).toEqual({
      Api: "sendcommand",
      ServiceName: "ssm",
    })
  })

  it("should correctly extract key-value pair with nested array of objects", () => {
    const lineContent =
      '"action": [{"type": "AWS_API_CALL", "value": {"Api": "sendcommand", "ServiceName": "ssm"}}]'
    const { key, value } = extractKeyValue(lineContent)

    expect(key).toBe("action")
    expect(value).toEqual([
      {
        type: "AWS_API_CALL",
        value: {
          Api: "sendcommand",
          ServiceName: "ssm",
        },
      },
    ])
  })

  it("should correctly handle a string with escaped quotes", () => {
    const lineContent =
      '"errorMessage": "User: arn:aws:sts::123456789012:assumed-role/test/someuser is not authorized to perform: ssm:SendCommand on resource: arn:aws:ec2:us-west-2:123456789012:instance/i-0123456789abcdef0 because no identity-based policy allows the ssm:SendCommand action"'
    const { key, value } = extractKeyValue(lineContent)

    expect(key).toBe("errorMessage")
    expect(value).toBe(
      "User: arn:aws:sts::123456789012:assumed-role/test/someuser is not authorized to perform: ssm:SendCommand on resource: arn:aws:ec2:us-west-2:123456789012:instance/i-0123456789abcdef0 because no identity-based policy allows the ssm:SendCommand action"
    )
  })

  it("should correctly extract key-value pair with nested object containing array", () => {
    const lineContent = '"geoIP": {"ip": "19.53.236.1337", "zip": ["90017"], "asnum": [2906]}'
    const { key, value } = extractKeyValue(lineContent)

    expect(key).toBe("geoIP")
    expect(value).toEqual({
      ip: "19.53.236.1337",
      zip: ["90017"],
      asnum: [2906],
    })
  })
})
