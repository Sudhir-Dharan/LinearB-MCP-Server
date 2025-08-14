#!/usr/bin/env python3
"""
LinearB MCP Server (Read-Only)

A Model Context Protocol server for safely viewing and querying LinearB API data.
This server provides read-only access to LinearB information without the ability 
to modify data.

All create, update, and delete operations are disabled for safety.
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
import httpx
from mcp.server.fastmcp.server import FastMCP

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv is optional
    pass

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("LinearB API Server")

# Get configuration from environment variables
API_KEY = os.getenv("LINEARB_API_KEY")
if not API_KEY:
    logger.warning("LINEARB_API_KEY environment variable not set. Server may not work properly.")
    API_KEY = "your-api-key-here"

API_TIMEOUT = float(os.getenv("API_TIMEOUT", "30.0"))
BASE_URL = os.getenv("LINEARB_BASE_URL", "https://public-api.linearb.io")

# Initialize HTTP client with proper configuration
client = httpx.AsyncClient(
    base_url=BASE_URL,
    headers={
        "x-api-key": API_KEY,
        "Content-Type": "application/json",
        "User-Agent": "LinearB-MCP-Server/1.0"
    },
    timeout=API_TIMEOUT
)

# Load OpenAPI specification for discovery service
OPENAPI_SPEC = None
try:
    openapi_path = Path(__file__).parent / "openAPI.json"
    if openapi_path.exists():
        with open(openapi_path, 'r') as f:
            OPENAPI_SPEC = json.load(f)
        logger.info("OpenAPI specification loaded successfully")
    else:
        logger.warning("OpenAPI specification file not found")
except Exception as e:
    logger.error(f"Failed to load OpenAPI specification: {e}")

# Documentation paths
DOCS_PATH = Path(__file__).parent / "docs"

# =============================================================================
# SUPPORTED METRICS REFERENCE
# =============================================================================

SUPPORTED_METRICS = {
    "branch.computed.cycle_time": {
        "name": "branch.computed.cycle_time",
        "aggregations": ["p75", "p50", "avg"],
        "description": "Full cycle time (Coding time + Pickup time + Review time + Time to production)",
        "units": "min",
        "category": "cycle_time"
    },
    "branch.time_to_pr": {
        "name": "branch.time_to_pr",
        "aggregations": ["p75", "p50", "avg"],
        "description": "Coding time (Time to PR)",
        "units": "min",
        "category": "cycle_time"
    },
    "branch.time_to_review": {
        "name": "branch.time_to_review",
        "aggregations": ["p75", "p50", "avg"],
        "description": "Pickup time (Time to review)",
        "units": "min",
        "category": "cycle_time"
    },
    "branch.review_time": {
        "name": "branch.review_time",
        "aggregations": ["p75", "p50", "avg"],
        "description": "Review time",
        "units": "min",
        "category": "cycle_time"
    },
    "branch.time_to_prod": {
        "name": "branch.time_to_prod",
        "aggregations": ["p75", "p50", "avg"],
        "description": "Time to production (Time to deploy)",
        "units": "min",
        "category": "cycle_time"
    },
    "pr.merged.size": {
        "name": "pr.merged.size",
        "aggregations": ["p75", "p50", "avg"],
        "description": "The sum of PR sizes of merged PRs",
        "units": "lines of code",
        "category": "pull_requests"
    },
    "pr.merged": {
        "name": "pr.merged",
        "aggregations": [],
        "description": "The number of PRs that got merged",
        "units": "count",
        "category": "pull_requests"
    },
    "pr.review_depth": {
        "name": "pr.review_depth",
        "aggregations": [],
        "description": "The sum of comments divided by the sum of PRs",
        "units": "lines of comments",
        "category": "pull_requests"
    },
    "commit.activity.new_work.count": {
        "name": "commit.activity.new_work.count",
        "aggregations": [],
        "description": "The total new lines of code",
        "units": "count",
        "category": "commits"
    },
    "commit.total_changes": {
        "name": "commit.total_changes",
        "aggregations": [],
        "description": "The total lines of code that have been replaced",
        "units": "lines of code",
        "category": "commits"
    },
    "commit.activity.refactor.count": {
        "name": "commit.activity.refactor.count",
        "aggregations": [],
        "description": "The total lines of code that have been replaced that are older then 25 days",
        "units": "lines of code",
        "category": "commits"
    },
    "commit.activity.rework.count": {
        "name": "commit.activity.rework.count",
        "aggregations": [],
        "description": "The total lines of code that have replaced code written within the last 25 days, but outside this branch",
        "units": "lines of code",
        "category": "commits"
    },
    "pr.merged.without.review.count": {
        "name": "pr.merged.without.review.count",
        "aggregations": [],
        "description": "The number of PRs that got merged without review",
        "units": "count",
        "category": "pull_requests"
    },
    "commit.total.count": {
        "name": "commit.total.count",
        "aggregations": [],
        "description": "The sum of commits",
        "units": "count",
        "category": "commits"
    },
    "pr.new": {
        "name": "pr.new",
        "aggregations": [],
        "description": "The number of opened PRs",
        "units": "count",
        "category": "pull_requests"
    },
    "pr.reviews": {
        "name": "pr.reviews",
        "aggregations": [],
        "description": "The number of reviews on all PRs",
        "units": "count",
        "category": "pull_requests"
    },
    "releases.count": {
        "name": "releases.count",
        "aggregations": [],
        "description": "The number of releases",
        "units": "count",
        "category": "releases"
    },
    "commit.activity_days": {
        "name": "commit.activity_days",
        "aggregations": [],
        "description": "The amount of day of developer activity (commit/comment/PR/merge/review)",
        "units": "days",
        "category": "activity"
    },
    "branch.state.computed.done": {
        "name": "branch.state.computed.done",
        "aggregations": [],
        "description": "Number of branches that reached state done",
        "units": "count",
        "category": "branches"
    },
    "branch.state.active": {
        "name": "branch.state.active",
        "aggregations": [],
        "description": "Number of active branches",
        "units": "count",
        "category": "branches"
    },
    "pm.mttr": {
        "name": "pm.mttr",
        "aggregations": [],
        "description": "Mean time to repair",
        "units": "min",
        "category": "incidents"
    },
    "pm.cfr.issues.done": {
        "name": "pm.cfr.issues.done",
        "aggregations": [],
        "description": "The sum of issues that are considered as incidents that reached a done state",
        "units": "count",
        "category": "incidents"
    }
}

METRICS_CATEGORIES = {
    "cycle_time": {
        "name": "Cycle Time Metrics",
        "description": "Metrics related to development cycle time and flow",
        "metrics": [m for m, data in SUPPORTED_METRICS.items() if data["category"] == "cycle_time"]
    },
    "pull_requests": {
        "name": "Pull Request Metrics",
        "description": "Metrics related to pull requests and code reviews",
        "metrics": [m for m, data in SUPPORTED_METRICS.items() if data["category"] == "pull_requests"]
    },
    "commits": {
        "name": "Commit Metrics",
        "description": "Metrics related to commits and code changes",
        "metrics": [m for m, data in SUPPORTED_METRICS.items() if data["category"] == "commits"]
    },
    "releases": {
        "name": "Release Metrics",
        "description": "Metrics related to software releases",
        "metrics": [m for m, data in SUPPORTED_METRICS.items() if data["category"] == "releases"]
    },
    "activity": {
        "name": "Activity Metrics",
        "description": "Metrics related to developer activity",
        "metrics": [m for m, data in SUPPORTED_METRICS.items() if data["category"] == "activity"]
    },
    "branches": {
        "name": "Branch Metrics",
        "description": "Metrics related to branch states",
        "metrics": [m for m, data in SUPPORTED_METRICS.items() if data["category"] == "branches"]
    },
    "incidents": {
        "name": "Incident Metrics",
        "description": "Metrics related to incidents and reliability",
        "metrics": [m for m, data in SUPPORTED_METRICS.items() if data["category"] == "incidents"]
    }
}

# =============================================================================
# ACTIVE TEAMS REFERENCE
# =============================================================================

ACTIVE_TEAMS = {
    "analytics": {
        "name": "Analytics",
        "short_name": "Aly",
        "type": "engineering",
        "description": "Analytics and data engineering team",
        "color": "#DC143C",  # Crimson red
        "comparable": True,
        "focus_areas": ["data analytics", "business intelligence", "data engineering"]
    },
    "cfd_titans": {
        "name": "CFD (Titans)",
        "short_name": "CFD",
        "type": "engineering",
        "description": "CFD Titans engineering team",
        "color": "#32CD32",  # Lime green
        "comparable": True,
        "focus_areas": ["Client Focus Delivery", "Support"]
    },
    "core_crm": {
        "name": "Core CRM",
        "short_name": "CC",
        "type": "engineering",
        "description": "Core CRM platform team",
        "color": "#4169E1",  # Royal blue
        "comparable": True,
        "focus_areas": ["customer relationship management", "core platform"]
    },
    "integrations_synergy": {
        "name": "Integrations(Synergy)",
        "short_name": "I",
        "type": "engineering",
        "description": "Integrations and Synergy team",
        "color": "#FF8C00",  # Dark orange
        "comparable": True,
        "focus_areas": ["system integrations", "api development", "third-party connections"]
    },
    "media": {
        "name": "Media",
        "short_name": "Med",
        "type": "engineering",
        "description": "Media and content management team",
        "color": "#00BFFF",  # Deep sky blue
        "comparable": True,
        "focus_areas": ["media processing", "content management", "digital assets"]
    },
    "shinsei": {
        "name": "Shinsei",
        "short_name": "S",
        "type": "engineering",
        "description": "Shinsei development team",
        "color": "#DA70D6",  # Orchid purple
        "comparable": True,
        "focus_areas": ["new product development", "innovation"]
    },
    "qa_automation": {
        "name": "QA-Automation",
        "short_name": "QA",
        "type": "qa",
        "description": "Quality Assurance and Test Automation team",
        "color": "#FFD700",  # Gold
        "comparable": False,
        "focus_areas": ["test automation", "quality assurance", "testing frameworks"]
    }
}

TEAM_TYPES = {
    "engineering": {
        "name": "Engineering Teams",
        "description": "Software development and engineering teams",
        "comparable": True,
        "teams": [team_id for team_id, team in ACTIVE_TEAMS.items() if team["type"] == "engineering"]
    },
    "qa": {
        "name": "Quality Assurance Teams",
        "description": "QA and testing teams - tracked separately from engineering squads",
        "comparable": False,
        "teams": [team_id for team_id, team in ACTIVE_TEAMS.items() if team["type"] == "qa"]
    }
}


# =============================================================================
# DISCOVERY SERVICE TOOLS
# =============================================================================

@mcp.tool(name="discover_api", description="Get comprehensive API information and available endpoints")
async def discover_api() -> Dict[str, Any]:
    """
    Discover all available LinearB API endpoints with comprehensive information.
    
    Returns:
        Complete API information including endpoints, methods, parameters, and documentation.
    """
    if not OPENAPI_SPEC:
        return {
            "error": "OpenAPI specification not available",
            "available_tools": [
                "list_deployments", "create_deployment", "get_teams", "get_team", 
                "search_teams", "get_services", "get_service", "get_incident",
                "create_incident", "update_incident", "search_incidents", "delete_incident",
                "post_metrics", "export_metrics", "post_custom_metric", "create_cycle_time_stage",
                "health_check"
            ]
        }
    
    discovery_info = {
        "api_info": OPENAPI_SPEC.get("info", {}),
        "base_url": OPENAPI_SPEC.get("servers", [{}])[0].get("url", BASE_URL),
        "endpoints": {},
        "categories": {
            "deployments": [],
            "teams": [],
            "services": [],
            "incidents": [],
            "measurements": [],
            "health": [],
            "custom_metrics": []
        }
    }
    
    # Process all endpoints from OpenAPI spec
    for path, methods in OPENAPI_SPEC.get("paths", {}).items():
        for method, details in methods.items():
            endpoint_info = {
                "path": path,
                "method": method.upper(),
                "summary": details.get("summary", ""),
                "description": details.get("description", ""),
                "tags": details.get("tags", []),
                "parameters": [],
                "request_body": None,
                "responses": details.get("responses", {}),
                "operation_id": details.get("operationId", "")
            }
            
            # Extract parameters
            for param in details.get("parameters", []):
                param_info = {
                    "name": param.get("name"),
                    "in": param.get("in"),
                    "required": param.get("required", False),
                    "type": param.get("schema", {}).get("type"),
                    "description": param.get("description", "")
                }
                endpoint_info["parameters"].append(param_info)
            
            # Extract request body info
            if "requestBody" in details:
                request_body = details["requestBody"]
                endpoint_info["request_body"] = {
                    "required": request_body.get("required", False),
                    "content_types": list(request_body.get("content", {}).keys()),
                    "schema": request_body.get("content", {}).get("application/json", {}).get("schema", {}),
                    "examples": request_body.get("content", {}).get("application/json", {}).get("examples", {})
                }
            
            endpoint_key = f"{method.upper()} {path}"
            discovery_info["endpoints"][endpoint_key] = endpoint_info
            
            # Categorize endpoints
            tags = details.get("tags", [])
            for tag in tags:
                tag_lower = tag.lower()
                if "deployment" in tag_lower:
                    discovery_info["categories"]["deployments"].append(endpoint_key)
                elif "team" in tag_lower:
                    discovery_info["categories"]["teams"].append(endpoint_key)
                elif "service" in tag_lower:
                    discovery_info["categories"]["services"].append(endpoint_key)
                elif "incident" in tag_lower:
                    discovery_info["categories"]["incidents"].append(endpoint_key)
                elif "measurement" in tag_lower or "metric" in tag_lower:
                    discovery_info["categories"]["measurements"].append(endpoint_key)
                elif "health" in tag_lower:
                    discovery_info["categories"]["health"].append(endpoint_key)
    
    return discovery_info


@mcp.tool(name="get_endpoint_details", description="Get detailed information about a specific API endpoint")
async def get_endpoint_details(endpoint_path: str, method: str = "GET") -> Dict[str, Any]:
    """
    Get detailed information about a specific API endpoint.
    
    Args:
        endpoint_path: The API endpoint path (e.g., '/api/v1/deployments')
        method: HTTP method (GET, POST, PUT, DELETE, default: GET)
    
    Returns:
        Detailed endpoint information including parameters, examples, and usage.
    """
    if not OPENAPI_SPEC:
        return {"error": "OpenAPI specification not available"}
    
    method = method.upper()
    paths = OPENAPI_SPEC.get("paths", {})
    
    if endpoint_path not in paths:
        available_paths = list(paths.keys())
        return {
            "error": f"Endpoint '{endpoint_path}' not found",
            "available_endpoints": available_paths
        }
    
    endpoint_methods = paths[endpoint_path]
    if method.lower() not in endpoint_methods:
        available_methods = list(endpoint_methods.keys())
        return {
            "error": f"Method '{method}' not available for '{endpoint_path}'",
            "available_methods": [m.upper() for m in available_methods]
        }
    
    details = endpoint_methods[method.lower()]
    
    endpoint_info = {
        "endpoint": f"{method} {endpoint_path}",
        "summary": details.get("summary", ""),
        "description": details.get("description", ""),
        "tags": details.get("tags", []),
        "parameters": {
            "query": [],
            "path": [],
            "header": []
        },
        "request_body": None,
        "responses": {},
        "examples": {},
        "mcp_tool_name": _get_mcp_tool_name(endpoint_path, method)
    }
    
    # Process parameters
    for param in details.get("parameters", []):
        param_info = {
            "name": param.get("name"),
            "type": param.get("schema", {}).get("type", "string"),
            "required": param.get("required", False),
            "description": param.get("description", ""),
            "default": param.get("schema", {}).get("default"),
            "enum": param.get("schema", {}).get("enum"),
            "minimum": param.get("schema", {}).get("minimum"),
            "maximum": param.get("schema", {}).get("maximum")
        }
        
        param_location = param.get("in", "query")
        endpoint_info["parameters"][param_location].append(param_info)
    
    # Process request body
    if "requestBody" in details:
        request_body = details["requestBody"]
        content = request_body.get("content", {})
        json_content = content.get("application/json", {})
        
        endpoint_info["request_body"] = {
            "required": request_body.get("required", False),
            "content_type": "application/json",
            "schema": json_content.get("schema", {}),
            "examples": json_content.get("examples", {})
        }
    
    # Process responses
    for status_code, response in details.get("responses", {}).items():
        endpoint_info["responses"][status_code] = {
            "description": response.get("description", ""),
            "schema": response.get("content", {}).get("application/json", {}).get("schema", {})
        }
    
    return endpoint_info


@mcp.tool(name="get_api_categories", description="Get API endpoints organized by categories")
async def get_api_categories() -> Dict[str, Any]:
    """
    Get all API endpoints organized by functional categories.
    
    Returns:
        API endpoints grouped by categories like deployments, teams, services, etc.
    """
    categories = {
        "deployments": {
            "description": "View deployment information (read-only)",
            "endpoints": [
                {"tool": "list_deployments", "method": "GET", "path": "/api/v1/deployments", "description": "List deployments with filtering"}
            ]
        },
        "teams": {
            "description": "View team information using V2 API (read-only)",
            "endpoints": [
                {"tool": "search_teams_v2", "method": "GET", "path": "/api/v2/teams", "description": "Search teams with pagination"}
            ]
        },
        "users": {
            "description": "View user information (read-only)",
            "endpoints": [
                {"tool": "search_users", "method": "GET", "path": "/api/v1/users", "description": "Search users with pagination"}
            ]
        },
        "services": {
            "description": "Retrieve service information",
            "endpoints": [
                {"tool": "get_services", "method": "GET", "path": "/api/v1/services/", "description": "Get all services"},
                {"tool": "get_service", "method": "GET", "path": "/api/v1/services/{service_id}", "description": "Get specific service by ID"}
            ]
        },
        "incidents": {
            "description": "View incident information (read-only)",
            "endpoints": [
                {"tool": "get_incident", "method": "GET", "path": "/api/v1/incidents/{provider_id}", "description": "Get specific incident"},
                {"tool": "search_incidents", "method": "POST", "path": "/api/v1/incidents/search", "description": "Search incidents with filtering"}
            ]
        },
        "metrics": {
            "description": "Query and export metrics data (read-only)",
            "endpoints": [
                {"tool": "post_metrics", "method": "POST", "path": "/api/v2/measurements", "description": "Query metrics data"},
                {"tool": "export_metrics", "method": "POST", "path": "/api/v2/measurements/export", "description": "Export metrics in CSV/JSON"}
            ]
        },
        "health": {
            "description": "Monitor API health",
            "endpoints": [
                {"tool": "health_check", "method": "GET", "path": "/api/v1/health", "description": "Check API health status"}
            ]
        },
        "discovery": {
            "description": "API discovery and reference tools",
            "endpoints": [
                {"tool": "discover_api", "method": "N/A", "path": "N/A", "description": "Get comprehensive API information"},
                {"tool": "get_endpoint_details", "method": "N/A", "path": "N/A", "description": "Get detailed endpoint information"},
                {"tool": "get_api_categories", "method": "N/A", "path": "N/A", "description": "Get API endpoints by categories"},
                {"tool": "get_usage_examples", "method": "N/A", "path": "N/A", "description": "Get usage examples"},
                {"tool": "get_documentation_files", "method": "N/A", "path": "N/A", "description": "List documentation files"},
                {"tool": "get_supported_metrics", "method": "N/A", "path": "N/A", "description": "Get all supported metrics"},
                {"tool": "get_metrics_by_category", "method": "N/A", "path": "N/A", "description": "Get metrics by category"},
                {"tool": "search_metrics", "method": "N/A", "path": "N/A", "description": "Search metrics by name/description"},
                {"tool": "get_metric_examples", "method": "N/A", "path": "N/A", "description": "Get metric usage examples"},
                {"tool": "get_active_teams", "method": "N/A", "path": "N/A", "description": "Get all active teams"},
                {"tool": "get_teams_by_type", "method": "N/A", "path": "N/A", "description": "Get teams by type (engineering/qa)"},
                {"tool": "get_comparable_teams", "method": "N/A", "path": "N/A", "description": "Get comparable engineering teams"},
                {"tool": "search_teams_by_focus", "method": "N/A", "path": "N/A", "description": "Search teams by focus area"}
            ]
        }
    }
    
    return {
        "total_categories": len(categories),
        "total_endpoints": sum(len(cat["endpoints"]) for cat in categories.values()),
        "categories": categories
    }


@mcp.tool(name="get_usage_examples", description="Get usage examples for API endpoints")
async def get_usage_examples(category: Optional[str] = None, tool_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Get comprehensive usage examples for API endpoints.
    
    Args:
        category: Filter examples by category (deployments, teams, services, incidents, metrics, health)
        tool_name: Get examples for a specific tool name
    
    Returns:
        Usage examples with code snippets and explanations.
    """
    examples = {
        "deployments": {
            "list_deployments": {
                "description": "List recent deployments with filtering (read-only)",
                "examples": [
                    {
                        "title": "List 10 most recent deployments",
                        "code": "await list_deployments(limit=10, sort_dir='desc')",
                        "parameters": {"limit": 10, "sort_dir": "desc"}
                    },
                    {
                        "title": "List deployments for specific repository",
                        "code": "await list_deployments(repository_id=12345, limit=20)",
                        "parameters": {"repository_id": 12345, "limit": 20}
                    },
                    {
                        "title": "List deployments in date range",
                        "code": "await list_deployments(after='2023-01-01', before='2023-12-31')",
                        "parameters": {"after": "2023-01-01", "before": "2023-12-31"}
                    }
                ]
            }
        },
        "teams": {
            "search_teams_v2": {
                "description": "Search teams with V2 API (read-only)",
                "examples": [
                    {
                        "title": "Search all teams",
                        "code": "await search_teams_v2(page_size=50)",
                        "parameters": {"page_size": 50}
                    },
                    {
                        "title": "Search teams by name",
                        "code": "await search_teams_v2(search_term='backend', page_size=20)",
                        "parameters": {"search_term": "backend", "page_size": 20}
                    }
                ]
            }
        },
        "users": {
            "search_users": {
                "description": "Search users with filtering (read-only)",
                "examples": [
                    {
                        "title": "Search all users",
                        "code": "await search_users(page_size=50)",
                        "parameters": {"page_size": 50}
                    },
                    {
                        "title": "Search users by name",
                        "code": "await search_users(search_by_field='name', search_term='john', order_by='name')",
                        "parameters": {"search_by_field": "name", "search_term": "john", "order_by": "name"}
                    }
                ]
            }
        },
        "metrics": {
            "post_metrics": {
                "description": "Query metrics data",
                "examples": [
                    {
                        "title": "Get cycle time metrics",
                        "code": """await post_metrics(
    group_by='organization',
    roll_up='1w',
    requested_metrics=[{'name': 'branch.computed.cycle_time', 'agg': 'p75'}],
    time_ranges=[{'after': '2023-01-01', 'before': '2023-01-31'}]
)""",
                        "parameters": {
                            "group_by": "organization",
                            "roll_up": "1w",
                            "requested_metrics": [{"name": "branch.computed.cycle_time", "agg": "p75"}],
                            "time_ranges": [{"after": "2023-01-01", "before": "2023-01-31"}]
                        }
                    }
                ]
            }
        },
        "incidents": {
            "search_incidents": {
                "description": "Search incidents with filtering (read-only)",
                "examples": [
                    {
                        "title": "Search recent incidents",
                        "code": "await search_incidents(limit=20, after='2023-01-01')",
                        "parameters": {"limit": 20, "after": "2023-01-01"}
                    },
                    {
                        "title": "Search incidents by status",
                        "code": "await search_incidents(status='open', limit=10)",
                        "parameters": {"status": "open", "limit": 10}
                    }
                ]
            },
            "get_incident": {
                "description": "Get specific incident details (read-only)",
                "examples": [
                    {
                        "title": "Get incident by provider ID",
                        "code": "await get_incident(provider_id='INC-001')",
                        "parameters": {"provider_id": "INC-001"}
                    }
                ]
            }
        },
        "metrics_discovery": {
            "get_supported_metrics": {
                "description": "Get comprehensive metrics reference",
                "examples": [
                    {
                        "title": "Get all supported metrics",
                        "code": "await get_supported_metrics()",
                        "parameters": {}
                    }
                ]
            },
            "search_metrics": {
                "description": "Search for specific metrics",
                "examples": [
                    {
                        "title": "Search cycle time metrics",
                        "code": "await search_metrics('cycle', category='cycle_time')",
                        "parameters": {"search_term": "cycle", "category": "cycle_time"}
                    },
                    {
                        "title": "Find metrics with aggregation support",
                        "code": "await search_metrics('time', has_aggregation=True)",
                        "parameters": {"search_term": "time", "has_aggregation": True}
                    }
                ]
            },
            "get_metrics_by_category": {
                "description": "Get metrics organized by category",
                "examples": [
                    {
                        "title": "Get all pull request metrics",
                        "code": "await get_metrics_by_category('pull_requests')",
                        "parameters": {"category": "pull_requests"}
                    },
                    {
                        "title": "Get all categories overview",
                        "code": "await get_metrics_by_category()",
                        "parameters": {}
                    }
                ]
            }
        },
        "teams_discovery": {
            "get_active_teams": {
                "description": "Get comprehensive active teams reference",
                "examples": [
                    {
                        "title": "Get all active teams",
                        "code": "await get_active_teams()",
                        "parameters": {}
                    }
                ]
            },
            "get_comparable_teams": {
                "description": "Get teams suitable for comparison",
                "examples": [
                    {
                        "title": "Get engineering teams for comparison",
                        "code": "await get_comparable_teams()",
                        "parameters": {}
                    }
                ]
            },
            "search_teams_by_focus": {
                "description": "Search teams by focus area",
                "examples": [
                    {
                        "title": "Find integration teams",
                        "code": "await search_teams_by_focus('integration', comparable_only=True)",
                        "parameters": {"search_term": "integration", "comparable_only": True}
                    },
                    {
                        "title": "Find QA teams",
                        "code": "await search_teams_by_focus('automation', team_type='qa')",
                        "parameters": {"search_term": "automation", "team_type": "qa"}
                    }
                ]
            }
        }
    }
    
    if tool_name:
        # Find specific tool examples
        for cat_name, cat_examples in examples.items():
            if tool_name in cat_examples:
                return {
                    "tool": tool_name,
                    "category": cat_name,
                    "examples": cat_examples[tool_name]
                }
        return {"error": f"No examples found for tool '{tool_name}'"}
    
    if category:
        if category in examples:
            return {
                "category": category,
                "tools": examples[category]
            }
        return {"error": f"Category '{category}' not found", "available_categories": list(examples.keys())}
    
    return {
        "all_categories": list(examples.keys()),
        "examples": examples
    }


