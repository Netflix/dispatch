-- install `brew install wrk`
-- usage `wrk -t12 -c400 -d30s -H 'Authorization: Bearer xxxxx' -s tests/performance/signalInstances.lua http://localhost:8000/api/v1/default/signals/instances`

local wrk = require("wrk")

local requestJson = [[{"project": {"name": "Test"}, "raw": {
	"variant": "DA:1040.A",
	"createdAt": "1681332053916",
	"additionalMetadata": {
		"ipaddress": "192.168.1.1",
		"role_name": "admin",
		"timestamp": "2023-04-12T20:31:26.364Z",
		"alert_name": "Google Admin Sensitive Actions",
		"event_name": "ASSIGN_ROLE",
		"netflix_id": "",
		"user_email": "test@netflix.com",
		"admin_email": "wshel@netflix.com",
		"alert_variant": "A"
	}
}}]]

local headers = {
  ["Content-Type"] = "application/json"
}

local function merge_headers(cli_headers, local_headers)
  -- Create a new headers table
  local merged_headers = {}

  -- Copy CLI headers to the merged_headers table
  for key, value in pairs(cli_headers) do
    merged_headers[key] = value
  end

  -- Copy local headers to the merged_headers table, overwriting any conflicting headers
  for key, value in pairs(local_headers) do
    merged_headers[key] = value
  end

  return merged_headers
end

-- function response(status, headers, body)
--  io.write("Response status: ", status, "\n")
--  io.write("Response body: ", body, "\n")
--  io.write("Response message: ", wrk.format(nil, nil, nil, status_text), "\n")
-- end

-- Request function
function request()
  local req_headers = merge_headers(wrk.headers, headers)

  local body = requestJson

  -- Create the request object
  local req = wrk.format("POST", endpoint, req_headers, body)

  -- Return the request object
  return req
end
