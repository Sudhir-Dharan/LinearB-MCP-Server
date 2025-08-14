# LinearB MCP Server (Read-Only)

A Model Context Protocol (MCP) server for viewing and querying LinearB API data. This is a **read-only** server that provides safe access to LinearB information without the ability to modify data.

## Features (Read-Only)

- **Deployments**: List and view deployment information
- **Teams**: Search and view team information using V2 API
- **Users**: Search and view user information
- **Services**: Retrieve service information
- **Incidents**: View and search incident information
- **Metrics**: Query and export metrics data
- **Health Check**: Monitor API health status

> **Note**: This is a read-only server. All create, update, and delete operations are disabled for safety.

## Installation

1. Clone this repository
2. Create and activate a virtual environment (recommended):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Ensure pip is available:
   ```bash
   python3 -m ensurepip --upgrade
   ```
4. Install dependencies:
   ```bash
   python3 -m pip install -r requirements.txt
   ```

## Configuration

### API Key Setup

Set your LinearB API key as an environment variable:

```bash
export LINEARB_API_KEY="your-api-key-here"
```

Alternatively, you can set it in a `.env` file:

```
LINEARB_API_KEY=your-api-key-here
```

### MCP Configuration

Add this server to your MCP configuration file (`mcp.json`):

```json
{
  "mcpServers": {
    "linearb": {
      "command": "python",
      "args": ["path/to/Linearb_mcp/server.py"],
      "env": {
        "LINEARB_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## Available Tools

### Discovery Service

- `discover_api`: Get comprehensive API information and available endpoints
- `get_endpoint_details`: Get detailed information about a specific API endpoint
- `get_api_categories`: Get API endpoints organized by categories
- `get_usage_examples`: Get usage examples for API endpoints
- `get_documentation_files`: List available documentation files

### Metrics Discovery

- `get_supported_metrics`: Get comprehensive list of all supported LinearB metrics
- `get_metrics_by_category`: Get metrics organized by category (cycle_time, pull_requests, commits, etc.)
- `search_metrics`: Search metrics by name or description with filtering options
- `get_metric_examples`: Get practical usage examples for metrics queries

### Teams Discovery

- `get_active_teams`: Get comprehensive list of all active teams for analysis
- `get_teams_by_type`: Get teams filtered by type (engineering or qa)
- `get_comparable_teams`: Get engineering teams that can be compared (excludes QA teams)
- `search_teams_by_focus`: Search teams by focus area, name, or description

### Deployments (Read Only)

- `list_deployments`: List deployments with filtering options

### Teams (V2 API - Read Only)

- `search_teams_v2`: Search teams with pagination using V2 API

### Users (Read Only)

- `search_users`: Search users with pagination and filtering

### Services (Read Only)

- `get_services`: Get all services, optionally filtered by repository
- `get_service`: Get a specific service by ID

### Incidents (Read Only)

- `get_incident`: Get a specific incident by provider ID
- `search_incidents`: Search incidents with filtering

### Metrics (Read Only)

- `post_metrics`: Query metrics data from LinearB
- `export_metrics`: Export metrics data in CSV or JSON format

### Health

- `health_check`: Check API health status

## Usage Examples

### Discovery Service

```python
# Discover all available API endpoints
api_info = await discover_api()

# Get detailed information about a specific endpoint
endpoint_details = await get_endpoint_details("/api/v1/deployments", "GET")

# Get endpoints organized by categories
categories = await get_api_categories()

# Get usage examples for a specific category
examples = await get_usage_examples(category="deployments")

# Get usage examples for a specific tool
tool_examples = await get_usage_examples(tool_name="list_deployments")

# List available documentation files
docs = await get_documentation_files()
```

### Metrics Discovery

```python
# Get all supported metrics with details
all_metrics = await get_supported_metrics()

# Get metrics by category
cycle_time_metrics = await get_metrics_by_category("cycle_time")
pr_metrics = await get_metrics_by_category("pull_requests")

# Search for specific metrics
time_metrics = await search_metrics("time", has_aggregation=True)
commit_metrics = await search_metrics("commit", category="commits")

