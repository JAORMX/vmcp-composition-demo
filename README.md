# Virtual MCP Composition Demo

This demo showcases the **Virtual MCP Server's composite tool capabilities** - the ability to orchestrate multi-step workflows across multiple backend MCP servers.

## What You'll See

### 🎯 Demo Use Cases

1. **Multi-Source Documentation Aggregator**
   - Fetches documentation from 3 different sources in parallel
   - Aggregates results into a structured report with metadata
   - Demonstrates: parallel execution, output format templates, workflow timing

2. **GitHub Repository Health Check**
   - Analyzes a repository by fetching info, issues, and recent activity
   - Shows repo statistics and health metrics
   - Demonstrates: sequential steps with dependencies, parameter defaults, GitHub MCP integration

3. **Container Image Investigation**
   - Queries OCI registry for image details, manifest, and configuration
   - Provides comprehensive image analysis
   - Demonstrates: OCI registry MCP, nested data structures, real-world debugging use case

## Key Features Demonstrated

- ✅ **Composite Tools**: Multi-step workflows orchestrated by Virtual MCP
- ✅ **Structured Output Schemas**: Type-safe outputs with JSON Schema definitions
- ✅ **Output Aggregation**: Template-based value construction from workflow steps
- ✅ **Parallel Execution**: Independent steps run concurrently for performance
- ✅ **Sequential Dependencies**: Steps that depend on previous results
- ✅ **Parameter Defaults**: JSON Schema defaults automatically applied
- ✅ **Workflow Metadata**: Timing, step counts, execution details
- ✅ **Multi-Backend Orchestration**: Seamlessly coordinates fetch + GitHub + OCI registry backends

## Quick Start

```bash
# 1. Setup (creates venv and installs dependencies)
./setup.sh

# 2. Build Virtual MCP (from project root)
cd ../.. && task build-vmcp && cd demos/vmcp-composition

# 3. Start backend servers
./start-backends.sh start

# 4. Run the demo
./run-demo.sh
```

## Prerequisites

### 1. Setup Python Environment

Run the setup script to create a virtual environment and install dependencies:

```bash
./setup.sh
```

This creates a `.venv` directory with:
- `rich` - Beautiful terminal output
- `httpx` - HTTP client for MCP calls
- `pyyaml` - YAML configuration parsing

### 2. Build Virtual MCP

From the project root:

```bash
task build-vmcp
```

This creates `./bin/vmcp` binary.

### 3. Start Backend MCP Servers

The demo requires these backends running in the `default` group.

**Option A: Use the helper script** (recommended):
```bash
./start-backends.sh start
```

**Option B: Manual start**:
```bash
# Fetch MCP (HTTP fetching)
thv run --name fetch --group default --proxy-port 8090 fetch &

# GitHub MCP (GitHub API operations)
thv run --name github --group default --proxy-port 8091 github &

# OCI Registry MCP (Container registry queries)
thv run --name oci-registry --group default --proxy-port 8092 oci-registry &
```

**Check status**:
```bash
./start-backends.sh status
# or
thv list --group default
```

## Running the Demo

Activate the virtual environment and run:

```bash
source .venv/bin/activate
python3 demo.py
```

The demo will:
1. ✨ Show a beautiful introduction with Rich formatting
2. 📋 Display backend servers and configuration
3. ✅ Validate the composite tool definitions
4. 🚀 Start the Virtual MCP Server
5. 🎯 Execute three composite tool demos:
   - Multi-source documentation aggregator
   - GitHub repository health check
   - Container image investigation
6. 📊 Show results with syntax highlighting and tables
7. 🎉 Display summary and metrics

### Demo Modes

**Interactive Mode** (default):
```bash
python3 demo.py
```
Pauses between steps for explanation and demo presentation.

**Auto Mode** (for CI/testing):
```bash
AUTO_CONTINUE=1 python3 demo.py
```
Runs continuously without pauses.

**Fast Mode**:
```bash
DEMO_SPEED=fast python3 demo.py
```
Speeds up animations (combine with AUTO_CONTINUE for fastest execution).

## Configuration

### vmcp-config.yaml

The configuration file defines 3 composite tools with structured output schemas.

**Parameter format:**
```yaml
parameters:
  param_name:
    type: "string"      # Type: string, integer, array, object
    description: "..."  # Optional
    default: "value"    # Optional default
```

**Output schema format (new in PR #2677):**
```yaml
output:
  properties:
    property_name:
      type: "string"      # Type: string, integer, boolean, number, object, array
      description: "..."  # Property description
      value: "{{.template}}"  # Go template expression
      default: "value"    # Optional default value
      properties: {}      # For nested objects
  required: ["property_name"]  # Optional required fields
```

Files:
- **vmcp-config.yaml**: Virtual MCP server configuration with composite tool definitions
- **demo.py**: Interactive demo script with Rich library formatting
- **start-backends.sh**: Helper script to manage backend MCP servers

## Architecture

```
┌─────────────────────────────────────────────────────┐
│            MCP Client (Demo Script)                 │
└─────────────────┬───────────────────────────────────┘
                  │
                  │ HTTP/Streamable
                  ▼
┌─────────────────────────────────────────────────────┐
│         Virtual MCP Server (vmcp)                   │
│  • Discovers backends in 'default' group            │
│  • Aggregates tools with prefix resolution          │
│  • Executes composite tool workflows                │
│  • Applies output_format templates                  │
└──────┬──────────┬──────────────┬────────────────────┘
       │          │              │
       │          │              │ Routes to backends
       ▼          ▼              ▼
 ┌──────────┐ ┌──────────┐ ┌─────────────┐
 │  fetch   │ │  github  │ │ oci-registry│
 │  MCP     │ │  MCP     │ │    MCP      │
 └──────────┘ └──────────┘ └─────────────┘
```

## What Makes This Different?

Traditional MCP clients connect to individual servers. Virtual MCP:
- **Aggregates** multiple backends into one endpoint
- **Orchestrates** multi-step workflows across backends
- **Formats** outputs with custom templates
- **Manages** parallel and sequential execution
- **Provides** workflow metadata and timing

This enables agent-friendly composite operations like "investigate this container image" (requires OCI queries + documentation fetches) in a single tool call.
