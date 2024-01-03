import jsonpath from "jsonpath"
import { expect, describe, it } from "vitest"

import { findPath } from "@/util/jpath"

function testFindPath<T>(obj: T, key: keyof any, value: any, expectedPath: string | null) {
  const result = findPath(obj, key, value)
  expect(result).toBe(expectedPath)
  if (expectedPath) {
    const jsonpathResult = jsonpath.query(obj, result as string)
    expect(jsonpathResult[0]).toBe(value)
  }
}

describe("findPath", () => {
  it("should find the correct path to the key", () => {
    const obj = {
      a: {
        b: {
          c: "value",
        },
        d: "another value",
      },
      e: "yet another value",
    }

    const key = "c"
    const value = "value"
    const expectedPath = "$.a.b.c"

    testFindPath(obj, key, value, expectedPath)
  })

  it("should return null if the key-value pair does not exist", () => {
    const obj = {
      a: {
        b: {
          c: "value",
        },
        d: "another value",
      },
      e: "yet another value",
    }

    const key = "f"
    const value = "non-existent value"
    const result = findPath(obj, key, value)

    expect(result).toBeNull()
  })

  it("should handle keys with special characters", () => {
    const obj = {
      "a:b": {
        "/c": "value",
      },
    }

    const key = "/c"
    const value = "value"
    const expectedPath = "$['a:b']['/c']"

    testFindPath(obj, key, value, expectedPath)
  })

  it("should handle keys with $", () => {
    const obj = {
      a$b: {
        c: "value",
      },
    }

    const key = "c"
    const value = "value"
    const expectedPath = "$['a$b'].c"
    testFindPath(obj, key, value, expectedPath)
  })

  it("should handle keys with @", () => {
    const obj = {
      "a@b": {
        c: "value",
      },
    }

    const key = "c"
    const value = "value"
    const expectedPath = "$['a@b'].c"
    testFindPath(obj, key, value, expectedPath)
  })

  it("should handle keys with *", () => {
    const obj = {
      "a*b": {
        c: "value",
      },
    }

    const key = "c"
    const value = "value"
    const expectedPath = "$['a*b'].c"
    testFindPath(obj, key, value, expectedPath)
  })

  const geigerAlert = {
    id: "12345678910",
    name: "Sensitive Action",
    canary: false,
    events: [
      {
        start: "2023-11-15T20:10:01Z",
        original: {
          name: "ASSIGN_ROLE",
          type: "DELEGATED_ADMIN_SETTINGS",
          parameters: [
            {
              name: "ROLE_NAME",
              value: "users",
            },
            {
              name: "USER_EMAIL",
              value: "adm-wshel@pompompurin.com",
            },
          ],
        },
        subjects: [
          {
            id: "1337",
            name: "wshel@pompompurin.com",
            email: "wshel@pompom.com",
            domain: "pompom.com",
            subject_type: "user",
          },
        ],
      },
    ],
    variant: "DA:1337",
    computed: [
      {
        name: "alert_description",
        value:
          "wshel@pompom.com performed the sensitive action ASSIGN_ROLE at 2023-11-15T20:10:01.757Z, from the IP address 12.34.56.78.9 - The role `users` was granted to the user adm-wshel@pompompurin.com",
        reference: "",
        description: "A human readable description of the alert.",
      },
    ],
    created_at: "2023-11-15T20:16:32Z",
    external_id: "12345678910",
  }

  it("should find the correct path to a boolean value", () => {
    const key = "canary"
    const value = false
    const result = findPath(geigerAlert, key, value)
    expect(result).toBe("$.canary")
  })

  it("should find the correct path to a nested object within an array", () => {
    const key = "original"
    const value = {
      name: "ASSIGN_ROLE",
      type: "DELEGATED_ADMIN_SETTINGS",
      parameters: [
        {
          name: "ROLE_NAME",
          value: "users",
        },
        {
          name: "USER_EMAIL",
          value: "adm-wshel@pompompurin.com",
        },
      ],
    }
    const result = findPath(geigerAlert, key, value)
    expect(result).toBe("$.events[0].original")
  })

  it("should find the correct path to a string within a nested array", () => {
    const key = "email"
    const value = "wshel@pompom.com"
    const result = findPath(geigerAlert, key, value)
    expect(result).toBe("$.events[0].subjects[0].email")
  })

  it("should find the correct path to an object within a nested array", () => {
    const key = "subject_type"
    const value = "user"
    const result = findPath(geigerAlert, key, value)
    expect(result).toBe("$.events[0].subjects[0].subject_type")
  })

  it("should find the correct path to a deeply nested key", () => {
    const key = "description"
    const value = "A human readable description of the alert."
    const result = findPath(geigerAlert, key, value)
    expect(result).toBe("$.computed[0].description")
  })

  const guarddutyAlert = {
    id: "1337",
    ref: "https://pompompurin.com/",
    asset: [
      {
        id: "arn:aws:ec2:us-west-2:133711111111:instance/i-133711111111",
        type: "AwsEc2Instance",
        details: {
          App: "test",
          region: "us-west-2",
          devLead: {
            id: "133711111111",
            email: "test@netflix.com",
            title: "Test Test (test@netflix.com) - Test Test)",
          },
          ContactEmail: "test-dev@netflix.com",
          AwsEc2Instance: {
            Type: "m5.2xlarge",
            VpcId: "vpc-133711111111",
            ImageId: "ami-133711111111",
            SubnetId: "subnet-133711111111",
            LaunchedAt: "2023-12-21T04:40:04.000Z",
            IpV4Addresses: ["1337.1337.1337.1337"],
            IamInstanceProfileArn: "arn:aws:iam::133711111111:instance-profile/test",
          },
          public_facing_guess: false,
        },
      },
    ],
    variant: "AWSGD:18.A",
    createdAt: "2023-12-22T00:29:22.016Z",
    originLocation: [
      {
        flex: "False",
        type: "AwsAccount",
        value: "133711111111",
        unmanaged: "False",
        known_account: "True",
      },
      {
        type: "AwsRegion",
        value: "us-west-2",
      },
      {
        type: "IP",
        geoIP: {
          ip: "1337.1337.1337.1337",
          dma: "reserved",
          lat: "reserved",
          zip: ["reserved"],
          city: "reserved",
          long: "reserved",
          asnum: ["reserved"],
          domain: "reserved",
          company: "Internet_Assigned_Numbers_Authority",
          network: "reserved",
          timezone: "reserved",
          region_code: "reserved",
          country_code: "reserved",
          network_type: "reserved",
          default_answer: false,
          nf_ip_provider: "test",
        },
        value: "1337.1337.1337.1337",
      },
      {
        type: "App",
        value: "test",
        public_facing_guess: false,
      },
    ],
    additionalMetadata: {
      Id: "arn:aws:guardduty:us-west-2:133711111111:detector/133711111111/finding/9cc646957f8d6f8a6faf5d65fdf0b37e",
      Title: "EC2 instance i-133711111111 communicating with disallowed IP address.",
      Types: ["TTPs/Command and Control/UnauthorizedAccess:EC2-MaliciousIPCaller.Custom"],
      Region: "us-west-2",
      Sample: false,
      Severity: {
        Label: "MEDIUM",
        Product: 5,
        Normalized: 50,
      },
      Workflow: {
        Status: "NEW",
      },
      CreatedAt: "2023-12-21T16:17:34.490Z",
      Resources: [
        {
          Id: "arn:aws:ec2:us-west-2:133711111111:instance/i-133711111111",
          Tags: {
            testEnv: "test-prod",
            testcluster: "test-prod-v109-h283",
            "test:cluster": "test-prod-v1",
            "test:stack": "prod",
            "test:details": "runtime",
            "test:application": "test",
            "aws:ec2launchtemplate:id": "lt-133711111111",
            "aws:autoscaling:groupName": "test-prod-runtime-v226",
            "aws:ec2launchtemplate:version": "1",
          },
          Type: "AwsEc2Instance",
          Region: "us-west-2",
          Details: {
            region: "us-west-2",
            AwsEc2Instance: {
              Type: "m5.2xlarge",
              VpcId: "vpc-b61e6ed3",
              ImageId: "ami-0e92f780460b6ae00",
              SubnetId: "subnet-6905be30",
              LaunchedAt: "2023-12-21T04:40:04.000Z",
              IpV4Addresses: ["1337.1337.1337.1337"],
              IamInstanceProfileArn: "arn:aws:iam::133711111111:instance-profile/test",
            },
          },
          Partition: "aws",
        },
      ],
      SourceUrl: "https://pompompurin.com",
      UpdatedAt: "2023-12-22T00:29:22.016Z",
      ProductArn: "arn:aws:securityhub:us-west-2::product/aws/guardduty",
      CompanyName: "Amazon",
      Description:
        "EC2 instance i-133711111111 is communicating with a disallowed IP address 1337.1337.1337.1337 on the list ThreatIntelIOC-IPs.",
      GeneratorId: "arn:aws:guardduty:us-west-2:133711111111:detector/133711111111",
      ProcessedAt: "2023-12-22T06:07:06.586Z",
      ProductName: "GuardDuty",
      RecordState: "ACTIVE",
      AwsAccountId: "133711111111",
      ProductFields: {
        "aws/securityhub/FindingId":
          "arn:aws:securityhub:us-west-2::product/aws/guardduty/arn:aws:guardduty:us-west-2:133711111111:detector/133711111111/finding/9cc646957f8d6f8a6faf5d65fdf0b37e",
        "aws/guardduty/service/count": "8",
        "aws/securityhub/CompanyName": "Amazon",
        "aws/securityhub/ProductName": "GuardDuty",
        "aws/guardduty/service/archived": "false",
        "aws/guardduty/service/detectorId": "133711111111",
        "aws/guardduty/service/serviceName": "guardduty",
        "aws/guardduty/service/resourceRole": "TARGET",
        "aws/guardduty/service/eventLastSeen": "2023-12-22T00:28:55.000Z",
        "aws/guardduty/service/eventFirstSeen": "2023-12-21T16:16:41.000Z",
        "aws/guardduty/service/action/actionType": "NETWORK_CONNECTION",
        "aws/guardduty/service/additionalInfo/type": "default",
        "aws/guardduty/service/additionalInfo/value":
          '{"threatName":"Customer Threat Intel","threatListName":"ThreatIntelIOC-IPs"}',
        "aws/guardduty/service/additionalInfo/threatName": "Customer Threat Intel",
        "aws/guardduty/service/additionalInfo/threatListName": "ThreatIntelIOC-IPs",
        "aws/guardduty/service/action/networkConnectionAction/blocked": "false",
        "aws/guardduty/service/action/networkConnectionAction/protocol": "TCP",
        "aws/guardduty/service/action/networkConnectionAction/connectionDirection": "UNKNOWN",
        "aws/guardduty/service/action/networkConnectionAction/localPortDetails/port": "9031",
        "aws/guardduty/service/evidence/threatIntelligenceDetails.0_/threatListName":
          "ThreatIntelIOC-IPs",
        "aws/guardduty/service/evidence/threatIntelligenceDetails.0_/threatNames.0_":
          "Customer Threat Intel",
        "aws/guardduty/service/action/networkConnectionAction/remotePortDetails/port": "59761",
        "aws/guardduty/service/action/networkConnectionAction/localPortDetails/portName": "Unknown",
        "aws/guardduty/service/action/networkConnectionAction/localIpDetails/ipAddressV4":
          "1337.1337.1337.1337",
        "aws/guardduty/service/action/networkConnectionAction/remotePortDetails/portName":
          "Unknown",
        "aws/guardduty/service/action/networkConnectionAction/remoteIpDetails/ipAddressV4":
          "1337.1337.1337.1337",
        "aws/guardduty/service/action/networkConnectionAction/remoteIpDetails/city/cityName":
          "Test",
        "aws/guardduty/service/action/networkConnectionAction/remoteIpDetails/geoLocation/lat":
          "1337.9187",
        "aws/guardduty/service/action/networkConnectionAction/remoteIpDetails/geoLocation/lon":
          "1337.8598",
        "aws/guardduty/service/action/networkConnectionAction/remoteIpDetails/organization/asn":
          "136308",
        "aws/guardduty/service/action/networkConnectionAction/remoteIpDetails/organization/isp":
          "Test Test Pvt",
        "aws/guardduty/service/action/networkConnectionAction/remoteIpDetails/organization/org":
          "Test Test Pvt",
        "aws/guardduty/service/action/networkConnectionAction/remoteIpDetails/country/countryName":
          "USA",
        "aws/guardduty/service/action/networkConnectionAction/remoteIpDetails/organization/asnOrg":
          "Test Test Pvt Ltd",
      },
      SchemaVersion: "2018-10-08",
      WorkflowState: "NEW",
      AwsAccountName: "AWS",
      LastObservedAt: "2023-12-22T00:28:55.000Z",
      FirstObservedAt: "2023-12-21T16:16:41.000Z",
      UserDefinedFields: {
        "nf:variant": "test:18.A",
        "nf:account_name": "test",
        "nf:origin_region": "us-west-2",
        "nf:origin_account": "133711111111",
      },
      FindingProviderFields: {
        Types: ["TTPs/Command and Control/UnauthorizedAccess:EC2-MaliciousIPCaller.Custom"],
        Severity: {
          Label: "MEDIUM",
          Product: 5,
          Normalized: 50,
        },
      },
    },
  }

  it("should find the correct path to nested key in an object within an array", () => {
    const key = "id"
    const value = "arn:aws:ec2:us-west-2:133711111111:instance/i-133711111111"
    const result = findPath(guarddutyAlert, key, value)
    expect(result).toBe("$.asset[0].id")
    const evaluated = jsonpath.query(guarddutyAlert, result)
    expect(evaluated.includes(value)).toBe(true)
  })

  it("should find the correct path to deeply nested key in an object", () => {
    const key = "devLead"
    const value = {
      id: "133711111111",
      email: "test@netflix.com",
      title: "Test Test (test@netflix.com) - Test Test)",
    }
    const result = findPath(guarddutyAlert, key, value)
    expect(result).toBe("$.asset[0].details.devLead")
    const evaluated = jsonpath.query(guarddutyAlert, result)
    expect(evaluated[0]).toEqual(value)
  })

  it("should find the correct path to a boolean value in a nested object", () => {
    const key = "public_facing_guess"
    const value = false
    const result = findPath(guarddutyAlert, key, value)
    expect(result).toBe("$.asset[0].details.public_facing_guess")
    const evaluated = jsonpath.query(guarddutyAlert, result)
    expect(evaluated[0]).toBe(value)
  })

  it("should find the correct path to an array within a nested object", () => {
    const key = "IpV4Addresses"
    const value = ["1337.1337.1337.1337"]
    const result = findPath(guarddutyAlert, key, value)
    expect(result).toBe("$.asset[0].details.AwsEc2Instance.IpV4Addresses")
    const evaluated = jsonpath.query(guarddutyAlert, result)
    expect(evaluated[0]).toEqual(value)
  })

  it("should find the correct path to a string value within a nested array", () => {
    const key = "value"
    const value = "us-west-2"
    const result = findPath(guarddutyAlert, key, value)
    expect(result).toBe("$.originLocation[1].value")
    const evaluated = jsonpath.query(guarddutyAlert, result)
    expect(evaluated.includes(value)).toBe(true)
  })

  it("should find the correct path to a nested object with array value", () => {
    const key = "geoIP"
    const value = {
      ip: "1337.1337.1337.1337",
      dma: "reserved",
      lat: "reserved",
      zip: ["reserved"],
      city: "reserved",
      long: "reserved",
      asnum: ["reserved"],
      domain: "reserved",
      company: "Internet_Assigned_Numbers_Authority",
      network: "reserved",
      timezone: "reserved",
      region_code: "reserved",
      country_code: "reserved",
      network_type: "reserved",
      default_answer: false,
      nf_ip_provider: "test",
    }
    const result = findPath(guarddutyAlert, key, value)
    expect(result).toBe("$.originLocation[2].geoIP")
    const evaluated = jsonpath.query(guarddutyAlert, result)
    expect(evaluated[0]).toEqual(value)
  })
})
