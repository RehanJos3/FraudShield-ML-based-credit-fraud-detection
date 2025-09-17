#!/usr/bin/env python3
"""
Simple Backend Test for Credit Card Fraud Detection System
Tests core functionality with localhost connection
"""

import requests
import json
import time

# Test with localhost
BACKEND_URL = "http://localhost:8001/api"

def test_basic_endpoints():
    """Test basic endpoints"""
    results = {}
    
    print("🧪 Testing Basic Endpoints...")
    
    # Test health check
    try:
        response = requests.get(f"{BACKEND_URL}/fraud/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            results['health'] = {'success': True, 'data': data}
            print(f"✅ Health Check: {data.get('status')} - Models: {data.get('models_loaded', 0)}")
        else:
            results['health'] = {'success': False, 'error': f"HTTP {response.status_code}"}
            print(f"❌ Health Check Failed: HTTP {response.status_code}")
    except Exception as e:
        results['health'] = {'success': False, 'error': str(e)}
        print(f"❌ Health Check Error: {e}")
    
    # Test dataset info
    try:
        response = requests.get(f"{BACKEND_URL}/fraud/dataset/info", timeout=5)
        if response.status_code == 200:
            data = response.json()
            total = data.get('total_transactions', 0)
            fraud_pct = data.get('fraud_percentage', '0%')
            results['dataset'] = {'success': True, 'data': data}
            print(f"✅ Dataset Info: {total:,} transactions, {fraud_pct} fraud")
        else:
            results['dataset'] = {'success': False, 'error': f"HTTP {response.status_code}"}
            print(f"❌ Dataset Info Failed: HTTP {response.status_code}")
    except Exception as e:
        results['dataset'] = {'success': False, 'error': str(e)}
        print(f"❌ Dataset Info Error: {e}")
    
    # Test fraud info
    try:
        response = requests.get(f"{BACKEND_URL}/fraud/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = data.get('available_models', [])
            results['fraud_info'] = {'success': True, 'data': data}
            print(f"✅ Fraud Info: {len(models)} models available")
        else:
            results['fraud_info'] = {'success': False, 'error': f"HTTP {response.status_code}"}
            print(f"❌ Fraud Info Failed: HTTP {response.status_code}")
    except Exception as e:
        results['fraud_info'] = {'success': False, 'error': str(e)}
        print(f"❌ Fraud Info Error: {e}")
    
    # Test model status
    try:
        response = requests.get(f"{BACKEND_URL}/fraud/models/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            available = data.get('available_models', [])
            results['model_status'] = {'success': True, 'data': data, 'models': available}
            print(f"✅ Model Status: {len(available)} models trained")
        else:
            results['model_status'] = {'success': False, 'error': f"HTTP {response.status_code}"}
            print(f"❌ Model Status Failed: HTTP {response.status_code}")
    except Exception as e:
        results['model_status'] = {'success': False, 'error': str(e)}
        print(f"❌ Model Status Error: {e}")
    
    return results

def test_model_training():
    """Test model training"""
    print("\n🤖 Testing Model Training...")
    
    try:
        payload = {"balance_method": "smote", "retrain": False}
        response = requests.post(f"{BACKEND_URL}/fraud/train", json=payload, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            message = data.get('message', '')
            print(f"✅ Model Training: {message}")
            return {'success': True, 'data': data}
        else:
            print(f"❌ Model Training Failed: HTTP {response.status_code}")
            return {'success': False, 'error': f"HTTP {response.status_code}"}
    except Exception as e:
        print(f"❌ Model Training Error: {e}")
        return {'success': False, 'error': str(e)}

def main():
    print("🚀 Simple Credit Card Fraud Detection Backend Test")
    print("=" * 60)
    
    # Test basic endpoints
    basic_results = test_basic_endpoints()
    
    # Test model training
    training_result = test_model_training()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    total_tests = len(basic_results) + 1
    passed_tests = sum(1 for r in basic_results.values() if r['success']) + (1 if training_result['success'] else 0)
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {passed_tests/total_tests*100:.1f}%")
    
    # Check critical systems
    critical_ok = (
        basic_results.get('health', {}).get('success', False) and
        basic_results.get('dataset', {}).get('success', False) and
        basic_results.get('fraud_info', {}).get('success', False)
    )
    
    if critical_ok:
        print("✅ All critical systems operational")
    else:
        print("🚨 Critical system failures detected")
    
    # Model status
    models = basic_results.get('model_status', {}).get('models', [])
    if models:
        print(f"🤖 Models Available: {len(models)} - {models}")
    else:
        print("🤖 Models Status: Training in progress or not started")
    
    return {
        'basic_results': basic_results,
        'training_result': training_result,
        'summary': {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'success_rate': passed_tests/total_tests*100,
            'critical_ok': critical_ok,
            'models_available': models
        }
    }

if __name__ == "__main__":
    results = main()
    
    # Save results
    with open('/app/simple_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📁 Results saved to: /app/simple_test_results.json")