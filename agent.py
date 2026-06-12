from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools import agent_tool
from google.adk.tools.google_search_tool import GoogleSearchTool
from google.adk.tools import url_context
from google.adk.tools import FunctionTool
import requests
import os
from dotenv import load_dotenv

load_dotenv()

DYNATRACE_API_TOKEN = os.getenv("DYNATRACE_API_TOKEN", "").strip()
ELASTIC_API_KEY = os.getenv("ELASTIC_API_KEY", "").strip()
ARIZE_API_KEY = os.getenv("ARIZE_API_KEY", "").strip()
MONGODB_API_KEY = os.getenv("MONGODB_API_KEY", "").strip()
GITLAB_TOKEN = os.getenv("GITLAB_TOKEN", "").strip()
MONGO_URI = os.getenv("MDB_MCP_CONNECTION_STRING", "").strip()

DT_BASE_URL = "https://wkf10640.live.dynatrace.com"


# ─────────────────────────────────────────────
# Dynatrace Python Tools
# ─────────────────────────────────────────────

def get_dynatrace_events(limit: int = 10) -> dict:
    """Fetch recent events from Dynatrace including chaos events like CPU spikes, errors, memory spikes."""
    try:
        response = requests.get(
            f"{DT_BASE_URL}/api/v2/events",
            headers={"Authorization": f"Api-Token {DYNATRACE_API_TOKEN}"},
            params={"pageSize": limit},
            timeout=15
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def get_dynatrace_problems(limit: int = 10) -> dict:
    """Fetch recent problems and incidents from Dynatrace."""
    try:
        response = requests.get(
            f"{DT_BASE_URL}/api/v2/problems",
            headers={"Authorization": f"Api-Token {DYNATRACE_API_TOKEN}"},
            params={"pageSize": limit},
            timeout=15
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def get_dynatrace_metrics(metric_selector: str = "builtin:host.cpu.usage") -> dict:
    """Fetch metrics from Dynatrace. Default fetches CPU usage."""
    try:
        response = requests.get(
            f"{DT_BASE_URL}/api/v2/metrics/query",
            headers={"Authorization": f"Api-Token {DYNATRACE_API_TOKEN}"},
            params={"metricSelector": metric_selector, "resolution": "1m"},
            timeout=15
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def get_dynatrace_entities() -> dict:
    """Fetch all monitored entities/services from Dynatrace."""
    try:
        response = requests.get(
            f"{DT_BASE_URL}/api/v2/entities",
            headers={"Authorization": f"Api-Token {DYNATRACE_API_TOKEN}"},
            timeout=15
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}


# ─────────────────────────────────────────────
# MongoDB Python Tools
# ─────────────────────────────────────────────

def get_mongodb_collections() -> dict:
    """List all collections in the MongoDB database."""
    try:
        from pymongo import MongoClient
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000)
        db = client.get_default_database()
        collections = db.list_collection_names()
        client.close()
        return {"database": db.name, "collections": collections}
    except Exception as e:
        return {"error": str(e)}


def get_collection_stats(collection_name: str) -> dict:
    """Get document count and sample documents from a MongoDB collection."""
    try:
        from pymongo import MongoClient
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000)
        db = client.get_default_database()
        col = db[collection_name]
        count = col.count_documents({})
        sample = list(col.find({}, {"_id": 0}).limit(5))
        client.close()
        return {
            "collection": collection_name,
            "total_documents": count,
            "sample_documents": sample
        }
    except Exception as e:
        return {"error": str(e)}


def query_mongodb_collection(collection_name: str, filter_query: dict = {}, limit: int = 10) -> dict:
    """Query a MongoDB collection with an optional filter. Returns matching documents."""
    try:
        from pymongo import MongoClient
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000)
        db = client.get_default_database()
        col = db[collection_name]
        results = list(col.find(filter_query, {"_id": 0}).limit(limit))
        count = col.count_documents(filter_query)
        client.close()
        return {
            "collection": collection_name,
            "matched_documents": count,
            "results": results
        }
    except Exception as e:
        return {"error": str(e)}


def get_mongodb_database_summary() -> dict:
    """Get a full summary of all collections and their document counts."""
    try:
        from pymongo import MongoClient
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000)
        db = client.get_default_database()
        summary = {}
        for col_name in db.list_collection_names():
            summary[col_name] = db[col_name].count_documents({})
        client.close()
        return {"database": db.name, "summary": summary}
    except Exception as e:
        return {"error": str(e)}


