# 🗺️ Local Explorer Agent
**Track 2 Challenge — ADK + MCP Data Integration**

An AI-powered local discovery agent built with **Google ADK** and the **Google Maps Grounding Lite MCP server**. Ask it to find places, check the weather, or plan routes — it retrieves live, grounded data from Google Maps before answering.

---

## Architecture

```
User Query
    │
    ▼
ADK LlmAgent (Gemini on Vertex AI)
    │
    └── MCPToolset ──► https://mapstools.googleapis.com/mcp
                            ├── search_places
                            ├── lookup_weather
                            └── compute_routes
```

---

## Prerequisites

| Requirement | Details |
|---|---|
| Google Cloud project | Billing enabled |
| Python | 3.10+ |
| uv | Fast Python package manager — [install guide](https://docs.astral.sh/uv/getting-started/installation/) |
| Google Cloud CLI | [install guide](https://cloud.google.com/sdk/docs/install) |
| Vertex AI API | `gcloud services enable aiplatform.googleapis.com` |
| Maps Grounding Lite API | `gcloud services enable mapstools.googleapis.com` |
| Maps MCP interface | `gcloud beta services mcp enable mapstools.googleapis.com` |
| IAM role | `roles/mcp.toolUser` on your GCP project |
| Maps API Key | With Maps Grounding Lite API enabled |

---

## Google Cloud Project Setup

### 1. Create a Google Cloud Project

Go to [console.cloud.google.com](https://console.cloud.google.com) and sign in with your Google account.

Click the project dropdown at the top of the page, then click **New Project**. Enter a project name (e.g. `local-explorer-agent`), then click **Create**.

Wait a few seconds for the project to be created, then select it from the dropdown to make it your active project.

### 2. Enable Billing

Go to **Billing** in the left menu and link a billing account to your project. A billing account is required to use Vertex AI and Maps APIs. New accounts receive $300 in free credits.

### 3. Install the Google Cloud CLI

Download and install the gcloud CLI from [cloud.google.com/sdk/docs/install](https://cloud.google.com/sdk/docs/install).

After installation, initialise it:

```bash
gcloud init
```

Follow the prompts to sign in and select your project.

### 4. Set your Project ID

```bash
gcloud config set project YOUR_PROJECT_ID
```

Verify it is set correctly:

```bash
gcloud config get project
```

---

## Maps API Key Setup

### 1. Enable the Required APIs

```bash
gcloud services enable aiplatform.googleapis.com mapstools.googleapis.com
```

### 2. Enable the MCP Server Interface

```bash
gcloud beta services mcp enable mapstools.googleapis.com
```

### 3. Grant the MCP Tool User Role

```bash
export PROJECT_ID=$(gcloud config get project)
export USER_EMAIL=$(gcloud config get account)

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="user:$USER_EMAIL" \
  --role="roles/mcp.toolUser"
```

### 4. Create the API Key

```bash
gcloud alpha services api-keys create \
  --display-name="Local Explorer Maps Key" \
  --api-target=service=mapstools.googleapis.com
```

### 5. Retrieve the Key String

```bash
gcloud alpha services api-keys get-key-string \
  $(gcloud alpha services api-keys list \
    --filter="displayName='Local Explorer Maps Key'" \
    --format="value(name)")
```

Copy the printed key string — you will paste it into `local_explorer/.env` as `MAPS_API_KEY` in the Quick Start steps below.

> **Alternative (UI):** Go to **APIs & Services → Credentials** in the Cloud Console, click **+ Create Credentials → API key**, copy the key, then click **Edit API key** and restrict it to **Maps Grounding Lite API** under API restrictions.

---

## Quick Start (Local Machine)

### 1. Install uv

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.sh | iex"
```

### 2. Clone & Set Up Environment

Make sure all project files are committed and pushed to the repository before running these steps (the repo must not be empty).

If you have not cloned the repo yet:

```bash
git clone https://github.com/YOUR_USERNAME/local-explorer-agent.git
cd local-explorer-agent
```

If you already cloned it previously, just navigate into the existing folder:

```bash
cd local-explorer-agent
```

Then create the virtual environment and install all dependencies:

```bash
uv sync
```

### 3. Configure Environment

Copy the env template into the agent package folder:

```bash
cp .env.example local_explorer/.env
```

Then open `local_explorer/.env` in a text editor and fill in your `GOOGLE_CLOUD_PROJECT` and `MAPS_API_KEY`.

### 4. Authenticate

```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

### 5. Verify APIs & Permissions

If you have already completed the **Maps API Key Setup** section above, your APIs and IAM role are already configured. Just confirm your project is set:

```bash
gcloud config get project
```

If you skipped that section, go back and complete it before continuing.

### 6. Run Locally

Launch the interactive web UI — opens automatically at http://localhost:8000:

```bash
uv run adk web
```

Or run in CLI mode:

```bash
uv run adk run local_explorer
```

### 7. Deploy to Cloud Run

Read your Maps API key from the env file:

```bash
export MAPS_API_KEY=$(grep MAPS_API_KEY local_explorer/.env | cut -d= -f2)
```

Deploy to Cloud Run:

```bash
uv run adk deploy cloud_run \
  --project=$PROJECT_ID \
  --region=us-central1 \
  --service_name=local-explorer-agent \
  --with_ui \
  local_explorer \
  -- \
  --set-env-vars="MAPS_API_KEY=$MAPS_API_KEY,GOOGLE_GENAI_USE_VERTEXAI=True,GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_CLOUD_LOCATION=us-central1"
```

> The `--` separator passes everything after it directly to `gcloud run deploy`. Environment variables must go after `--` using `--set-env-vars`.
> The `--with_ui` flag bundles the ADK web UI into the Cloud Run service so you can access the chat interface directly from the Cloud Run URL.

After deployment, note the Cloud Run URL printed by ADK.

**Option 1 — Browser (ADK Web UI)**

Since the service is deployed with `--with_ui`, open the Cloud Run URL directly in your browser to get the full ADK chat interface:

```
<CLOUD_RUN_URL>
```

For the interactive API docs (Swagger UI):

```
<CLOUD_RUN_URL>/docs
```

To list available agents:

```
<CLOUD_RUN_URL>/list-apps
```

**Option 2 — Postman**

Postman also requires creating a session first.

Create the session — new POST request:
- URL: `<CLOUD_RUN_URL>/apps/local_explorer/users/test-user/sessions/test-session-1`
- Body → raw → JSON: `{}`
- Click Send

Then send a message — new POST request:
- URL: `<CLOUD_RUN_URL>/run`
- Body → raw → JSON:
```json
{
  "appName": "local_explorer",
  "userId": "test-user",
  "sessionId": "test-session-1",
  "newMessage": {
    "role": "user",
    "parts": [{ "text": "Find coffee shops near BGC, Taguig" }]
  }
}
```
- Click Send

**Option 3 — curl**

The ADK endpoint requires creating a session before sending a message.

First, create a session:

```bash
curl -X POST <CLOUD_RUN_URL>/apps/local_explorer/users/test-user/sessions/test-session-1 \
  -H "Content-Type: application/json" \
  -d '{}'
```

Then send your message:

```bash
curl -X POST <CLOUD_RUN_URL>/run \
  -H "Content-Type: application/json" \
  -d '{
    "appName": "local_explorer",
    "userId": "test-user",
    "sessionId": "test-session-1",
    "newMessage": {
      "role": "user",
      "parts": [{ "text": "Find coffee shops near BGC, Taguig" }]
    }
  }'
```

The required fields are:
- `appName` — must match the agent folder name (`local_explorer`)
- `userId` — any string identifying the user
- `sessionId` — any string identifying the session (must be created first)
- `newMessage` — the message object with `role` and `parts`

---

## Example Interactions

**Finding places:**
```
User: Find family-friendly restaurants near BGC, Taguig
Agent: Here are 5 top family-friendly restaurants near BGC: ...
```

**Weather check:**
```
User: What's the weather in Cebu this weekend?
Agent: In Cebu City this weekend, expect partly cloudy skies...
```

**Route planning:**
```
User: How long does it take to drive from Makati to the airport?
Agent: Driving from Makati CBD to NAIA Terminal 3 takes approximately 35-45 minutes...
```

---

## Project Structure

```
local-explorer-agent/
├── local_explorer/          ← ADK agent package (underscore required)
│   ├── __init__.py          ← marks folder as Python package
│   ├── agent.py             ← root_agent definition + MCP toolset
│   └── .env                 ← env vars (never commit this)
├── pyproject.toml           ← uv-native dependency management
├── requirements.txt         ← kept for Cloud Run build compatibility
├── .env.example             ← env var template
├── .gitignore
└── README.md
```

> **Key rule:** Always run `adk run`, `adk web`, and `adk deploy` from the repo root, never from inside `local_explorer/`.

---

## Dependency Management

This project uses **uv** for fast, reproducible dependency management.

Install all dependencies (first time or after pulling changes):

```bash
uv sync
```

Add a new dependency:

```bash
uv add <package>
```

Run any command inside the managed environment:

```bash
uv run <command>
```

> `requirements.txt` is kept alongside `pyproject.toml` because `adk deploy cloud_run` uses it during the Cloud Run build process.

---

## Known Issue & Fix: MCP Timeout

The ADK default timeout for MCP servers is 5 seconds, which is too short for the remote `mapstools.googleapis.com` server on first connection. This agent sets `timeout=30` in `StreamableHTTPConnectionParams` to avoid `Failed to get tools from MCP server` errors.

---

## Clean Up

```bash
gcloud run services delete local-explorer-agent --region=us-central1 --quiet
gcloud artifacts repositories delete cloud-run-source-deploy --location=us-central1
```
