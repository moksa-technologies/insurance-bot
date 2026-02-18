# Tool Info

This document lists all runtime tools exposed through `ToolExecutor.run(tool_name, args)` and their request/response contracts.

## Available Tools

1. `customer_create_tool`
2. `customer_profile_tool`
3. `pull_registered_profile_tool`
4. `update_email_tool`
5. `update_address_tool`
6. `change_ani_tool`
7. `create_claim_tool`
8. `callback_tool`
9. `hospital_tool`
10. `garage_tool`
11. `rag_kb_tool`

If an unknown tool name is passed, the executor raises:
- `ValueError("Unsupported tool: <tool_name>")`

## Common Notes

- DB-backed tools are pass-through wrappers over PostgreSQL functions.
- For DB tools, if no DB row/function output is returned, gateway fallback is:
  - `{"ok": false, "message": "No response"}` (for mutation tools)
  - `null` (for `customer_profile_tool`)
- Multilingual pipeline translates user input to English before these tools are called.
- `hospital_tool` and `garage_tool` search English Excel data.

## 1) customer_create_tool

### Request

```json
{
  "cust_id": 1010,
  "ani": "9000000010",
  "name": "New Customer",
  "email": "new.customer@example.com",
  "address": "Hyderabad, TS",
  "dob": "1995-05-20"
}
```

Required fields:
- `cust_id`
- `name`

Optional fields:
- `ani` (in orchestration, falls back to request ANI if omitted)
- `email`
- `address`
- `dob`

### Response

Type: `object`

Typical success shape:

```json
{
  "ok": true,
  "message": "Customer created",
  "customer": {
    "cust_id": 1010,
    "ani": "9000000010",
    "name": "New Customer",
    "email": "new.customer@example.com",
    "address": "Hyderabad, TS",
    "dob": "1995-05-20"
  }
}
```

Gateway fallback if no SQL output:

```json
{ "ok": false, "message": "No response", "customer": null }
```

## 2) customer_profile_tool

### Request

```json
{
  "ani": "9000000001"
}
```

### Response

Type: `object | null`

Typical object shape (from SQL function):

```json
{
  "ani": "9000000001",
  "name": "Ravi Kumar",
  "email": "ravi.kumar@example.com",
  "dob": "1990-04-12",
  "policies": [],
  "claims": [],
  "last_chat_summary": {},
  "chat_updated_at": "2026-02-14T10:12:00+05:30"
}
```

Not found:

```json
null
```

## 3) pull_registered_profile_tool

### Request

```json
{
  "ani": "9000000001"
}
```

### Response

Type: `object | null`

Behavior:
- Same as `customer_profile_tool`.
- This is an alias tool intended for flows that explicitly request pulling registered profile details.

Typical object shape:

```json
{
  "ani": "9000000001",
  "name": "Ravi Kumar",
  "email": "ravi.kumar@example.com",
  "dob": "1990-04-12"
}
```

Not found:

```json
null
```

## 4) update_email_tool

### Request

```json
{
  "ani": "9000000001",
  "new_email": "ravi.new@example.com"
}
```

### Response

Type: `object`

Typical success/failure shape (from SQL function):

```json
{
  "ok": true,
  "message": "Email updated",
  "customer": {
    "cust_id": 1001,
    "ani": "9000000001",
    "name": "Ravi Kumar",
    "email": "ravi.new@example.com"
  }
}
```

Possible failures:

```json
{ "ok": false, "message": "Customer not found for given ANI" }
```

```json
{ "ok": false, "message": "Invalid email format" }
```

```json
{ "ok": false, "message": "Email already exists (unique constraint)" }
```

Gateway fallback if no SQL output:

```json
{ "ok": false, "message": "No response" }
```

## 5) update_address_tool

### Request

```json
{
  "ani": "9000000001",
  "new_address": "Flat 12B, Kukatpally, Hyderabad, TS"
}
```

### Response

Type: `object`

Typical shape:

```json
{
  "ok": true,
  "message": "Address updated",
  "customer": {
    "cust_id": 1001,
    "ani": "9000000001",
    "address": "Flat 12B, Kukatpally, Hyderabad, TS"
  }
}
```

Not found:

```json
{ "ok": false, "message": "Customer not found for given ANI" }
```

Gateway fallback:

```json
{ "ok": false, "message": "No response" }
```

## 6) change_ani_tool

### Request

```json
{
  "old_ani": "9000000001",
  "new_ani": "9000000099"
}
```

### Response

Type: `object`

Typical shape:

```json
{
  "ok": true,
  "message": "ANI changed",
  "customer": {
    "ani": "9000000099"
  }
}
```

Possible failures:

```json
{ "ok": false, "message": "New ANI already exists" }
```

```json
{ "ok": false, "message": "Customer not found for old ANI" }
```

Gateway fallback:

```json
{ "ok": false, "message": "No response" }
```

## 7) create_claim_tool

### Request

```json
{
  "ani": "9000000001",
  "vehicle_no": "TS09AB1234",
  "incident_date": "2026-02-16",
  "incident_time": "10:15:00",
  "incident_place": "Hyderabad",
  "damage_type": "Accident",
  "damage_description": "Front bumper scratch",
  "fir_filed": false,
  "fir_no": null
}
```

Required fields:
- `ani`
- `vehicle_no`
- `incident_date`

Optional fields:
- `incident_time`
- `incident_place`
- `damage_type`
- `damage_description`
- `fir_no`

`fir_filed` defaults to `false` if missing.

### Response

Type: `object`

Typical shape:

```json
{
  "ok": true,
  "message": "Claim created",
  "claim": {
    "claim_id": 6,
    "cust_id": 1001,
    "vehicle_no": "TS09AB1234"
  }
}
```

Possible failures:

```json
{ "ok": false, "message": "Customer not found for given ANI" }
```

```json
{ "ok": false, "message": "Vehicle number is required" }
```

Gateway fallback:

```json
{ "ok": false, "message": "No response" }
```

## 8) callback_tool

### Request

```json
{
  "cust_id": 1001,
  "ani": "9000000001",
  "phone": "9876543210",
  "reason": "Need renewal details",
  "preferred_from": "2026-02-17T14:00:00+05:30",
  "preferred_to": "2026-02-17T17:00:00+05:30",
  "scheduled_at": null,
  "status": null,
  "priority": 3,
  "assigned_to": "agent_01"
}
```

All fields are optional.

Defaults:
- `priority = 3`
- If `ani` is missing in orchestration flow, request ANI is used automatically.

### Response

Type: `object`

Typical success shape:

```json
{
  "ok": true,
  "message": "Callback created",
  "callback": {
    "callback_id": 11,
    "cust_id": 1001,
    "ani": "9000000001",
    "phone": "9876543210",
    "reason": "Need renewal details",
    "preferred_from": "2026-02-17T14:00:00+05:30",
    "preferred_to": "2026-02-17T17:00:00+05:30",
    "scheduled_at": null,
    "status": "Requested",
    "priority": 3,
    "assigned_to": "agent_01"
  }
}
```

Gateway fallback if no SQL output:

```json
{ "ok": false, "message": "No response", "callback": null }
```

## 9) hospital_tool

### Request

```json
{
  "area": "Kukatpally",
  "city": "Hyderabad",
  "pincode": "500072",
  "limit": 5
}
```

All fields are optional except operationally you should pass location inputs.

Defaults:
- `limit = 5`

### Response

Type: `array<object>`

Matching rule:
- If 2 or 3 location inputs are provided (`area`, `city`, `pincode`), hospitals are returned when any 2 match in the same row.
- If only 1 location input is provided, a single-field match is enough.

Output rows include available columns among:
- `name`
- `address`
- `phone`
- `pincode`

Example:

```json
[
  {
    "name": "City Hospital",
    "address": "Main Road, Kukatpally, Hyderabad",
    "phone": "9999999999",
    "pincode": "500072"
  }
]
```

No match or empty Excel:

```json
[]
```

## 10) garage_tool

### Request

```json
{
  "area": "Kukatpally",
  "city": "Hyderabad",
  "pincode": "500072",
  "vehicle_type": "car",
  "manufacturer": "hyundai",
  "limit": 5
}
```

All fields optional.

Defaults:
- `limit = 5`

### Response

Type: `array<object>`

Behavior:
- Rows are ranked by score (pincode/city/area/vehicle_type/manufacturer matches).
- Returns top N rows.
- Keys come from garage Excel headers (lowercased), values normalized to strings.

Common keys used by orchestration:
- `garage_name`
- `mobile_no`
- `contact_number`
- `contact_person`
- `city`
- `pincode`
- `address`
- `product`
- `manufacturer`

Example:

```json
[
  {
    "garage_name": "Rapid Garage",
    "mobile_no": "8888888888",
    "city": "Hyderabad",
    "pincode": "500072",
    "address": "Kukatpally Main Road"
  }
]
```

No match:

```json
[]
```

## 11) rag_kb_tool

### Request

```json
{
  "query_en": "What is included in roadside assistance coverage?",
  "top_k": 4
}
```

Required:
- `query_en`

Defaults:
- `top_k = 4`

### Response

Type: `array<object>`

Each item:
- `source_file` (string)
- `page_number` (number)
- `snippet` (string, truncated chunk text)
- `score` (number)

Example:

```json
[
  {
    "source_file": "policy_faq.pdf",
    "page_number": 3,
    "snippet": "Roadside assistance includes towing...",
    "score": 0.83
  }
]
```

If index/documents are unavailable:

```json
[]
```