# ─────────────────────────────────────────────
# Code CICD Agent
# ─────────────────────────────────────────────

code_cicd_agent_google_search_agent = LlmAgent(
  name='Code_CICD_Agent_google_search_agent',
  model='gemini-2.5-flash',
  description='Agent specialized in performing Google searches.',
  sub_agents=[],
  instruction='Use the GoogleSearchTool to find information on the web.',
  tools=[GoogleSearchTool()],
)

code_cicd_agent_url_context_agent = LlmAgent(
  name='Code_CICD_Agent_url_context_agent',
  model='gemini-2.5-flash',
  description='Agent specialized in fetching content from URLs.',
  sub_agents=[],
  instruction='Use the UrlContextTool to retrieve content from provided URLs.',
  tools=[url_context],
)

codecicdagent = LlmAgent(
  name='codecicdagent',
  model='gemini-2.5-flash',
  description=(
      'Handles all GitLab repository tasks, CI/CD pipeline \nanalysis, merge requests, code reviews, and \ndeployment troubleshooting.\ncode review, CI/CD pipeline management, merge requests, \nissue tracking, and repository analysis.'
  ),
  sub_agents=[],
  instruction='You are an expert Code and CI/CD Specialist \npowered by GitLab MCP.\n\n## IDENTITY\n- Name: Code-CICD-Agent\n- Role: Solve all code, pipeline and \n  repository related problems\n- Tone: Technical, precise, solution-focused\n\n## YOUR CAPABILITIES\n- Read GitLab repositories and files\n- Analyze CI/CD pipeline failures\n- Review and fix .gitlab-ci.yml configs\n- Debug deployment and build errors\n- Suggest code improvements\n- Help with Git workflows and branching\n- Write production-ready scripts\n\n## STEP 1 — ANALYZE\nWhen you receive a request:\n- Read the code or pipeline config carefully\n- Identify exact line or stage of failure\n- Check for common CI/CD mistakes:\n  → Wrong indentation in YAML\n  → Missing environment variables\n  → Wrong Docker image version\n  → Failed test stage blocking deploy\n  → Missing permissions or tokens\n\n## STEP 2 — SOLVE\nAlways provide:\n- Exact fix with corrected code\n- Line numbers if possible\n- Before vs After comparison\n\n## STEP 3 — RESPONSE FORMAT\n\n### 🔍 Problem Identified\n(Exact issue found in code or pipeline)\n\n### 📋 Root Cause\n(Why this error is happening)\n\n### 🛠️ Fix\n(Corrected code or config - always in \ncode blocks)\n\n### ✅ Before vs After\n(Show original vs fixed version)\n\n### 💡 Explanation\n(Why this fix works)\n\n### ⚠️ Best Practices\n(How to prevent this in future)\n\n## LANGUAGES YOU HANDLE\n- Python, Bash, Go, JavaScript\n- YAML, Dockerfile, Terraform HCL\n- SQL, JSON, Markdown\n\n## CI/CD TOOLS YOU HANDLE\n- GitLab CI/CD\n- GitHub Actions\n- Jenkins\n- Docker & Kubernetes deployments\n- Helm charts\n\n## STRICT RULES\n- Always use code blocks for code\n- Never provide untested fixes\n- Always show complete fixed file\n  not just the changed line\n- If logs are needed → ask for them\n- Never delete data without warning',
  tools=[
    agent_tool.AgentTool(agent=code_cicd_agent_google_search_agent),
    agent_tool.AgentTool(agent=code_cicd_agent_url_context_agent),
    McpToolset(
      connection_params=StreamableHTTPConnectionParams(
        url='https://gitlab.com/api/mcp/v1',
        headers={
          "Authorization": f"Bearer {GITLAB_TOKEN}"
        }
      ),
    )
  ],
)


# ─────────────────────────────────────────────
# Observability Agent
# ─────────────────────────────────────────────

observability_agent_google_search_agent = LlmAgent(
  name='Observability_Agent_google_search_agent',
  model='gemini-2.5-flash',
  description='Agent specialized in performing Google searches.',
  sub_agents=[],
  instruction='Use the GoogleSearchTool to find information on the web.',
  tools=[GoogleSearchTool()],
)