@mcp.tool(name="get_documentation_files", description="List available documentation files")
async def get_documentation_files() -> Dict[str, Any]:
    """
    Get list of available documentation files.
    
    Returns:
        List of documentation files with descriptions.
    """
    if not DOCS_PATH.exists():
        return {"error": "Documentation directory not found"}
    
    doc_files = []
    for file_path in DOCS_PATH.glob("*.pdf"):
        doc_files.append({
            "filename": file_path.name,
            "category": file_path.stem.split(" - ")[0] if " - " in file_path.stem else file_path.stem,
            "path": str(file_path.relative_to(Path(__file__).parent))
        })
    
    return {
        "documentation_path": str(DOCS_PATH),
        "total_files": len(doc_files),
        "files": sorted(doc_files, key=lambda x: x["category"])
    }


@mcp.tool(name="get_supported_metrics", description="Get comprehensive list of supported LinearB metrics")
async def get_supported_metrics() -> Dict[str, Any]:
    """
    Get comprehensive information about all supported LinearB metrics.
    
    Returns:
        Complete metrics reference including names, aggregations, descriptions, and units.
    """
    return {
        "total_metrics": len(SUPPORTED_METRICS),
        "categories": len(METRICS_CATEGORIES),
        "metrics": SUPPORTED_METRICS,
        "categories_info": METRICS_CATEGORIES,
        "usage_note": "Use these metric names in post_metrics() calls. Specify aggregation (p75, p50, avg) where supported."
    }


