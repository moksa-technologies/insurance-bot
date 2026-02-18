# Insurence Bot v1.0

DDD-based multilingual agentic insurance chatbot with ANI-first tooling, emergency orchestration, Excel assistance lookup, PDF RAG, REST + WebSocket APIs, and SaaS web UI.

## Features

- ANI-based customer tools backed by PostgreSQL functions:
  - `customer_create`
  - `get_customer_profile_by_ani`
  - `update_customer_email_by_ani`
  - `update_customer_address_by_ani`
  - `change_customer_ani`
  - `create_claim_by_ani`
  - `callback_create`
- Single-prompt LLM orchestration (`Priya`) for intent handling, multilingual response, and tool planning.
- Emergency and roadside handling via unified conversational workflow in one agent prompt.
- Hospital/Garage lookup from Excel files (`data/excel`).
- Hospital lookup supports field-wise matching and returns results when any two of `area/city/pincode` match.
- RAG from English PDFs with FAISS + OpenAI embeddings (`text-embedding-3-small`).
- REST and WebSocket chat contracts.
- Responsive SaaS UI with collapsible sidebar, top branding bar, and theme switch.
- Detailed external logs with rotating file output and JSON transcript persistence per ANI/session.

## Architecture

```text
app/
  domain/
    customer, claims, assistance, knowledge, conversation
  application/
    orchestration/
    use_cases/
  infrastructure/
    db/
    tools/
    llm/
    retrieval/
    external/
  interfaces/
    api/
    ws/
    ui/
```

## Prerequisites

- Python 3.11+
- PostgreSQL with `demo_insurence` database
- `psql` available in PATH

## Setup

1. Install dependencies.

```powershell
pip install -r requirements.txt
```

2. Create env file.

```powershell
copy .env.example .env
```

3. Update `.env` values:

- DB credentials
- LLM key/base/model (`LLM_OPENAI_*`)
- Embedding key/base/model (`EMBEDDING_OPENAI_*`)

4. Add PDFs for KB (English):

- Put files in `data/pdfs/`

## Database Bootstrap and Verification

From repo root:

```powershell
.\scripts\bootstrap_db.ps1
```

Optional seed:

```powershell
.\scripts\bootstrap_db.ps1 -Seed
```

Verify functions:

```powershell
.\scripts\verify_db.ps1
```

## Run

```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

UI: `http://localhost:8000/`

## Deployment Scripts

### Windows (PowerShell)

```powershell
.\scripts\deploy_windows.ps1
```

Options:
- `-SkipBootstrap`
- `-SkipVerify`
- `-NoStart`
- `-Seed`
- `-Port 8000`
- `-Workers 1`

Example:

```powershell
.\scripts\deploy_windows.ps1 -Port 8000 -Workers 2
```

If an old `.venv` was created with Python 3.10, recreate it:

```powershell
.\scripts\deploy_windows.ps1 -RecreateVenv
```

### Linux (Bash)

```bash
chmod +x scripts/bootstrap_db.sh scripts/verify_db.sh scripts/deploy_linux.sh
./scripts/deploy_linux.sh
```

Options:
- `--skip-bootstrap`
- `--skip-verify`
- `--no-start`
- `--seed`
- `--port 8000`
- `--workers 1`

Example:

```bash
./scripts/deploy_linux.sh --port 8000 --workers 2
```

If needed, pin interpreter explicitly:

```bash
./scripts/deploy_linux.sh --python python3.11
```

If an old `.venv` was created with Python 3.10, recreate it:

```bash
./scripts/deploy_linux.sh --recreate-venv
```

## Service Installers

### Windows Service (NSSM)

Prerequisite: install `nssm.exe` and run PowerShell as Administrator.

Install and start service:

```powershell
.\scripts\install_service_windows.ps1 -ServiceName InsurenceBot -Port 8000 -Workers 2
```

Install only (do not start):

```powershell
.\scripts\install_service_windows.ps1 -ServiceName InsurenceBot -NoStart
```

Reinstall existing service:

```powershell
.\scripts\install_service_windows.ps1 -ServiceName InsurenceBot -ForceReinstall
```

Uninstall service:

```powershell
.\scripts\uninstall_service_windows.ps1 -ServiceName InsurenceBot
```

Uninstall service and remove service log files:

```powershell
.\scripts\uninstall_service_windows.ps1 -ServiceName InsurenceBot -RemoveLogs
```

### Linux Service (systemd)

Prerequisite: run with `sudo` on a systemd-based Linux host.

Install and start service:

```bash
sudo ./scripts/install_service_linux.sh --service-name insurence-bot --port 8000 --workers 2
```

Install only (skip setup if already prepared):

```bash
sudo ./scripts/install_service_linux.sh --service-name insurence-bot --skip-setup
```

Uninstall service:

```bash
sudo ./scripts/uninstall_service_linux.sh --service-name insurence-bot
```

Uninstall and remove log files:

```bash
sudo ./scripts/uninstall_service_linux.sh --service-name insurence-bot --remove-logs --project-root "$(pwd)"
```

## Admin UI (CRUD Console)

- The root page (`/`) serves a responsive admin SPA for database operations on:
  - `customer`
  - `customer_policies`
  - `claim`
  - `chat_summary`
- UI features:
  - Collapsible sidebar with active section highlighting.
  - Top bar branding, theme switch (light/dark), and animated settings dropdown.
  - Search, sortable table headers, pagination, create/view/edit modals, and delete confirmation.
  - Toast notifications for success/error actions.

## Admin CRUD APIs

### Dashboard

- `GET /api/v1/admin/dashboard`

### Customers (`customer`)

- `GET /api/v1/admin/customers`
- `GET /api/v1/admin/customers/{cust_id}`
- `POST /api/v1/admin/customers`
- `PATCH /api/v1/admin/customers/{cust_id}`
- `DELETE /api/v1/admin/customers/{cust_id}`

### Policies (`customer_policies`)

- `GET /api/v1/admin/policies`
- `GET /api/v1/admin/policies/{policy_no}`
- `POST /api/v1/admin/policies`
- `PATCH /api/v1/admin/policies/{policy_no}`
- `DELETE /api/v1/admin/policies/{policy_no}`

### Claims (`claim`)

- `GET /api/v1/admin/claims`
- `GET /api/v1/admin/claims/{claim_id}`
- `POST /api/v1/admin/claims`
- `PATCH /api/v1/admin/claims/{claim_id}`
- `DELETE /api/v1/admin/claims/{claim_id}`

### Chat Summaries (`chat_summary`)

- `GET /api/v1/admin/chat-summaries`
- `GET /api/v1/admin/chat-summaries/{cust_id}`
- `POST /api/v1/admin/chat-summaries`
- `PATCH /api/v1/admin/chat-summaries/{cust_id}`
- `DELETE /api/v1/admin/chat-summaries/{cust_id}`

### Callbacks (`call_back`) - Function Backed

- `GET /api/v1/admin/callbacks` (queue/list via `callback_queue`)
- `GET /api/v1/admin/callbacks/{callback_id}` (`callback_get`)
- `POST /api/v1/admin/callbacks` (`callback_create`)
- `PATCH /api/v1/admin/callbacks/{callback_id}` (`callback_update_patch`)
- `POST /api/v1/admin/callbacks/{callback_id}/attempt` (`callback_mark_attempt`)
- `DELETE /api/v1/admin/callbacks/{callback_id}` (`callback_delete`)

### Query Parameters (List Endpoints)

- `search` (string, optional)
- `page` (default `1`)
- `page_size` (default `10`, max `100`)
- `sort_by` (resource-specific sortable column)
- `sort_dir` (`asc` or `desc`)

### Patch Semantics

- PATCH endpoints use optional fields.
- If a field is passed as `null`, it is treated as "no change" in repository update logic.

## API Contract

### POST `/api/v1/chat`

Request:

```json
{
  "ani": "9000000001",
  "session_uuid": "optional",
  "input_message": "I had an accident",
  "channel": "web"
}
```

Response:

```json
{
  "session_uuid": "...",
  "language": "en",
  "response": "...",
  "follow_up_needed": true,
  "follow_up_query": "...",
  "intent": "accident_emergency",
  "data_references": {
    "database_function": "get_customer_profile_by_ani",
    "external_source": null
  }
}
```

### WS `/ws/chat`

- Accepts same payload as `/api/v1/chat`.
- Returns same response envelope.

### Other Endpoints

- `GET /health`
- `POST /admin/reload-assets`
- `GET /admin/tools/self-test`

## Tests

```powershell
python -m pytest -q
```

## Notes

- Excel assets are repo-local at `data/excel/hospitals.xlsx` and `data/excel/garages.xlsx`.
- FAISS artifacts are persisted in `data/vector`.
- App logs are written to `logs/app.log` (configurable via `APP_LOG_FILE`).
- Chat transcripts are written as JSON files under `logs/transcripts` (configurable via `TRANSCRIPT_DIR`).
- If no PDFs are present, RAG endpoints still work with graceful fallback messages.
