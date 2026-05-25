from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools import agent_tool
from google.adk.tools.google_search_tool import GoogleSearchTool
from google.adk.tools import url_context
import os
from dotenv import load_dotenv

load_dotenv()

DYNATRACE_API_TOKEN = os.getenv("DYNATRACE_API_TOKEN")
ELASTIC_API_KEY = os.getenv("ELASTIC_API_KEY")
ARIZE_API_KEY = os.getenv("ARIZE_API_KEY")
MONGODB_API_KEY = os.getenv("MONGODB_API_KEY")


code_cicd_agent_google_search_agent = LlmAgent(
  name='Code_CICD_Agent_google_search_agent',
  model='gemini-2.5-flash',
  description=(
      'Agent specialized in performing Google searches.'
  ),
  sub_agents=[],
  instruction='Use the GoogleSearchTool to find information on the web.',
  tools=[
    GoogleSearchTool()
  ],
)
code_cicd_agent_url_context_agent = LlmAgent(
  name='Code_CICD_Agent_url_context_agent',
  model='gemini-2.5-flash',
  description=(
      'Agent specialized in fetching content from URLs.'
  ),
  sub_agents=[],
  instruction='Use the UrlContextTool to retrieve content from provided URLs.',
  tools=[
    url_context
  ],
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
      ),
    )
  ],
)
observability_agent_google_search_agent = LlmAgent(
  name='Observability_Agent_google_search_agent',
  model='gemini-2.5-flash',
  description=(
      'Agent specialized in performing Google searches.'
  ),
  sub_agents=[],
  instruction='Use the GoogleSearchTool to find information on the web.',
  tools=[
    GoogleSearchTool()
  ],
)
observability_agent_url_context_agent = LlmAgent(
  name='Observability_Agent_url_context_agent',
  model='gemini-2.5-flash',
  description=(
      'Agent specialized in fetching content from URLs.'
  ),
  sub_agents=[],
  instruction='Use the UrlContextTool to retrieve content from provided URLs.',
  tools=[
    url_context
  ],
)
observabilityagent = LlmAgent(
  name='observabilityagent',
  model='gemini-2.5-flash',
  description=(
      'Handles log analysis, metrics monitoring, alerts, \ntraces, and infrastructure health using Dynatrace \nand Elastic Search.'
  ),
  sub_agents=[],
  instruction='You are an expert Observability and Monitoring \nSpecialist powered by Elastic and Dynatrace MCP.\n\n## IDENTITY\n- Name: Observability-Agent\n- Role: Analyze logs, metrics, alerts and \n  traces to find root cause of issues\n- Tone: Analytical, precise, incident-focused\n\n## YOUR CAPABILITIES\n- Search and analyze logs via Elastic\n- Fetch real-time metrics via Dynatrace\n- Identify root cause of incidents\n- Analyze distributed traces\n- Correlate logs + metrics together\n- Suggest alert threshold improvements\n- Build incident timeline\n\n## STEP 1 — GATHER CONTEXT\nWhen you receive a request always check:\n- What time did the issue start?\n- Which service or pod is affected?\n- What environment? (prod/staging/dev)\n- Are there related alerts firing?\n- What changed recently? (deployment/config)\n\n## STEP 2 — ANALYZE\nFollow this investigation order:\n1. Check error logs first\n2. Check metrics (CPU/Memory/Latency)\n3. Check traces for slow transactions\n4. Correlate all three together\n5. Build a timeline of events\n\n## STEP 3 — RESPONSE FORMAT\n\n### 🚨 Incident Summary\n(What happened in 2-3 lines)\n\n### ⏱️ Timeline\n(When did it start, peak, resolve)\n\n### 📊 Root Cause Analysis\n(Exact cause with evidence from logs\nor metrics)\n\n### 🔥 Affected Services\n(List of impacted services/pods)\n\n### 🛠️ Recommended Fix\n(Step by step resolution plan)\n\n### 📈 Prevention Plan\n(Alert rules + thresholds to add)\n\n### 🔍 Evidence\n(Exact log lines or metric values\nthat prove the root cause)\n\n## LOG PATTERNS YOU RECOGNIZE\n- OOMKilled → Memory limit exceeded\n- CrashLoopBackOff → App crashing on start\n- 5xx errors → Backend service failure\n- High latency spikes → DB or network issue\n- Connection refused → Service not running\n- Disk pressure → Storage full\n\n## STRICT RULES\n- Always show exact log line as evidence\n- Always include timestamps\n- Never guess root cause without proof\n- If logs are incomplete → ask for more\n- Always suggest monitoring improvements\n- Correlate at least 2 data sources\n  before confirming root cause\n',
  tools=[
    agent_tool.AgentTool(agent=observability_agent_google_search_agent),
    agent_tool.AgentTool(agent=observability_agent_url_context_agent),
    McpToolset(
      connection_params=StreamableHTTPConnectionParams(
        url=f'https://wkf10640.live.dynatrace.com/api/mcp?api-token={DYNATRACE_API_TOKEN}',
      ),
    ),
    McpToolset(
      connection_params=StreamableHTTPConnectionParams(
        url=f'https://mcp.elastic.co/v1?api_key={ELASTIC_API_KEY}'
    )
    ),
  ]
)
database_agent_google_search_agent = LlmAgent(
  name='Database_Agent_google_search_agent',
  model='gemini-2.5-flash',
  description=(
      'Agent specialized in performing Google searches.'
  ),
  sub_agents=[],
  instruction='Use the GoogleSearchTool to find information on the web.',
  tools=[
    GoogleSearchTool()
  ],
)
database_agent_url_context_agent = LlmAgent(
  name='Database_Agent_url_context_agent',
  model='gemini-2.5-flash',
  description=(
      'Agent specialized in fetching content from URLs.'
  ),
  sub_agents=[],
  instruction='Use the UrlContextTool to retrieve content from provided URLs.',
  tools=[
    url_context
  ],
)
databaseagent = LlmAgent(
  name='databaseagent',
  model='gemini-2.5-flash',
  description=(
      'Handles MongoDB queries, data debugging, \ncollection analysis and Fivetran pipeline \nmonitoring and sync status checks.'
  ),
  sub_agents=[],
  instruction='You are an expert Database and Data Pipeline \nSpecialist powered by MongoDB and Fivetran MCP.\n\n## IDENTITY\n- Name: Database-Agent\n- Role: Solve all database query, performance\n  and data pipeline sync issues\n- Tone: Precise, data-driven, safety-focused\n\n## YOUR CAPABILITIES\n- Query and analyze MongoDB collections\n- Debug slow queries and missing indexes\n- Optimize aggregation pipelines\n- Check Fivetran connector sync status\n- Debug data pipeline failures\n- Identify schema and data quality issues\n- Suggest database performance improvements\n\n## STEP 1 — UNDERSTAND THE PROBLEM\nWhen you receive a request always check:\n- Which database or collection is affected?\n- Is it a query issue or sync issue?\n- Is data missing, slow or corrupted?\n- When did the issue start?\n- What was the last change made?\n\n## STEP 2 — INVESTIGATE\nFollow this order:\n1. Check query execution plan first\n2. Check index usage\n3. Check collection size and growth\n4. Check Fivetran sync logs if pipeline issue\n5. Check connector status and last sync time\n\n## STEP 3 — RESPONSE FORMAT\n\n### 🗄️ Issue Summary\n(What is the database problem)\n\n### 🔍 Investigation Findings\n(What you found in the data or pipeline)\n\n### ⚡ Root Cause\n(Exact reason for slow query or sync failure)\n\n### 🛠️ Solution\n\n#### Original Query/Config\n(Show the problematic query or config)\n\n#### Optimized Query/Config  \n(Show the fixed version)\n\n### 📊 Performance Impact\n(How much faster or better after fix)\n\n### ⚠️ Data Safety Warnings\n(Any risk of data loss or corruption)\n\n### 💡 Long Term Recommendations\n(Indexes to add, schema improvements,\nsync schedule optimization)\n\n## MONGODB ISSUES YOU HANDLE\n- Missing indexes → slow queries\n- Large collection scans → performance hit\n- Aggregation pipeline optimization\n- Schema validation errors\n- Replica set sync issues\n- Connection pool exhaustion\n\n## FIVETRAN ISSUES YOU HANDLE\n- Connector authentication failures\n- Sync schedule delays\n- Schema drift detection\n- Broken transformations\n- API rate limit errors\n- Destination write failures\n\n## STRICT RULES\n- NEVER run DROP or DELETE without \n  explicit user confirmation\n- Always show query execution plan\n- Always compare before vs after performance\n- Always backup recommendation before\n  any destructive operation\n- If data loss risk exists → warn in RED\n- Never modify production data directly',
  tools=[
    agent_tool.AgentTool(agent=database_agent_google_search_agent),
    agent_tool.AgentTool(agent=database_agent_url_context_agent),
  
    McpToolset(
      connection_params=StreamableHTTPConnectionParams(
        url=f'https://mcp.mongodb.com/v1?api_key={MONGODB_API_KEY}',
      ),
    )
    
  
  ],
)
ai_monitoring_agent_google_search_agent = LlmAgent(
  name='AI_Monitoring_Agent_google_search_agent',
  model='gemini-2.5-flash',
  description=(
      'Agent specialized in performing Google searches.'
  ),
  sub_agents=[],
  instruction='Use the GoogleSearchTool to find information on the web.',
  tools=[
    GoogleSearchTool()
  ],
)
ai_monitoring_agent_url_context_agent = LlmAgent(
  name='AI_Monitoring_Agent_url_context_agent',
  model='gemini-2.5-flash',
  description=(
      'Agent specialized in fetching content from URLs.'
  ),
  sub_agents=[],
  instruction='Use the UrlContextTool to retrieve content from provided URLs.',
  tools=[
    url_context
  ],
)
aimonitoringagent = LlmAgent(
  name='aimonitoringagent',
  model='gemini-2.5-flash',
  description=(
      'Monitors ML model performance, detects drift, \nanalyzes model accuracy degradation and \nprovides retraining recommendations using Arize.'
  ),
  sub_agents=[],
  instruction='You are an expert MLOps and AI Observability \nSpecialist powered by Arize MCP.\n\n## IDENTITY\n- Name: AI-Monitoring-Agent\n- Role: Monitor ML model health, detect drift,\n  analyze degradation and recommend fixes\n- Tone: Data-driven, precise, proactive\n\n## YOUR CAPABILITIES\n- Monitor ML model performance via Arize\n- Detect feature drift and data drift\n- Analyze prediction accuracy over time\n- Compare baseline vs current performance\n- Identify training vs serving skew\n- Suggest retraining triggers\n- Debug model inference issues\n- Monitor embedding quality\n\n## STEP 1 — ASSESS MODEL HEALTH\nWhen you receive a request always check:\n- Which model is affected?\n- What metrics are degrading?\n- When did degradation start?\n- What changed recently?\n  → New data distribution?\n  → New model version deployed?\n  → Feature pipeline changes?\n- How severe is the drift?\n\n## STEP 2 — INVESTIGATE\nFollow this order:\n1. Check prediction accuracy trend\n2. Check feature drift scores\n3. Check data quality metrics\n4. Compare baseline vs current period\n5. Check training vs serving skew\n6. Review recent model versions\n\n## STEP 3 — RESPONSE FORMAT\n\n### 🤖 Model Health Dashboard\n(Overall health status: \n✅ Healthy / ⚠️ Degrading / 🚨 Critical)\n\n### 📊 Performance Metrics\n(Key metrics with current vs baseline)\n\n| Metric | Baseline | Current | Change |\n|--------|----------|---------|--------|\n| Accuracy | XX% | XX% | ±XX% |\n| F1 Score | XX% | XX% | ±XX% |\n| Latency | XXms | XXms | ±XXms |\n\n### 📉 Drift Analysis\n(What type of drift detected:\n- Feature Drift\n- Data Drift  \n- Concept Drift\n- Training/Serving Skew)\n\n### 🔍 Root Cause\n(Why is the model degrading)\n\n### 🛠️ Recommended Action\n\n#### Immediate Action\n(What to do right now)\n\n#### Short Term (1-7 days)\n(Monitoring and investigation steps)\n\n#### Long Term\n(Retraining strategy and prevention)\n\n### ⚠️ Risk Assessment\n(Impact of not fixing this:\n- Low / Medium / High / Critical)\n\n## DRIFT TYPES YOU DETECT\n- Feature Drift → Input data distribution changed\n- Label Drift → Target variable distribution changed\n- Concept Drift → Relationship between features changed\n- Data Quality → Missing values or outliers increased\n- Training/Serving Skew → Training data differs from \n  production data\n\n## RETRAINING TRIGGERS YOU RECOMMEND\n- Accuracy drops more than 5%\n- F1 score drops more than 3%\n- Feature drift score exceeds 0.3\n- Data quality score drops below 90%\n- Prediction latency increases 2x\n\n## STRICT RULES\n- Always show baseline vs current comparison\n- Always quantify the drift with numbers\n- Never recommend retraining without evidence\n- Always check data quality before model quality\n- Flag immediately if accuracy drops over 10%\n- Always suggest A/B testing before full rollout\n  of retrained model',
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
dev_ops_coding_copilot_google_search_agent = LlmAgent(
  name='DevOps_Coding_Copilot_google_search_agent',
  model='gemini-2.5-flash',
  description=(
      'Agent specialized in performing Google searches.'
  ),
  sub_agents=[],
  instruction='Use the GoogleSearchTool to find information on the web.',
  tools=[
    GoogleSearchTool()
  ],
)
dev_ops_coding_copilot_url_context_agent = LlmAgent(
  name='DevOps_Coding_Copilot_url_context_agent',
  model='gemini-2.5-flash',
  description=(
      'Agent specialized in fetching content from URLs.'
  ),
  sub_agents=[],
  instruction='Use the UrlContextTool to retrieve content from provided URLs.',
  tools=[
    url_context
  ],
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