@mcp.tool(name="get_metrics_by_category", description="Get metrics organized by category")
async def get_metrics_by_category(category: Optional[str] = None) -> Dict[str, Any]:
    """
    Get metrics organized by category or get specific category metrics.
    
    Args:
        category: Optional category name (cycle_time, pull_requests, commits, releases, activity, branches, incidents)
    
    Returns:
        Metrics organized by category or specific category details.
    """
    if category:
        if category not in METRICS_CATEGORIES:
            return {
                "error": f"Category '{category}' not found",
                "available_categories": list(METRICS_CATEGORIES.keys())
            }
        
        cat_info = METRICS_CATEGORIES[category]
        metrics_details = {name: SUPPORTED_METRICS[name] for name in cat_info["metrics"]}
        
        return {
            "category": category,
            "name": cat_info["name"],
            "description": cat_info["description"],
            "total_metrics": len(cat_info["metrics"]),
            "metrics": metrics_details
        }
    
    # Return all categories with summary
    result = {
        "total_categories": len(METRICS_CATEGORIES),
        "categories": {}
    }
    
    for cat_key, cat_info in METRICS_CATEGORIES.items():
        result["categories"][cat_key] = {
            "name": cat_info["name"],
            "description": cat_info["description"],
            "metric_count": len(cat_info["metrics"]),
            "metrics": cat_info["metrics"]
        }
    
    return result