# Get practical usage examples
metric_examples = await get_metric_examples()
```

### Teams Discovery

```python
# Get all active teams
all_teams = await get_active_teams()

# Get only engineering teams for comparison
engineering_teams = await get_teams_by_type("engineering")
comparable_teams = await get_comparable_teams()

# Get QA teams (tracked separately)
qa_teams = await get_teams_by_type("qa")

# Search teams by focus area
integration_teams = await search_teams_by_focus("integration", comparable_only=True)
automation_teams = await search_teams_by_focus("automation", team_type="qa")
```

### List Recent Deployments

```python
# List the 20 most recent deployments
deployments = await list_deployments(limit=20, sort_dir="desc")
```

### View Deployment Details

```python
# List deployments with filtering
deployments = await list_deployments(
    repository_id=12345,
    after="2023-01-01",
    limit=20
)
```

### Query Metrics

```python
# Get cycle time metrics for the last month
metrics = await post_metrics(
    group_by="organization",
    roll_up="1w",
    requested_metrics=[
        {"name": "branch.computed.cycle_time", "agg": "p75"},
        {"name": "branch.time_to_pr", "agg": "p50"},
        {"name": "pr.merged"}
    ],
    time_ranges=[
        {"after": "2023-12-01", "before": "2023-12-31"}
    ]
)

# Use metrics discovery to find available metrics
supported_metrics = await get_supported_metrics()
cycle_metrics = await get_metrics_by_category("cycle_time")
```

### Search Teams (V2 API)

```python
# Search for teams with V2 API
teams = await search_teams_v2(
    search_term="backend",
    page_size=20,
    offset=0
)

# Search teams with filtering
teams = await search_teams_v2(
    search_term="backend",
    page_size=20,
    nonmerged_members_only=False
)
```

### Search Users

```python
# Search for users
users = await search_users(
    search_by_field="name",
    search_term="john",
    page_size=25,
    order_by="name",
    order_dir="ASC"
)

# Search users with advanced filtering
users = await search_users(
    search_by_field="name",
    search_term="john",
    user_role="editor",
    order_by="name",
    order_dir="ASC"
)
```

## Error Handling

The server includes comprehensive error handling:

- **HTTP Errors**: Proper handling of API response errors with detailed messages
- **Network Errors**: Graceful handling of connection issues
- **Validation Errors**: Input validation with clear error messages
- **Logging**: Structured logging for debugging and monitoring

## Security Features

- **Environment Variables**: API keys are loaded from environment variables
- **Input Validation**: All inputs are validated before making API calls
- **Rate Limiting**: Respects API limits and includes proper timeout handling
- **Secure Headers**: Includes proper HTTP headers for API requests

## Development

### Running the Server

```bash
python3 server.py
```

### Testing

#### Quick Test
Run the test script to verify installation:
```bash
python3 test_server.py
```

This will test basic functionality. Note that without a valid API key, you'll see 403 errors, which is expected.

#### Manual Testing
You can test individual tools using the MCP client or by importing the functions directly:

```python
# Test import
python3 -c "import server; print('Server imports successfully')"
```

#### Discovery Service Demo
Run the discovery service demo to see all features in action:
```bash
python3 demo_discovery.py
```

This demo showcases:
- API endpoint discovery and categorization
- Detailed parameter information
- Usage examples and code snippets
- Available documentation files
- Interactive exploration capabilities

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## API Documentation

For detailed information about the LinearB API endpoints, refer to the [LinearB API Documentation](https://docs.linearb.io/).

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:

1. Check the [LinearB API Documentation](https://docs.linearb.io/)
2. Review the server logs for error details
3. Open an issue in this repository

## Discovery Service Features

The LinearB MCP server includes a comprehensive discovery service that helps MCP clients understand and interact with the API:

### API Discovery
- **Endpoint Discovery**: Automatically discovers all available API endpoints from the OpenAPI specification
- **Parameter Information**: Provides detailed parameter information including types, requirements, and constraints
- **Response Schemas**: Shows expected response formats and structures
- **Request Examples**: Includes example requests and payloads

### Self-Documentation
- **Tool Mapping**: Maps API endpoints to MCP tool names for easy reference
- **Category Organization**: Groups endpoints by functional categories (deployments, teams, metrics, etc.)
- **Usage Examples**: Provides code examples and best practices for each tool
- **Documentation Files**: Lists available PDF documentation files

### Interactive Exploration
Use the discovery tools to explore the API:

```python
# Get overview of all available endpoints
api_overview = await discover_api()