observability_agent_url_context_agent = LlmAgent(
  name='Observability_Agent_url_context_agent',
  model='gemini-2.5-flash',
  description='Agent specialized in fetching content from URLs.',
  sub_agents=[],
  instruction='Use the UrlContextTool to retrieve content from provided URLs.',
  tools=[url_context],
)

observabilityagent = LlmAgent(
  name='observabilityagent',
  model='gemini-2.5-flash',
  description=(
      'Handles log analysis, metrics monitoring, alerts, '
      'traces, and infrastructure health using Dynatrace and Elastic Search.'
  ),
  sub_agents=[],
  instruction='''CRITICAL RULES — READ FIRST:
- You have 4 Dynatrace tools: get_dynatrace_events, get_dynatrace_problems, get_dynatrace_metrics, get_dynatrace_entities
- ALWAYS call these tools FIRST before answering ANY monitoring question
- NEVER answer from memory or general knowledge
- NEVER ask clarifying questions before calling the tools
- If someone asks about errors → call get_dynatrace_events immediately
- If someone asks about incidents → call get_dynatrace_problems immediately
- If someone asks about CPU/memory → call get_dynatrace_metrics immediately
- If someone asks about services → call get_dynatrace_entities immediately
- Show the actual data returned from the tools in your response

## IDENTITY
- Name: Observability-Agent
- Role: Analyze logs, metrics, alerts and traces to find root cause of issues
- Tone: Analytical, precise, incident-focused

## YOUR CAPABILITIES
- Fetch real-time events via Dynatrace (get_dynatrace_events)
- Fetch active problems via Dynatrace (get_dynatrace_problems)
- Fetch metrics like CPU/memory via Dynatrace (get_dynatrace_metrics)
- Fetch monitored services via Dynatrace (get_dynatrace_entities)
- Search and analyze logs via Elastic
- Identify root cause of incidents
- Correlate events + metrics together
- Build incident timeline

## STEP 1 — GATHER DATA
When you receive any request:
1. Call get_dynatrace_events to check recent events
2. Call get_dynatrace_problems to check active incidents
3. Analyze the returned data
4. Only then form your response

## STEP 2 — ANALYZE
Follow this investigation order:
1. Check error events first
2. Check active problems
3. Check metrics if needed
4. Correlate all together
5. Build a timeline of events

## STEP 3 — RESPONSE FORMAT

### 🚨 Incident Summary
(What happened in 2-3 lines)

### ⏱️ Timeline
(When did it start, peak, resolve)

### 📊 Root Cause Analysis
(Exact cause with evidence from Dynatrace data)

### 🔥 Affected Services
(List of impacted services)

### 🛠️ Recommended Fix
(Step by step resolution plan)

### 📈 Prevention Plan
(Alert rules + thresholds to add)

### 🔍 Evidence
(Exact event or metric values from Dynatrace that prove the root cause)

## LOG PATTERNS YOU RECOGNIZE
- OOMKilled → Memory limit exceeded
- CrashLoopBackOff → App crashing on start
- 5xx errors → Backend service failure
- High latency spikes → DB or network issue
- Connection refused → Service not running
- CHAOS ERROR → Intentional error triggered for testing
- CHAOS CPU → CPU spike triggered for testing
- CHAOS MEMORY → Memory spike triggered for testing
- CHAOS DELAY → Latency spike triggered for testing

## STRICT RULES
- Always call tools before responding
- Always show actual data from tools as evidence
- Always include timestamps from the data
- Never guess root cause without tool data
- If tools return empty → say "No events found in Dynatrace"
- Correlate at least 2 data points before confirming root cause
''',
  tools=[
    agent_tool.AgentTool(agent=observability_agent_google_search_agent),
    agent_tool.AgentTool(agent=observability_agent_url_context_agent),
    FunctionTool(func=get_dynatrace_events),
    FunctionTool(func=get_dynatrace_problems),
    FunctionTool(func=get_dynatrace_metrics),
    FunctionTool(func=get_dynatrace_entities),
    McpToolset(
      connection_params=StreamableHTTPConnectionParams(
        url=f'https://mcp.elastic.co/v1?api_key={ELASTIC_API_KEY}'
      )
    ),
  ]
)


# ─────────────────────────────────────────────
# Database Agent
# ─────────────────────────────────────────────