@mcp.tool(name="search_metrics", description="Search metrics by name or description")
async def search_metrics(
    search_term: str,
    category: Optional[str] = None,
    has_aggregation: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Search metrics by name or description with optional filtering.
    
    Args:
        search_term: Search term to match against metric names and descriptions
        category: Optional category filter
        has_aggregation: Optional filter for metrics that support aggregation (p75, p50, avg)
    
    Returns:
        Matching metrics with details.
    """
    if not search_term or len(search_term.strip()) < 2:
        raise ValueError("search_term must be at least 2 characters long")
    
    search_term = search_term.lower().strip()
    matching_metrics = {}
    
    for metric_name, metric_data in SUPPORTED_METRICS.items():
        # Check if search term matches name or description
        name_match = search_term in metric_name.lower()
        desc_match = search_term in metric_data["description"].lower()
        
        if not (name_match or desc_match):
            continue
        
        # Apply category filter
        if category and metric_data["category"] != category:
            continue
        
        # Apply aggregation filter
        if has_aggregation is not None:
            has_agg = len(metric_data["aggregations"]) > 0
            if has_aggregation != has_agg:
                continue
        
        matching_metrics[metric_name] = metric_data
    
    return {
        "search_term": search_term,
        "filters": {
            "category": category,
            "has_aggregation": has_aggregation
        },
        "total_matches": len(matching_metrics),
        "metrics": matching_metrics
    }


@mcp.tool(name="get_metric_examples", description="Get usage examples for metrics queries")
async def get_metric_examples() -> Dict[str, Any]:
    """
    Get practical examples of how to use metrics in post_metrics() calls.
    
    Returns:
        Example metric queries with different aggregations and combinations.
    """
    return {
        "examples": {
            "cycle_time_analysis": {
                "description": "Analyze development cycle time with different aggregations",
                "code": """await post_metrics(
    group_by="team",
    roll_up="1w",
    requested_metrics=[
        {"name": "branch.computed.cycle_time", "agg": "p75"},
        {"name": "branch.time_to_pr", "agg": "p50"},
        {"name": "branch.review_time", "agg": "avg"}
    ],
    time_ranges=[{"after": "2023-01-01", "before": "2023-01-31"}]
)""",
                "metrics_used": ["branch.computed.cycle_time", "branch.time_to_pr", "branch.review_time"]
            },
            "pr_quality_metrics": {
                "description": "Analyze pull request quality and review patterns",
                "code": """await post_metrics(
    group_by="repository",
    roll_up="1mo",
    requested_metrics=[
        {"name": "pr.merged"},
        {"name": "pr.review_depth"},
        {"name": "pr.merged.without.review.count"},
        {"name": "pr.merged.size", "agg": "p75"}
    ],
    time_ranges=[{"after": "2023-01-01", "before": "2023-12-31"}]
)""",
                "metrics_used": ["pr.merged", "pr.review_depth", "pr.merged.without.review.count", "pr.merged.size"]
            },
            "activity_overview": {
                "description": "Get overview of development activity",
                "code": """await post_metrics(
    group_by="organization",
    roll_up="1d",
    requested_metrics=[
        {"name": "commit.total.count"},
        {"name": "pr.new"},
        {"name": "pr.reviews"},
        {"name": "commit.activity_days"}
    ],
    time_ranges=[{"after": "2023-12-01", "before": "2023-12-31"}]
)""",
                "metrics_used": ["commit.total.count", "pr.new", "pr.reviews", "commit.activity_days"]
            },
            "code_quality_analysis": {
                "description": "Analyze code quality through rework and refactor metrics",
                "code": """await post_metrics(
    group_by="team",
    roll_up="1w",
    requested_metrics=[
        {"name": "commit.activity.new_work.count"},
        {"name": "commit.activity.rework.count"},
        {"name": "commit.activity.refactor.count"},
        {"name": "commit.total_changes"}
    ],
    time_ranges=[{"after": "2023-01-01", "before": "2023-03-31"}]
)""",
                "metrics_used": ["commit.activity.new_work.count", "commit.activity.rework.count", "commit.activity.refactor.count", "commit.total_changes"]
            },
            "reliability_metrics": {
                "description": "Monitor system reliability and incident metrics",
                "code": """await post_metrics(
    group_by="organization",
    roll_up="1mo",
    requested_metrics=[
        {"name": "pm.mttr"},
        {"name": "pm.cfr.issues.done"},
        {"name": "releases.count"}
    ],
    time_ranges=[{"after": "2023-01-01", "before": "2023-12-31"}]
)""",
                "metrics_used": ["pm.mttr", "pm.cfr.issues.done", "releases.count"]
            }
        },
        "aggregation_guide": {
            "p75": "75th percentile - good for understanding typical high-end performance",
            "p50": "50th percentile (median) - represents typical performance",
            "avg": "Average - useful for overall trends but can be skewed by outliers"
        },
        "best_practices": [
            "Use p75 for cycle time metrics to understand realistic delivery times",
            "Use p50 for median performance analysis",
            "Combine count metrics with time-based metrics for comprehensive analysis",
            "Use appropriate roll_up periods: 1d for detailed analysis, 1w for trends, 1mo for high-level overview"
        ]
    }


@mcp.tool(name="get_active_teams", description="Get list of active teams for analysis")
@mcp.tool(name="get_active_teams", description="Get list of active teams for analysis")
async def get_active_teams() -> Dict[str, Any]:
    """
    Get comprehensive information about all active teams.
    
    Returns:
        Complete active teams reference including types, comparability, and focus areas.
    """
    return {
        "total_teams": len(ACTIVE_TEAMS),
        "team_types": len(TEAM_TYPES),
        "teams": ACTIVE_TEAMS,
        "types": TEAM_TYPES,
        "usage_note": "Use team names in metrics queries. Engineering teams are comparable, QA teams should be analyzed separately."
    }


@mcp.tool(name="get_teams_by_type", description="Get teams filtered by type")
async def get_teams_by_type(team_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Get teams filtered by type (engineering or qa).
    
    Args:
        team_type: Optional team type filter ('engineering' or 'qa')
    
    Returns:
   fily type or overview of all types.
    """
    if team_type:
        if team_type not in TEAM_TYPES:
            return {
                "error": f"Team type '{team_type}' not found",
                "available_types": list(TEAM_TYPES.keys())
            }
        
        type_info = TEAM_TYPES[team_type]
        teams_details = {team_id: ACTIVE_TEAMS[team_id] for team_id in type_info["teams"]}
        
        return {
            "team_type": team_type,
            "name": type_info["name"],
            "description": type_info["description"],
            "comparable": type_info["comparable"],
            "total_teams": len(type_info["teams"]),
            "teams": teams_details
        }
    
    # Return all types with summary
    result = {
        "total_types": len(TEAM_TYPES),
        "types": {}
    }
    
    for type_key, type_info in TEAM_TYPES.items():
        result["types"][type_key] = {
            "name": type_info["name"],
            "description": type_info["description"],
            "comparable": type_info["comparable"],
            "team_count": len(type_info["teams"]),
            "teams": type_info["teams"]
        }
    
    return result


@mcp.tool(name="get_comparable_teams", description="Get teams that can be compared for analysis")
async def get_comparable_teams() -> Dict[str, Any]:
    """
    Get only the teams that are comparable for analysis (excludes QA teams).
    
    Returns:
        Engineering teams that can be compared in metrics analysis.
    """
    comparable_teams = {
        team_id: team_data 
        for team_id, team_data in ACTIVE_TEAMS.items() 
        if team_data["comparable"]
    }
    
    return {
        "total_comparable_teams": len(comparable_teams),
        "teams": comparable_teams,
        "excluded_teams": {
            team_id: team_data 
            for team_id, team_data in ACTIVE_TEAMS.items() 
            if not team_data["comparable"]
        },
        "usage_note": "These teams can be compared in metrics analysis. QA teams are tracked separately."
    }


@mcp.tool(name="search_teams_by_focus", description="Search teams by focus area or name")
async def search_teams_by_focus(
    search_term: str,
    team_type: Optional[str] = None,
    comparable_only: bool = False
) -> Dict[str, Any]:
    """
    Search teams by focus area, name, or description.
    
    Args:
        search_term: Search term to match against team names, descriptions, or focus areas
        team_type: Optional team type filter ('engineering' or 'qa')
        comparable_only: If True, only return comparable teams
    
    Returns:
        Matching teams with details.
    """
    if not search_term or len(search_term.strip()) < 2:
        raise ValueError("search_term must be at least 2 characters long")
    
    search_term = search_term.lower().strip()
    matching_teams = {}
    
    for team_id, team_data in ACTIVE_TEAMS.items():
        # Check if search term matches name, description, or focus areas
        name_match = search_term in team_data["name"].lower()
        desc_match = search_term in team_data["description"].lower()
        focus_match = any(search_term in area.lower() for area in team_data["focus_areas"])
        
        if not (name_match or desc_match or focus_match):
            continue
        
        # Apply team type filter
        if team_type and team_data["type"] != team_type:
            continue
        
        # Apply comparable filter
        if comparable_only and not team_data["comparable"]:
            continue
        
        matching_teams[team_id] = team_data
    
    return {
        "search_term": search_term,
        "filters": {
            "team_type": team_type,
            "comparable_only": comparable_only
        },
        "total_matches": len(matching_teams),
        "teams": matching_teams
    }

def _get_mcp_tool_name(endpoint_path: str, method: str) -> Optional[str]:
    """Helper function to map API endpoints to MCP tool names."""
    endpoint_map = {
        # Read-only endpoints (GET operations)
        ("GET", "/api/v1/deployments"): "list_deployments",
        ("GET", "/api/v2/teams"): "search_teams_v2",
        ("GET", "/api/v1/users"): "search_users",
        ("GET", "/api/v1/services/"): "get_services",
        ("GET", "/api/v1/services/{service_id}"): "get_service",
        ("GET", "/api/v1/incidents/{provider_id}"): "get_incident",
        ("GET", "/api/v1/health"): "health_check",
        
        # Read-only POST operations (search/query operations)
        ("POST", "/api/v1/incidents/search"): "search_incidents",
        ("POST", "/api/v2/measurements"): "post_metrics",
        ("POST", "/api/v2/measurements/export"): "export_metrics",
        
        # Write operations are commented out for read-only server
        # ("POST", "/api/v1/deployments"): "create_deployment",
        # ("POST", "/api/v2/teams"): "create_teams_v2",
        # ("DELETE", "/api/v2/teams/{team_id}"): "delete_team_v2",
        # ("PATCH", "/api/v2/teams/{team_id}"): "update_team_v2",
        # ("POST", "/api/v2/teams/{team_id}/members"): "add_team_members_v2",
        # ("DELETE", "/api/v2/teams/{team_id}/members/{user_id_or_email}"): "remove_team_member_v2",
        # ("POST", "/api/v1/users"): "create_users",
        # ("DELETE", "/api/v1/users/{user_id}"): "delete_user",
        # ("PATCH", "/api/v1/users/{user_id}"): "update_user",
        # ("POST", "/api/v1/incidents"): "create_incident",
        # ("POST", "/api/v1/incidents/{provider_id}"): "update_incident",
        # ("DELETE", "/api/v1/incidents/{provider_id}"): "delete_incident",
        # ("POST", "/api/v1/report/metric"): "post_custom_metric",
        # ("POST", "/api/v1/cycle-time-stages"): "create_cycle_time_stage",
    }
    
    return endpoint_map.get((method.upper(), endpoint_path))


# =============================================================================
# API REQUEST HELPER
# =============================================================================

async def _make_request(method: str, endpoint: str, params: Optional[Dict] = None, json_data: Optional[Dict] = None) -> Dict[str, Any]:
    """Helper function to make HTTP requests with proper error handling."""
    try:
        if method.upper() == "GET":
            response = await client.get(endpoint, params=params)
        elif method.upper() == "POST":
            response = await client.post(endpoint, params=params, json=json_data)
        elif method.upper() == "DELETE":
            response = await client.delete(endpoint)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        
        # Handle empty responses for DELETE operations
        if response.status_code == 204 or not response.content:
            return {"status": "success", "message": "Operation completed successfully"}
        
        return response.json()
    
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error {e.response.status_code} for {method} {endpoint}: {e.response.text}")
        raise Exception(f"API request failed with status {e.response.status_code}: {e.response.text}")
    except httpx.RequestError as e:
        logger.error(f"Request error for {method} {endpoint}: {str(e)}")
        raise Exception(f"Network error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error for {method} {endpoint}: {str(e)}")
        raise Exception(f"Unexpected error: {str(e)}")


@mcp.tool(name="list_deployments", description="List deployments with optional filtering parameters")
async def list_deployments(
    repository_id: Optional[int] = None,
    after: Optional[str] = None,
    before: Optional[str] = None,
    limit: Optional[int] = 10,
    offset: Optional[int] = 0,
    stage: Optional[str] = None,
    sort_by: Optional[str] = "published_at",
    sort_dir: Optional[str] = "desc",
    commit_sha: Optional[str] = None
) -> Dict[str, Any]:
    """
    List deployments with optional filtering.
    
    Args:
        repository_id: Filter by repository ID
        after: Filter deployments after this date (ISO format)
        before: Filter deployments before this date (ISO format)
        limit: Maximum number of results (1-100, default: 10)
        offset: Number of results to skip (default: 0)
        stage: Filter by deployment stage
        sort_by: Sort field (default: published_at)
        sort_dir: Sort direction (asc/desc, default: desc)
        commit_sha: Filter by specific commit SHA
    """
    params = {
        "repository_id": repository_id,
        "after": after,
        "before": before,
        "limit": min(limit or 10, 100),  # Enforce API limit
        "offset": max(offset or 0, 0),   # Ensure non-negative
        "stage": stage,
        "sort_by": sort_by,
        "sort_dir": sort_dir,
        "commit_sha": commit_sha
    }
    # Remove None values
    params = {k: v for k, v in params.items() if v is not None}
    
    return await _make_request("GET", "/api/v1/deployments", params=params)


@mcp.tool(name="search_teams_v2", description="Search teams with pagination (V2 API)")
async def search_teams_v2(
    offset: int = 0,
    page_size: int = 50,
    search_term: Optional[str] = None,
    nonmerged_members_only: bool = False
) -> Dict[str, Any]:
    """
    Search teams with pagination using V2 API.
    
    Args:
        offset: Pagination offset (default: 0)
        page_size: Number of teams per page (1-50, default: 50)
        search_term: Search term to filter teams (1-100 characters)
        nonmerged_members_only: If True, returns only contributors without parent contributors
    """
    params = {
        "offset": max(offset, 0),
        "page_size": min(max(page_size, 1), 50),
        "nonmerged_members_only": nonmerged_members_only
    }
    
    if search_term and search_term.strip():
        if len(search_term.strip()) < 1 or len(search_term.strip()) > 100:
            raise ValueError("search_term must be between 1 and 100 characters")
        params["search_term"] = search_term.strip()
    
    return await _make_request("GET", "/api/v2/teams", params=params)


# =============================================================================
# WRITE OPERATIONS DISABLED - READ-ONLY MCP SERVER
# =============================================================================
# The following tools are commented out to make this a read-only server
# Uncomment them if you need write operations

# @mcp.tool(name="create_teams_v2", description="Create teams in bulk (V2 API)")
# async def create_teams_v2(teams: List[Dict[str, Any]]) -> Dict[str, Any]:
#     """Create teams in bulk using V2 API."""
#     return await _make_request("POST", "/api/v2/teams", json_data=teams)

# @mcp.tool(name="delete_team_v2", description="Delete a team by ID (V2 API)")
# async def delete_team_v2(team_id: int) -> Dict[str, Any]:
#     """Delete a team by ID using V2 API."""
#     endpoint = f"/api/v2/teams/{team_id}"
#     return await _make_request("DELETE", endpoint)

# @mcp.tool(name="update_team_v2", description="Update a team by ID (V2 API)")
# async def update_team_v2(team_id: int, **kwargs) -> Dict[str, Any]:
#     """Update a team by ID using V2 API."""
#     endpoint = f"/api/v2/teams/{team_id}"
#     return await _make_request("PATCH", endpoint, json_data=kwargs)

# @mcp.tool(name="add_team_members_v2", description="Add members to a team (V2 API)")
# async def add_team_members_v2(team_id: int, **kwargs) -> List[Dict[str, Any]]:
#     """Add members to a team using V2 API."""
#     endpoint = f"/api/v2/teams/{team_id}/members"
#     return await _make_request("POST", endpoint, json_data=kwargs)

# @mcp.tool(name="remove_team_member_v2", description="Remove a member from a team (V2 API)")
# async def remove_team_member_v2(team_id: int, user_id_or_email: str) -> Dict[str, Any]:
#     """Remove a member from a team using V2 API."""
#     endpoint = f"/api/v2/teams/{team_id}/members/{user_id_or_email.strip()}"
#     return await _make_request("DELETE", endpoint)


@mcp.tool(name="get_services", description="Get all services, optionally filtered by repository")
async def get_services(repository_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Get all services, optionally filtered by repository.
    
    Args:
        repository_id: Optional repository ID to filter services
    """
    params = {}
    if repository_id is not None:
        params["repository_id"] = repository_id
    
    return await _make_request("GET", "/api/v1/services/", params=params)


@mcp.tool(name="get_service", description="Get a specific service by ID")
async def get_service(service_id: int) -> Dict[str, Any]:
    """
    Get a specific service by ID.
    
    Args:
        service_id: The service ID to retrieve
    """
    if service_id <= 0:
        raise ValueError("service_id must be a positive integer")
    
    endpoint = f"/api/v1/services/{service_id}"
    return await _make_request("GET", endpoint)


@mcp.tool(name="get_incident", description="Get a specific incident by provider ID")
async def get_incident(provider_id: str) -> Dict[str, Any]:
    """
    Get a specific incident by provider ID.
    
    Args:
        provider_id: The incident provider ID to retrieve
    """
    if not provider_id or not provider_id.strip():
        raise ValueError("provider_id is required and cannot be empty")
    
    endpoint = f"/api/v1/incidents/{provider_id}"
    return await _make_request("GET", endpoint)


@mcp.tool(name="health_check", description="Check API health status")
async def health_check() -> Dict[str, Any]:
    """
    Check the health status of the LinearB API.
    """
    return await _make_request("GET", "/api/v1/health")

# @mcp.tool(name="create_deployment", description="Create a new deployment")
# async def create_deployment(repo_url: str, ref_name: str, **kwargs) -> Dict[str, Any]:
#     """Create a new deployment."""
#     payload = {"repo_url": repo_url.strip(), "ref_name": ref_name.strip(), **kwargs}
#     return await _make_request("POST", "/api/v1/deployments", json_data=payload)


@mcp.tool(name="post_metrics", description="Query metrics data from LinearB")
async def post_metrics(
    group_by: str,
    roll_up: str,
    requested_metrics: List[Dict[str, str]],
    time_ranges: List[Dict[str, str]],
    repository_ids: Optional[List[int]] = None,
    team_ids: Optional[List[int]] = None
) -> List[Dict[str, Any]]:
    """
    Query metrics data from LinearB.
    
    Args:
        group_by: Grouping level (e.g., 'organization', 'team', 'repository')
        roll_up: Time aggregation (e.g., '1d', '1w', '1mo', 'custom')
        requested_metrics: List of metrics with optional aggregation (e.g., [{"name": "branch.computed.cycle_time", "agg": "p75"}])
        time_ranges: List of time ranges (e.g., [{"after": "2023-01-01", "before": "2023-01-31"}])
        repository_ids: Optional list of repository IDs to filter
        team_ids: Optional list of team IDs to filter
    """
    if not requested_metrics:
        raise ValueError("requested_metrics is required and cannot be empty")
    if not time_ranges:
        raise ValueError("time_ranges is required and cannot be empty")
    
    payload = {
        "group_by": group_by,
        "roll_up": roll_up,
        "requested_metrics": requested_metrics,
        "time_ranges": time_ranges
    }
    
    if repository_ids:
        payload["repository_ids"] = repository_ids
    if team_ids:
        payload["team_ids"] = team_ids
    
    return await _make_request("POST", "/api/v2/measurements", json_data=payload)


@mcp.tool(name="export_metrics", description="Export metrics data in CSV or JSON format")
async def export_metrics(
    group_by: str,
    roll_up: str,
    requested_metrics: List[Dict[str, str]],
    time_ranges: List[Dict[str, str]],
    file_format: str = "csv",
    repository_ids: Optional[List[int]] = None,
    team_ids: Optional[List[int]] = None
) -> Dict[str, Any]:
    """
    Export metrics data in CSV or JSON format.
    
    Args:
        group_by: Grouping level (e.g., 'organization', 'team', 'repository')
        roll_up: Time aggregation (e.g., '1d', '1w', '1mo', 'custom')
        requested_metrics: List of metrics with optional aggregation
        time_ranges: List of time ranges
        file_format: Export format ('csv' or 'json', default: 'csv')
        repository_ids: Optional list of repository IDs to filter
        team_ids: Optional list of team IDs to filter
    """
    if file_format not in ["csv", "json"]:
        raise ValueError("file_format must be 'csv' or 'json'")
    
    payload = {
        "group_by": group_by,
        "roll_up": roll_up,
        "requested_metrics": requested_metrics,
        "time_ranges": time_ranges
    }
    
    if repository_ids:
        payload["repository_ids"] = repository_ids
    if team_ids:
        payload["team_ids"] = team_ids
    
    params = {"file_format": file_format}
    return await _make_request("POST", "/api/v2/measurements/export", params=params, json_data=payload)


@mcp.tool(name="search_users", description="Search users with pagination and filtering")
async def search_users(
    offset: int = 0,
    page_size: int = 50,
    order_by: Optional[str] = None,
    order_dir: Optional[str] = None,
    search_by_field: Optional[str] = None,
    search_term: Optional[str] = None,
    user_role: Optional[str] = None,
    include_user_children: bool = False
) -> Dict[str, Any]:
    """
    Search users with pagination and filtering.
    
    Args:
        offset: Pagination offset (default: 0)
        page_size: Number of users per page (1-50, default: 50)
        order_by: Field to order by ('name' or 'email')
        order_dir: Order direction ('ASC' or 'DESC')
        search_by_field: Field to search by ('name' or 'email')
        search_term: Search term (1-100 characters)
        user_role: User role filter ('admin', 'editor', 'viewer', 'external', 'basic')
        include_user_children: Include user children in response
    """
    params = {
        "offset": max(offset, 0),
        "page_size": min(max(page_size, 1), 50),
        "include_user_children": include_user_children
    }
    
    if order_by and order_by in ["name", "email"]:
        params["order_by"] = order_by
    
    if order_dir and order_dir in ["ASC", "DESC"]:
        params["order_dir"] = order_dir
    
    if search_by_field and search_by_field in ["name", "email"]:
        params["search_by_field"] = search_by_field
    
    if search_term and search_term.strip():
        if len(search_term.strip()) < 1 or len(search_term.strip()) > 100:
            raise ValueError("search_term must be between 1 and 100 characters")
        params["search_term"] = search_term.strip()
    
    if user_role and user_role in ["admin", "editor", "viewer", "external", "basic"]:
        params["user_role"] = user_role
    
    return await _make_request("GET", "/api/v1/users", params=params)


# @mcp.tool(name="create_users", description="Create users in bulk")
# async def create_users(users: List[Dict[str, Any]]) -> Dict[str, Any]:
#     """Create users in bulk."""
#     return await _make_request("POST", "/api/v1/users", json_data=users)

# @mcp.tool(name="delete_user", description="Delete a user by ID")
# async def delete_user(user_id: int) -> Dict[str, Any]:
#     """Delete a user by ID."""
#     endpoint = f"/api/v1/users/{user_id}"
#     return await _make_request("DELETE", endpoint)

# @mcp.tool(name="update_user", description="Update a user by ID")
# async def update_user(user_id: int, **kwargs) -> Dict[str, Any]:
#     """Update a user by ID."""
#     endpoint = f"/api/v1/users/{user_id}"
#     return await _make_request("PATCH", endpoint, json_data=kwargs)

# @mcp.tool(name="create_incident", description="Create a new incident")
# async def create_incident(provider_id: str, title: str, **kwargs) -> Dict[str, Any]:
#     """Create a new incident."""
#     payload = {"provider_id": provider_id.strip(), "title": title.strip(), **kwargs}
#     return await _make_request("POST", "/api/v1/incidents", json_data=payload)


@mcp.tool(name="search_incidents", description="Search incidents with filtering")
async def search_incidents(
    limit: int = 10,
    offset: int = 0,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    after: Optional[str] = None,
    before: Optional[str] = None
) -> Dict[str, Any]:
    """
    Search incidents with filtering options.
    
    Args:
        limit: Maximum number of results (default: 10)
        offset: Number of results to skip (default: 0)
        status: Filter by incident status
        severity: Filter by incident severity
        after: Filter incidents after this date (ISO format)
        before: Filter incidents before this date (ISO format)
    """
    payload = {
        "limit": min(limit, 100),  # Enforce reasonable limit
        "offset": max(offset, 0)   # Ensure non-negative
    }
    
    if status:
        payload["status"] = status
    if severity:
        payload["severity"] = severity
    if after:
        payload["after"] = after
    if before:
        payload["before"] = before
    
    return await _make_request("POST", "/api/v1/incidents/search", json_data=payload)


# @mcp.tool(name="update_incident", description="Update an existing incident")
# async def update_incident(provider_id: str, **kwargs) -> Dict[str, Any]:
#     """Update an existing incident."""
#     endpoint = f"/api/v1/incidents/{provider_id}"
#     return await _make_request("POST", endpoint, json_data=kwargs)


# @mcp.tool(name="create_cycle_time_stage", description="Create a custom cycle time stage")
# async def create_cycle_time_stage(name: str, **kwargs) -> Dict[str, Any]:
#     """Create a custom cycle time stage."""
#     payload = {"name": name.strip(), **kwargs}
#     return await _make_request("POST", "/api/v1/cycle-time-stages", json_data=payload)


# @mcp.tool(name="post_custom_metric", description="Post a custom metric to LinearB")
# async def post_custom_metric(metric_name: str, value: float, **kwargs) -> Dict[str, Any]:
#     """Post a custom metric to LinearB."""
#     payload = {"metric_name": metric_name.strip(), "value": value, **kwargs}
#     return await _make_request("POST", "/api/v1/report/metric", json_data=payload)


# @mcp.tool(name="delete_incident", description="Delete an incident")
# async def delete_incident(provider_id: str) -> Dict[str, Any]:
#     """Delete an incident by provider ID."""
#     endpoint = f"/api/v1/incidents/{provider_id}"
#     return await _make_request("DELETE", endpoint)
async def cleanup():
    """Cleanup function to close HTTP client."""
    await client.aclose()


if __name__ == "__main__":
    import atexit
    import asyncio
    
    # Register cleanup function
    atexit.register(lambda: asyncio.run(cleanup()))
    
    try:
        logger.info("Starting LinearB MCP Server...")
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise
