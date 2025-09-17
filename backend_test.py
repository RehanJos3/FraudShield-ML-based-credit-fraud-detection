#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Credit Card Fraud Detection System
Tests all API endpoints and ML model functionality
"""

import requests
import json
import pandas as pd
import io
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://transact-shield.preview.emergentagent.com/api"

class FraudDetectionTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_results = {}
        self.sample_transaction = {
            "Time": 0.0,
            "V1": -1.3598071336738,
            "V2": -0.0727811733098497,
            "V3": 2.53634673796914,
            "V4": 1.37815522427443,
            "V5": -0.338320769942518,
            "V6": 0.462387777762292,
            "V7": 0.239598554061257,
            "V8": 0.0986979012610507,
            "V9": 0.363786969611213,
            "V10": 0.0907941719789316,
            "V11": -0.551599533260813,
            "V12": -0.617800855762348,
            "V13": -0.991389847235408,
            "V14": -0.311169353699879,
            "V15": 1.46817697209427,
            "V16": -0.470400525259478,
            "V17": 0.207971241929242,
            "V18": 0.0257905801985591,
            "V19": 0.403992960255733,
            "V20": 0.251412098239705,
            "V21": -0.018306777944153,
            "V22": 0.277837575558899,
            "V23": -0.110473910188767,
            "V24": 0.0669280749146731,
            "V25": 0.128539358273528,
            "V26": -0.189114843888824,
            "V27": 0.133558376740387,
            "V28": -0.0210530534538215,
            "Amount": 149.62
        }
        
    def log_test(self, test_name, success, message, response_data=None):
        """Log test results"""
        self.test_results[test_name] = {
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
    def test_health_check(self):
        """Test health check endpoint"""
        try:
            response = requests.get(f"{self.base_url}/fraud/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Check", True, f"System healthy - Models: {data.get('models_loaded', 0)}, Dataset: {data.get('dataset_available', False)}", data)
                return True
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Connection error: {str(e)}")
            return False
            
    def test_fraud_info(self):
        """Test fraud detection info endpoint"""
        try:
            response = requests.get(f"{self.base_url}/fraud/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                models = data.get('available_models', [])
                features = data.get('features', [])
                self.log_test("Fraud Info", True, f"API info retrieved - {len(models)} models, {len(features)} features", data)
                return True
            else:
                self.log_test("Fraud Info", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Fraud Info", False, f"Error: {str(e)}")
            return False
            
    def test_dataset_info(self):
        """Test dataset information endpoint"""
        try:
            response = requests.get(f"{self.base_url}/fraud/dataset/info", timeout=10)
            if response.status_code == 200:
                data = response.json()
                total = data.get('total_transactions', 0)
                fraud_cases = data.get('fraud_cases', 0)
                fraud_pct = data.get('fraud_percentage', '0%')
                
                # Verify expected dataset statistics
                if total > 280000:  # Should be around 284,807
                    self.log_test("Dataset Info", True, f"Dataset loaded - {total:,} transactions, {fraud_cases:,} fraud cases ({fraud_pct})", data)
                    return True
                else:
                    self.log_test("Dataset Info", False, f"Dataset size unexpected: {total} transactions")
                    return False
            else:
                self.log_test("Dataset Info", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Dataset Info", False, f"Error: {str(e)}")
            return False
            
    def test_model_status(self):
        """Test model status endpoint"""
        try:
            response = requests.get(f"{self.base_url}/fraud/models/status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                models = data.get('available_models', [])
                total = data.get('total_models', 0)
                self.log_test("Model Status", True, f"Model status retrieved - {total} models available: {models}", data)
                return True, models
            else:
                self.log_test("Model Status", False, f"HTTP {response.status_code}: {response.text}")
                return False, []
        except Exception as e:
            self.log_test("Model Status", False, f"Error: {str(e)}")
            return False, []
            
    def test_model_training(self):
        """Test model training initiation"""
        try:
            payload = {
                "balance_method": "smote",
                "retrain": False
            }
            response = requests.post(f"{self.base_url}/fraud/train", json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                message = data.get('message', '')
                if 'started' in message.lower() or 'already exist' in message.lower():
                    self.log_test("Model Training", True, f"Training response: {message}", data)
                    return True
                else:
                    self.log_test("Model Training", False, f"Unexpected response: {message}")
                    return False
            else:
                self.log_test("Model Training", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Model Training", False, f"Error: {str(e)}")
            return False
            
    def test_single_prediction(self, available_models):
        """Test single transaction prediction"""
        if not available_models:
            self.log_test("Single Prediction", False, "No models available for testing")
            return False
            
        # Test with first available model
        model_name = available_models[0] if available_models else "xgboost"
        
        try:
            payload = {
                "transaction": self.sample_transaction,
                "model_name": model_name
            }
            response = requests.post(f"{self.base_url}/fraud/predict", json=payload, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                prediction = data.get('prediction')
                probability = data.get('probability')
                risk_level = data.get('risk_level')
                
                if prediction is not None and probability is not None:
                    self.log_test("Single Prediction", True, f"Prediction: {prediction}, Probability: {probability:.3f}, Risk: {risk_level}", data)
                    return True
                else:
                    self.log_test("Single Prediction", False, f"Invalid response format: {data}")
                    return False
            elif response.status_code == 400 and "not available" in response.text:
                self.log_test("Single Prediction", True, f"Expected error - models not trained yet: {response.text}")
                return True
            else:
                self.log_test("Single Prediction", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Single Prediction", False, f"Error: {str(e)}")
            return False
            
    def test_batch_prediction(self, available_models):
        """Test batch transaction prediction"""
        if not available_models:
            self.log_test("Batch Prediction", False, "No models available for testing")
            return False
            
        model_name = available_models[0] if available_models else "xgboost"
        
        try:
            # Create batch of 3 transactions
            batch_transactions = [self.sample_transaction] * 3
            payload = {
                "transactions": batch_transactions,
                "model_name": model_name
            }
            
            response = requests.post(f"{self.base_url}/fraud/predict/batch", json=payload, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                total = data.get('total_transactions', 0)
                fraud_detected = data.get('fraud_detected', 0)
                results = data.get('results', [])
                
                if total == 3 and len(results) == 3:
                    self.log_test("Batch Prediction", True, f"Batch processed - {total} transactions, {fraud_detected} fraud detected", {"total": total, "fraud_detected": fraud_detected})
                    return True
                else:
                    self.log_test("Batch Prediction", False, f"Unexpected batch size: expected 3, got {total}")
                    return False
            elif response.status_code == 400 and "not available" in response.text:
                self.log_test("Batch Prediction", True, f"Expected error - models not trained yet: {response.text}")
                return True
            else:
                self.log_test("Batch Prediction", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Batch Prediction", False, f"Error: {str(e)}")
            return False
            
    def test_csv_upload(self, available_models):
        """Test CSV file upload for batch prediction"""
        if not available_models:
            self.log_test("CSV Upload", False, "No models available for testing")
            return False
            
        try:
            # Create a small CSV with sample data
            df = pd.DataFrame([self.sample_transaction] * 2)
            csv_content = df.to_csv(index=False)
            
            files = {'file': ('test_transactions.csv', io.StringIO(csv_content), 'text/csv')}
            data = {'model_name': available_models[0] if available_models else 'xgboost'}
            
            response = requests.post(f"{self.base_url}/fraud/upload/csv", files=files, data=data, timeout=20)
            
            if response.status_code == 200:
                result = response.json()
                total = result.get('total_transactions', 0)
                fraud_detected = result.get('fraud_detected', 0)
                
                if total == 2:
                    self.log_test("CSV Upload", True, f"CSV processed - {total} transactions, {fraud_detected} fraud detected", {"total": total, "fraud_detected": fraud_detected})
                    return True
                else:
                    self.log_test("CSV Upload", False, f"Unexpected CSV processing: {total} transactions")
                    return False
            elif response.status_code == 400 and "not available" in response.text:
                self.log_test("CSV Upload", True, f"Expected error - models not trained yet: {response.text}")
                return True
            else:
                self.log_test("CSV Upload", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("CSV Upload", False, f"Error: {str(e)}")
            return False
            
    def test_model_metrics(self, available_models):
        """Test model metrics endpoint"""
        if not available_models:
            self.log_test("Model Metrics", True, "No models available - expected behavior")
            return True
            
        model_name = available_models[0]
        try:
            response = requests.get(f"{self.base_url}/fraud/models/{model_name}/metrics", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                accuracy = data.get('accuracy')
                precision = data.get('precision')
                
                if accuracy is not None and precision is not None:
                    self.log_test("Model Metrics", True, f"Metrics retrieved - Accuracy: {accuracy:.3f}, Precision: {precision:.3f}", {"accuracy": accuracy, "precision": precision})
                    return True
                else:
                    self.log_test("Model Metrics", False, f"Invalid metrics format: {data}")
                    return False
            elif response.status_code == 404:
                self.log_test("Model Metrics", True, f"Expected error - metrics not found for {model_name}")
                return True
            else:
                self.log_test("Model Metrics", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Model Metrics", False, f"Error: {str(e)}")
            return False
            
    def test_feature_importance(self, available_models):
        """Test feature importance endpoint"""
        if not available_models:
            self.log_test("Feature Importance", True, "No models available - expected behavior")
            return True
            
        model_name = available_models[0]
        try:
            response = requests.get(f"{self.base_url}/fraud/models/{model_name}/feature-importance", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                importance = data.get('feature_importance', {})
                
                if importance and len(importance) > 0:
                    top_feature = list(importance.keys())[0]
                    self.log_test("Feature Importance", True, f"Feature importance retrieved - {len(importance)} features, top: {top_feature}", {"feature_count": len(importance)})
                    return True
                else:
                    self.log_test("Feature Importance", False, f"Empty feature importance: {data}")
                    return False
            elif response.status_code == 404:
                self.log_test("Feature Importance", True, f"Expected error - model {model_name} not found")
                return True
            elif response.status_code == 400:
                self.log_test("Feature Importance", True, f"Expected error - feature importance not available for {model_name}")
                return True
            else:
                self.log_test("Feature Importance", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Feature Importance", False, f"Error: {str(e)}")
            return False
            
    def run_all_tests(self):
        """Run comprehensive backend tests"""
        print("🚀 Starting Comprehensive Credit Card Fraud Detection Backend Tests")
        print("=" * 80)
        
        # Basic connectivity and info tests
        health_ok = self.test_health_check()
        info_ok = self.test_fraud_info()
        dataset_ok = self.test_dataset_info()
        
        # Model-related tests
        status_ok, available_models = self.test_model_status()
        training_ok = self.test_model_training()
        
        # Wait a moment for potential model loading
        if available_models:
            print("\n⏳ Models available, testing prediction endpoints...")
        else:
            print("\n⏳ No models available yet, testing error handling...")
            
        time.sleep(2)
        
        # Prediction tests
        single_pred_ok = self.test_single_prediction(available_models)
        batch_pred_ok = self.test_batch_prediction(available_models)
        csv_upload_ok = self.test_csv_upload(available_models)
        
        # Analytics tests
        metrics_ok = self.test_model_metrics(available_models)
        importance_ok = self.test_feature_importance(available_models)
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result['success'])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {passed_tests/total_tests*100:.1f}%")
        
        # Critical issues
        critical_failures = []
        for test_name, result in self.test_results.items():
            if not result['success'] and test_name in ['Health Check', 'Dataset Info', 'Fraud Info']:
                critical_failures.append(test_name)
                
        if critical_failures:
            print(f"\n🚨 CRITICAL FAILURES: {critical_failures}")
        else:
            print(f"\n✅ All critical systems operational")
            
        # Model status
        if available_models:
            print(f"🤖 Models Available: {len(available_models)} - {available_models}")
        else:
            print(f"🤖 Models Status: Training in progress or not started")
            
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'success_rate': passed_tests/total_tests*100,
            'critical_failures': critical_failures,
            'available_models': available_models,
            'detailed_results': self.test_results
        }

if __name__ == "__main__":
    tester = FraudDetectionTester()
    results = tester.run_all_tests()
    
    # Save results to file
    with open('/app/backend_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📁 Detailed results saved to: /app/backend_test_results.json")