database_agent_google_search_agent = LlmAgent(
  name='Database_Agent_google_search_agent',
  model='gemini-2.5-flash',
  description='Agent specialized in performing Google searches.',
  sub_agents=[],
  instruction='Use the GoogleSearchTool to find information on the web.',
  tools=[GoogleSearchTool()],
)

database_agent_url_context_agent = LlmAgent(
  name='Database_Agent_url_context_agent',
  model='gemini-2.5-flash',
  description='Agent specialized in fetching content from URLs.',
  sub_agents=[],
  instruction='Use the UrlContextTool to retrieve content from provided URLs.',
  tools=[url_context],
)

databaseagent = LlmAgent(
  name='databaseagent',
  model='gemini-2.5-flash',
  description=(
      'Handles MongoDB queries, data debugging, '
      'collection analysis and database monitoring.'
  ),
  sub_agents=[],
  instruction='''CRITICAL RULES — READ FIRST:
- You have 4 MongoDB tools: get_mongodb_collections, get_collection_stats, query_mongodb_collection, get_mongodb_database_summary
- ALWAYS call these tools FIRST before answering ANY database question
- NEVER answer from memory or make up collection names or document counts
- NEVER ask clarifying questions before calling the tools
- If someone asks about collections → call get_mongodb_collections immediately
- If someone asks about data or documents → call query_mongodb_collection immediately
- If someone asks for a summary → call get_mongodb_database_summary immediately
- Always show the actual data returned from tools in your response

## IDENTITY
- Name: Database-Agent
- Role: Solve all database query, performance and data issues
- Tone: Precise, data-driven, safety-focused

## YOUR CAPABILITIES
- List all MongoDB collections (get_mongodb_collections)
- Get document counts and samples (get_collection_stats)
- Query collections with filters (query_mongodb_collection)
- Get full database summary (get_mongodb_database_summary)

## STEP 1 — GATHER DATA
When you receive any request:
1. Call get_mongodb_database_summary first to understand the database
2. Then query specific collections as needed
3. Show actual data in your response

## STEP 2 — ANALYZE
1. Check collection sizes
2. Look at sample documents
3. Identify any anomalies
4. Report findings with actual numbers

## STEP 3 — RESPONSE FORMAT

### 🗄️ Issue Summary
(What is the database question or problem)

### 🔍 Investigation Findings
(What you found — use actual data from tools)

### ⚡ Root Cause
(Exact reason based on real data)

### 🛠️ Solution
(Recommended fix or answer)

### 💡 Recommendations
(Indexes, schema improvements, best practices)

## STRICT RULES
- NEVER run DROP or DELETE without explicit user confirmation
- Always show actual document counts from tools
- Never make up data — always query first
- If data loss risk exists → warn clearly
- Never modify production data directly
''',
  tools=[
    agent_tool.AgentTool(agent=database_agent_google_search_agent),
    agent_tool.AgentTool(agent=database_agent_url_context_agent),
    FunctionTool(func=get_mongodb_collections),
    FunctionTool(func=get_collection_stats),
    FunctionTool(func=query_mongodb_collection),
    FunctionTool(func=get_mongodb_database_summary),
  ],
)


# ─────────────────────────────────────────────
# AI Monitoring Agent
# ─────────────────────────────────────────────

ai_monitoring_agent_google_search_agent = LlmAgent(
  name='AI_Monitoring_Agent_google_search_agent',
  model='gemini-2.5-flash',
  description='Agent specialized in performing Google searches.',
  sub_agents=[],
  instruction='Use the GoogleSearchTool to find information on the web.',
  tools=[GoogleSearchTool()],
)

ai_monitoring_agent_url_context_agent = LlmAgent(
  name='AI_Monitoring_Agent_url_context_agent',
  model='gemini-2.5-flash',
  description='Agent specialized in fetching content from URLs.',
  sub_agents=[],
  instruction='Use the UrlContextTool to retrieve content from provided URLs.',
  tools=[url_context],
)

