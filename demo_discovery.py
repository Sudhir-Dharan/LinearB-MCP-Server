#!/usr/bin/env python3
"""
Demo script showcasing the LinearB MCP Server Discovery Service
This script demonstrates how to use the discovery tools to explore the API
"""

import asyncio
import json
from server import (
    discover_api, get_api_categories, get_endpoint_details, 
    get_usage_examples, get_documentation_files
)

async def demo_discovery_service():
    """Demonstrate the discovery service capabilities"""
    
    print("🔍 LinearB MCP Server Discovery Service Demo")
    print("=" * 60)
    
    # 1. API Overview
    print("\n1️⃣  API Overview")
    print("-" * 30)
    try:
        api_info = await discover_api()
        print(f"📊 Total Endpoints: {len(api_info.get('endpoints', {}))}")
        print(f"🏷️  API Version: {api_info.get('api_info', {}).get('version', 'Unknown')}")
        print(f"🌐 Base URL: {api_info.get('base_url', 'Unknown')}")
        
        # Show categories summary
        categories = api_info.get('categories', {})
        print(f"📂 Categories: {len([cat for cat in categories.values() if cat])}")
        for cat_name, endpoints in categories.items():
            if endpoints:
                print(f"   • {cat_name}: {len(endpoints)} endpoints")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 2. Category Details
    print("\n2️⃣  API Categories")
    print("-" * 30)
    try:
        categories = await get_api_categories()
        print(f"📊 Total Categories: {categories['total_categories']}")
        print(f"🔧 Total Tools: {categories['total_endpoints']}")
        
        for cat_name, cat_info in categories['categories'].items():
            print(f"\n📁 {cat_name.upper()}")
            print(f"   Description: {cat_info['description']}")
            for endpoint in cat_info['endpoints'][:2]:  # Show first 2 endpoints
                print(f"   • {endpoint['tool']} ({endpoint['method']} {endpoint['path']})")
            if len(cat_info['endpoints']) > 2:
                print(f"   ... and {len(cat_info['endpoints']) - 2} more")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 3. Endpoint Details
    print("\n3️⃣  Endpoint Details Example")
    print("-" * 30)
    try:
        details = await get_endpoint_details("/api/v1/deployments", "GET")
        print(f"🎯 Endpoint: {details['endpoint']}")
        print(f"🔧 MCP Tool: {details['mcp_tool_name']}")
        print(f"📝 Summary: {details['summary']}")
        print(f"🏷️  Tags: {', '.join(details['tags'])}")
        
        # Show parameters
        query_params = details['parameters']['query']
        print(f"📋 Query Parameters: {len(query_params)}")
        for param in query_params[:3]:  # Show first 3 parameters
            required = "✅" if param['required'] else "⭕"
            print(f"   {required} {param['name']} ({param['type']}): {param['description'][:50]}...")
        if len(query_params) > 3:
            print(f"   ... and {len(query_params) - 3} more parameters")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 4. Usage Examples
    print("\n4️⃣  Usage Examples")
    print("-" * 30)
    try:
        examples = await get_usage_examples(category="deployments")
        print(f"📚 Examples for: {examples['category']}")
        
        for tool_name, tool_examples in examples['tools'].items():
            print(f"\n🔧 {tool_name}")
            print(f"   Description: {tool_examples['description']}")
            
            for i, example in enumerate(tool_examples['examples'][:1], 1):  # Show first example
                print(f"   Example {i}: {example['title']}")
                print(f"   Code: {example['code']}")
                break  # Just show one example per tool
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 5. Documentation Files
    print("\n5️⃣  Documentation Files")
    print("-" * 30)
    try:
        docs = await get_documentation_files()
        print(f"📚 Total Documentation Files: {docs['total_files']}")
        print(f"📁 Documentation Path: {docs['documentation_path']}")
        
        # Group by category
        categories = {}
        for doc in docs['files']:
            category = doc['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(doc['filename'])
        
        for category, files in list(categories.items())[:5]:  # Show first 5 categories
            print(f"   📂 {category}: {files[0]}")
        
        if len(categories) > 5:
            print(f"   ... and {len(categories) - 5} more categories")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 6. Interactive Example
    print("\n6️⃣  Interactive Example")
    print("-" * 30)
    print("💡 Try these commands in your MCP client:")
    print("   • discover_api() - Get complete API overview")
    print("   • get_api_categories() - Browse by categories")
    print("   • get_endpoint_details('/api/v1/teams/', 'GET') - Explore specific endpoints")
    print("   • get_usage_examples(tool_name='list_deployments') - Get code examples")
    print("   • get_documentation_files() - Browse available docs")
    print("   • get_supported_metrics() - Get all 22 supported metrics")
    print("   • search_metrics('cycle', has_aggregation=True) - Find cycle time metrics")
    print("   • get_metrics_by_category('pull_requests') - Get PR metrics")
    print("   • get_metric_examples() - Get practical metric usage examples")
    print("   • get_active_teams() - Get all 7 active teams (6 engineering + 1 QA)")
    print("   • get_comparable_teams() - Get 6 engineering teams for comparison")
    print("   • search_teams_by_focus('integration') - Find integration teams")
    print("   • get_teams_by_type('qa') - Get QA teams (tracked separately)")
    
    print("\n✨ Discovery service provides comprehensive API exploration!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(demo_discovery_service())