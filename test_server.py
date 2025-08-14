#!/usr/bin/env python3
"""
Test script for LinearB MCP Server (Read-Only)
Run this to validate basic read functionality
"""

import asyncio
import os
import sys
from server import health_check, search_teams_v2, list_deployments, discover_api, get_api_categories, get_usage_examples, get_supported_metrics, search_metrics, get_active_teams, get_comparable_teams

async def test_health_check():
    """Test the health check endpoint"""
    try:
        result = await health_check()
        print("✅ Health check passed:", result)
        return True
    except Exception as e:
        print("❌ Health check failed:", str(e))
        return False

async def test_search_teams_v2():
    """Test searching teams with V2 API"""
    try:
        result = await search_teams_v2(page_size=10)
        teams_count = len(result.get('items', []))
        total_count = result.get('total', 0)
        print(f"✅ Search teams V2 passed, found {teams_count} teams (total: {total_count})")
        return True
    except Exception as e:
        print("❌ Search teams V2 failed:", str(e))
        return False

async def test_list_deployments():
    """Test listing deployments"""
    try:
        result = await list_deployments(limit=5)
        print("✅ List deployments passed, found", len(result.get('deployments', [])), "deployments")
        return True
    except Exception as e:
        print("❌ List deployments failed:", str(e))
        return False

async def test_discover_api():
    """Test API discovery service"""
    try:
        result = await discover_api()
        endpoint_count = len(result.get('endpoints', {}))
        print(f"✅ API discovery passed, found {endpoint_count} endpoints")
        return True
    except Exception as e:
        print("❌ API discovery failed:", str(e))
        return False

async def test_get_api_categories():
    """Test API categories"""
    try:
        result = await get_api_categories()
        category_count = result.get('total_categories', 0)
        endpoint_count = result.get('total_endpoints', 0)
        print(f"✅ API categories passed, found {category_count} categories with {endpoint_count} endpoints")
        return True
    except Exception as e:
        print("❌ API categories failed:", str(e))
        return False

async def test_get_usage_examples():
    """Test usage examples"""
    try:
        result = await get_usage_examples(category="deployments")
        tools_count = len(result.get('tools', {}))
        print(f"✅ Usage examples passed, found examples for {tools_count} deployment tools")
        return True
    except Exception as e:
        print("❌ Usage examples failed:", str(e))
        return False

async def test_get_supported_metrics():
    """Test supported metrics reference"""
    try:
        result = await get_supported_metrics()
        metrics_count = result.get('total_metrics', 0)
        categories_count = result.get('categories', 0)
        print(f"✅ Supported metrics passed, found {metrics_count} metrics in {categories_count} categories")
        return True
    except Exception as e:
        print("❌ Supported metrics failed:", str(e))
        return False

async def test_search_metrics():
    """Test metrics search"""
    try:
        result = await search_metrics("cycle", has_aggregation=True)
        matches_count = result.get('total_matches', 0)
        print(f"✅ Metrics search passed, found {matches_count} cycle time metrics with aggregation")
        return True
    except Exception as e:
        print("❌ Metrics search failed:", str(e))
        return False

async def test_get_active_teams():
    """Test active teams reference"""
    try:
        result = await get_active_teams()
        teams_count = result.get('total_teams', 0)
        types_count = result.get('team_types', 0)
        print(f"✅ Active teams passed, found {teams_count} teams in {types_count} types")
        return True
    except Exception as e:
        print("❌ Active teams failed:", str(e))
        return False

async def test_get_comparable_teams():
    """Test comparable teams"""
    try:
        result = await get_comparable_teams()
        comparable_count = result.get('total_comparable_teams', 0)
        excluded_count = len(result.get('excluded_teams', {}))
        print(f"✅ Comparable teams passed, found {comparable_count} comparable teams, {excluded_count} excluded")
        return True
    except Exception as e:
        print("❌ Comparable teams failed:", str(e))
        return False

async def main():
    """Run all tests"""
    print("🧪 Testing LinearB MCP Server...")
    print("=" * 50)
    
    # Check if API key is set
    api_key = os.getenv("LINEARB_API_KEY")
    if not api_key or api_key == "your-api-key-here":
        print("⚠️  Warning: LINEARB_API_KEY not properly set")
        print("   Set your API key: export LINEARB_API_KEY='your-actual-key'")
        print()
    
    tests = [
        ("API Discovery", test_discover_api),
        ("API Categories", test_get_api_categories),
        ("Usage Examples", test_get_usage_examples),
        ("Supported Metrics", test_get_supported_metrics),
        ("Metrics Search", test_search_metrics),
        ("Active Teams", test_get_active_teams),
        ("Comparable Teams", test_get_comparable_teams),
        ("Health Check", test_health_check),
        ("Search Teams V2", test_search_teams_v2),
        ("List Deployments", test_list_deployments),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        if await test_func():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Tests completed: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("💥 Some tests failed. Check your API key and network connection.")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))