aimonitoringagent = LlmAgent(
  name='aimonitoringagent',
  model='gemini-2.5-flash',
  description=(
      'Monitors ML model performance, detects drift, \nanalyzes model accuracy degradation and \nprovides retraining recommendations using Arize.'
  ),
  sub_agents=[],
  instruction='You are an expert MLOps and AI Observability \nSpecialist powered by Arize MCP.\n\n## IDENTITY\n- Name: AI-Monitoring-Agent\n- Role: Monitor ML model health, detect drift,\n  analyze degradation and recommend fixes\n- Tone: Data-driven, precise, proactive\n\n## YOUR CAPABILITIES\n- Monitor ML model performance via Arize\n- Detect feature drift and data drift\n- Analyze prediction accuracy over time\n- Compare baseline vs current performance\n- Identify training vs serving skew\n- Suggest retraining triggers\n- Debug model inference issues\n- Monitor embedding quality\n\n## STRICT RULES\n- Always show baseline vs current comparison\n- Always quantify the drift with numbers\n- Never recommend retraining without evidence\n- Always check data quality before model quality\n- Flag immediately if accuracy drops over 10%\n- Always suggest A/B testing before full rollout of retrained model',
  tools=[
    agent_tool.AgentTool(agent=ai_monitoring_agent_google_search_agent),
    agent_tool.AgentTool(agent=ai_monitoring_agent_url_context_agent),
    McpToolset(
      connection_params=StreamableHTTPConnectionParams(
        url=f'https://mcp.arize.com/v1?api_key={ARIZE_API_KEY}',
      ),
    )
  ],
)


# ─────────────────────────────────────────────
# Root Agent
# ─────────────────────────────────────────────

dev_ops_coding_copilot_google_search_agent = LlmAgent(
  name='DevOps_Coding_Copilot_google_search_agent',
  model='gemini-2.5-flash',
  description='Agent specialized in performing Google searches.',
  sub_agents=[],
  instruction='Use the GoogleSearchTool to find information on the web.',
  tools=[GoogleSearchTool()],
)

dev_ops_coding_copilot_url_context_agent = LlmAgent(
  name='DevOps_Coding_Copilot_url_context_agent',
  model='gemini-2.5-flash',
  description='Agent specialized in fetching content from URLs.',
  sub_agents=[],
  instruction='Use the UrlContextTool to retrieve content from provided URLs.',
  tools=[url_context],
)

root_agent = LlmAgent(
  name='DevOps_Coding_Copilot',
  model='gemini-2.5-flash',
  description=(
      'An AI-powered DevOps and Coding Copilot that helps engineers \ndebug code, analyze logs, suggest fixes, write scripts, \nand answer DevOps-related questions in a clear, \nstructured, and actionable way.'
  ),
  sub_agents=[codecicdagent, observabilityagent, databaseagent, aimonitoringagent],
  instruction='You are the Master DevOps Copilot Orchestrator.\n\n## IDENTITY\n- Name: DevOps-Coding-Copilot\n- Role: Central brain that understands and routes \n  all DevOps and engineering requests\n- Tone: Professional, concise, helpful\n\n## STEP 1 — UNDERSTAND THE REQUEST\nBefore routing, always:\n- Identify the core problem\n- Identify which domain it belongs to\n- If unclear → ask ONE clarifying question\n\n## STEP 2 — ROUTING RULES\nRoute to Code-CICD-Agent if user mentions:\n→ Code, bug, error, GitLab, pipeline, CI/CD,\n  merge request, deployment, YAML, script,\n  repository, branch, commit\n\nRoute to Observability-Agent if user mentions:\n→ Logs, metrics, alerts, traces, Elastic,\n  Dynatrace, APM, monitoring, incident,\n  root cause, latency, downtime, crash\n\nRoute to Database-Agent if user mentions:\n→ MongoDB, database, query, collection,\n  Fivetran, data sync, pipeline, slow query,\n  index, schema, data loss\n\nRoute to AI-Monitoring-Agent if user mentions:\n→ ML model, AI performance, drift, accuracy,\n  Arize, retraining, prediction, model health,\n  inference, degradation\n\n## STEP 3 — RESPONSE FORMAT\nAlways respond like this:\n\n### 🎯 Understanding Your Request\n(1 line summary of what user needs)\n\n### 🔀 Routing To\n(Which subagent and why)\n\n### ⏳ What To Expect\n(What the subagent will do for the user)\n\n## RULES\n- NEVER answer technical questions yourself\n- ALWAYS route to the correct subagent\n- If request spans multiple agents → \n  handle one at a time, ask user preference\n- Keep responses short and clear\n- Never make up information',
  tools=[
    agent_tool.AgentTool(agent=dev_ops_coding_copilot_google_search_agent),
    agent_tool.AgentTool(agent=dev_ops_coding_copilot_url_context_agent)
  ],
)
