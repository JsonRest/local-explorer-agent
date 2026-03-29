"""
Local Explorer Agent  ·  Track 2 Challenge
===========================================
An AI agent that uses Google Maps Grounding Lite via MCP to help users
discover places, check the weather, and compute routes in any location.

Architecture
  ADK (LlmAgent)
    └── MCPToolset → https://mapstools.googleapis.com/mcp
          ├── search_places
          ├── lookup_weather
          └── compute_routes

Run locally
  cd <repo-root>
  adk web --host=0.0.0.0 --allow_origins="*"        # Cloud Shell
  adk run local_explorer                              # CLI

Deploy
  adk deploy cloud_run \\
    --project=$PROJECT_ID \\
    --region=us-central1 \\
    --service_name=local-explorer-agent \\
    --env_vars="MAPS_API_KEY=$MAPS_API_KEY,GOOGLE_GENAI_USE_VERTEXAI=True,GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_CLOUD_LOCATION=us-central1" \\
    local_explorer
"""

import os
import dotenv

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams

# ── Environment ───────────────────────────────────────────────────────────────
dotenv.load_dotenv()

MODEL       = os.getenv("MODEL",       "gemini-2.5-flash")
MAPS_API_KEY = os.getenv("MAPS_API_KEY", "")

# Google-managed Maps Grounding Lite MCP endpoint
MAPS_MCP_URL = "https://mapstools.googleapis.com/mcp"

# ── MCP Toolset ───────────────────────────────────────────────────────────────
# timeout=30 avoids the default 5-second timeout that causes failures on
# the first cold connection to the remote Maps MCP server.
maps_toolset = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=MAPS_MCP_URL,
        headers={"X-Goog-Api-Key": MAPS_API_KEY},
        timeout=30,
    )
)

# ── Agent Definition ──────────────────────────────────────────────────────────
root_agent = LlmAgent(
    name="local_explorer",
    model=MODEL,
    description=(
        "An AI agent that helps users discover local places, check the weather,"
        " and plan routes using live Google Maps data via MCP."
    ),
    instruction="""
You are Local Explorer, a helpful AI guide for location discovery and travel planning.

You have access to three tools from the Google Maps Grounding Lite MCP server:
  • search_places   — find businesses, attractions, restaurants, landmarks, etc.
  • lookup_weather  — get current weather and forecasts for any location
  • compute_routes  — calculate travel time and distance between two points

HOW TO RESPOND
--------------
1. Always use the tools to retrieve real, grounded data before answering.
2. After getting tool results, synthesize the information into a clear,
   friendly, and well-structured response.
3. For place searches, present results with name, address, rating (if available),
   and a brief description. Limit to the 5 most relevant results.
4. For weather, report current conditions and any important upcoming changes.
5. For routes, report the primary route distance, estimated duration, and
   travel mode used.
6. If the user's query requires multiple tools (e.g., "find a restaurant near
   me and tell me how to get there from downtown"), chain the tool calls.
7. If a location is ambiguous, ask a single clarifying question.
8. Keep responses concise and practical. Use bullet points for lists.

EXAMPLE PROMPTS USERS MAY ASK
------------------------------
• "Find me coffee shops in Makati, Manila"
• "What's the weather like in Cebu this weekend?"
• "How long does it take to drive from BGC to Makati?"
• "Find family-friendly restaurants near SM Mall of Asia"
• "Best tourist spots in Palawan"
""",
    tools=[maps_toolset],
)
