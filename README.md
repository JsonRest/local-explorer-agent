# 🗺️ Local Explorer Agent
**Track 2 Challenge — ADK + MCP Data Integration**

An AI-powered local discovery agent built with **Google ADK** and the **Google Maps Grounding Lite MCP server**. Ask it to find places, check the weather, or plan routes — it retrieves live, grounded data from Google Maps before answering.

<img width="1615" height="845" alt="track2projectdemo" src="https://github.com/user-attachments/assets/bd76d1ac-6bbe-48b7-bb4e-67752af26218" />

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

Clone the repo and navigate into it:

```bash
git clone https://github.com/YOUR_USERNAME/local-explorer-agent.git
cd local-explorer-agent
```

Create the virtual environment and install all dependencies:

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

### 5. Enable APIs & Permissions

Set your project and account variables:

```bash
export PROJECT_ID=$(gcloud config get project)
export USER_EMAIL=$(gcloud config get account)
```

Enable the required APIs:

```bash
gcloud services enable aiplatform.googleapis.com mapstools.googleapis.com
```

Enable the MCP server interface:

```bash
gcloud beta services mcp enable mapstools.googleapis.com
```

Grant the MCP tool user role:

```bash
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="user:$USER_EMAIL" \
  --role="roles/mcp.toolUser"
```

Create a Maps API key restricted to Maps Grounding Lite:

```bash
gcloud alpha services api-keys create \
  --display-name="Local Explorer Maps Key" \
  --api-target=service=mapstools.googleapis.com
```

Copy the printed key string into `local_explorer/.env` as `MAPS_API_KEY`.

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
  --env_vars="MAPS_API_KEY=$MAPS_API_KEY,GOOGLE_GENAI_USE_VERTEXAI=True,GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_CLOUD_LOCATION=us-central1" \
  local_explorer
```

After deployment, note the Cloud Run URL printed by ADK. Test with:

```bash
curl -X POST <CLOUD_RUN_URL>/run \
  -H "Content-Type: application/json" \
  -d '{"message": "Find coffee shops in Makati, Manila"}'
```

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
