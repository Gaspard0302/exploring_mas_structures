#!/usr/bin/env python3
"""
Quick test script for LLM-powered TSP evaluation
Tests basic functionality with minimal example
"""

import os
import sys
from evaluations.tsp.llm_integration import get_llm_integration, get_logger
from evaluations.tsp.llm_hierarchical_tsp import evaluate_llm_hierarchical_tsp

def test_configuration():
    """Test configuration setup"""
    print("🧪 Testing Configuration...")
    
    try:
        # Try to import config
        try:
            from config import get_openai_api_key
            api_key = get_openai_api_key()
            print("✅ Configuration file found and API key loaded")
            return True, api_key
        except ImportError:
            print("⚠️ No config.py found, checking environment variable...")
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                print("✅ API key found in environment variable")
                return True, api_key
            else:
                print("❌ No API key found")
                print("   Please either:")
                print("   1. Copy config_template.py to config.py and set your API key")
                print("   2. Set OPENAI_API_KEY environment variable")
                return False, None
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False, None

def test_llm_integration():
    """Test basic LLM integration"""
    print("\n🧪 Testing LLM Integration...")
    
    config_ok, api_key = test_configuration()
    if not config_ok:
        return False
    
    try:
        # Test connection
        llm = get_llm_integration(api_key)
        response = llm.call_llm(
            agent_name="TestAgent",
            agent_type="test",
            call_type="connection_test",
            prompt="Respond with exactly 'SUCCESS' if you can read this.",
            context={"test": True}
        )
        
        if "SUCCESS" in response.upper():
            print("✅ LLM connection successful")
            return True
        else:
            print(f"⚠️ Unexpected response: {response}")
            return False
            
    except Exception as e:
        print(f"❌ LLM connection failed: {e}")
        return False

def test_hierarchical_tsp():
    """Test hierarchical TSP with minimal example"""
    print("\n🧪 Testing Hierarchical TSP...")
    
    config_ok, api_key = test_configuration()
    if not config_ok:
        return False
    
    try:
        # Minimal test case
        cities = [(0, 0), (1, 1), (2, 0), (1, -1)]  # 4 cities in diamond pattern
        n_agents = 2
        
        print(f"   Cities: {cities}")
        print(f"   Agents: {n_agents}")
        print("   Running evaluation... (this may take 30-60 seconds)")
        
        result = evaluate_llm_hierarchical_tsp(
            cities=cities,
            n_agents=n_agents,
            api_key=api_key,
            seed=42
        )
        
        # Check results
        if result.get('total_distance', float('inf')) < float('inf'):
            print(f"✅ Distance: {result['total_distance']:.2f}")
            print(f"✅ Communications: {result['communication_overhead']}")
            
            additional = result.get('additional_metrics', {})
            print(f"✅ LLM Calls: {additional.get('llm_calls', 0)}")
            print(f"✅ Cost: ${additional.get('total_llm_cost', 0):.3f}")
            
            return True
        else:
            print("❌ Invalid results returned")
            return False
            
    except Exception as e:
        print(f"❌ Hierarchical TSP test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting LLM TSP Tests")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_configuration),
        ("LLM Integration", test_llm_integration),
        ("Hierarchical TSP", test_hierarchical_tsp)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                break  # Stop on first failure for dependency chain
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            break
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("✅ All tests passed! LLM TSP evaluation is ready.")
        print("\nNext steps:")
        print("1. Run quick evaluation: python -m evaluations.tsp.llm_main --quick")
        print("2. Run full evaluation: python -m evaluations.tsp.llm_main")
        print("3. View detailed docs: docs/LLM_TSP_EVALUATION.md")
    elif passed == 0:
        print("❌ Configuration failed. Please setup your API key:")
        print("1. Copy: cp config_template.py config.py")
        print("2. Edit config.py and set your OpenAI API key")
        print("3. Or set environment variable: export OPENAI_API_KEY='your-key'")
        return 1
    else:
        print("❌ Some tests failed. Check error messages above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 