# Explore endpoints by category
categories = await get_api_categories()

# Get detailed information about a specific endpoint
endpoint_info = await get_endpoint_details("/api/v1/deployments", "GET")

# Find usage examples
examples = await get_usage_examples(tool_name="list_deployments")
```

## Active Teams Reference

The server includes a comprehensive reference of 7 active teams organized by type:

### Engineering Teams (Comparable)
- **Analytics** (Aly) - Analytics and data engineering team
- **CFD (Titans)** (CFD) - CFD Titans engineering team  
- **Core CRM** (CC) - Core CRM platform team
- **Integrations(Synergy)** (I) - Integrations and Synergy team
- **Media** (Med) - Media and content management team
- **Shinsei** (S) - Shinsei development team

### QA Teams (Tracked Separately)
- **QA-Automation** (QA) - Quality Assurance and Test Automation team

> **Note**: Engineering teams can be compared in metrics analysis. QA teams are tracked separately and should not be compared with engineering squads.

## Supported Metrics Reference

The server includes a comprehensive reference of 22 supported LinearB metrics organized into 7 categories:

### Metric Categories

- **Cycle Time** (5 metrics): Full development cycle metrics with p75/p50/avg aggregations
- **Pull Requests** (6 metrics): PR size, reviews, merge patterns
- **Commits** (4 metrics): Code changes, rework, refactor analysis
- **Releases** (1 metric): Release counting
- **Activity** (1 metric): Developer activity tracking
- **Branches** (2 metrics): Branch state monitoring
- **Incidents** (2 metrics): MTTR and incident resolution

### Key Metrics Examples

- `branch.computed.cycle_time` - Full cycle time (supports p75, p50, avg)
- `branch.time_to_pr` - Coding time (supports p75, p50, avg)
- `pr.merged.size` - PR size analysis (supports p75, p50, avg)
- `commit.activity.rework.count` - Code rework tracking
- `pm.mttr` - Mean time to repair

Use the metrics discovery tools to explore all available metrics and their usage patterns.

## Enabling Write Operations

If you need to enable create, update, and delete operations, you can uncomment the relevant functions in `server.py`. Look for the section marked:

```python
# =============================================================================
# WRITE OPERATIONS DISABLED - READ-ONLY MCP SERVER
# =============================================================================
```

**⚠️ Warning**: Enabling write operations allows the server to modify data in your LinearB account. Use with caution and ensure proper access controls.

## Changelog

### v1.2.0
- **BREAKING CHANGE**: Converted to read-only server for safety
- Disabled all create, update, and delete operations
- Updated Teams API to use V2 endpoints (read operations only)
- Added Users API support (search operations only)
- **NEW**: Comprehensive metrics discovery system with 22 supported metrics
- **NEW**: 4 metrics discovery tools (get_supported_metrics, search_metrics, etc.)
- **NEW**: Metrics organized by 7 categories (cycle_time, pull_requests, commits, etc.)
- **NEW**: Active teams discovery system with 7 teams (6 engineering + 1 QA)
- **NEW**: 4 teams discovery tools (get_active_teams, get_comparable_teams, etc.)
- **NEW**: Team type classification (engineering vs QA) with comparability rules
- **NEW**: Practical usage examples for metrics and teams queries
- Comprehensive discovery service with 13 tools total
- OpenAPI specification integration for automatic endpoint discovery
- Self-documenting API with usage examples and parameter details
- Enhanced test suite with discovery service validation
- Updated to match latest OpenAPI specification

### v1.1.0
- Added comprehensive discovery service with 5 new tools
- OpenAPI specification integration for automatic endpoint discovery
- Self-documenting API with usage examples and parameter details
- Enhanced test suite with discovery service validation
- Improved documentation with discovery service examples

### v1.0.0
- Initial release with full LinearB API support
- Comprehensive error handling and logging
- Security improvements with environment variable configuration
- Type hints and documentation for all functions