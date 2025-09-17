import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import { Activity, TrendingUp, Shield, Database, Brain, AlertTriangle } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const Dashboard = () => {
  const [datasetInfo, setDatasetInfo] = useState(null);
  const [modelsStatus, setModelsStatus] = useState(null);
  const [isTraining, setIsTraining] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [datasetResponse, modelsResponse] = await Promise.all([
        axios.get(`${BACKEND_URL}/api/fraud/dataset/info`),
        axios.get(`${BACKEND_URL}/api/fraud/models/status`)
      ]);

      setDatasetInfo(datasetResponse.data);
      setModelsStatus(modelsResponse.data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const startModelTraining = async () => {
    try {
      setIsTraining(true);
      await axios.post(`${BACKEND_URL}/api/fraud/train`, {
        balance_method: 'smote',
        retrain: true
      });
      
      // Refresh models status after training starts
      setTimeout(() => {
        fetchDashboardData();
        setIsTraining(false);
      }, 2000);
    } catch (error) {
      console.error('Error starting model training:', error);
      setIsTraining(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Fraud Detection Dashboard</h1>
          <p className="text-gray-600 mt-1">Production-ready credit card fraud detection system</p>
        </div>
        <div className="flex space-x-3">
          <Button
            onClick={startModelTraining}
            disabled={isTraining}
            className="bg-blue-600 hover:bg-blue-700"
          >
            {isTraining ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Training Models...
              </>
            ) : (
              <>
                <Brain className="h-4 w-4 mr-2" />
                Train Models
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Dataset Overview */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Transactions</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {datasetInfo ? datasetInfo.total_transactions.toLocaleString() : 'Loading...'}
            </div>
            <p className="text-xs text-muted-foreground">
              Dataset size: {datasetInfo ? datasetInfo.dataset_size_mb : 'Loading...'}
            </p>
          </CardContent>
        </Card>

        {/* Fraud Cases */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Fraud Cases</CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {datasetInfo ? datasetInfo.fraud_cases.toLocaleString() : 'Loading...'}
            </div>
            <p className="text-xs text-muted-foreground">
              {datasetInfo ? datasetInfo.fraud_percentage : 'Loading...'} of total transactions
            </p>
          </CardContent>
        </Card>

        {/* Normal Cases */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Normal Cases</CardTitle>
            <Shield className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {datasetInfo ? datasetInfo.normal_cases.toLocaleString() : 'Loading...'}
            </div>
            <p className="text-xs text-muted-foreground">
              Legitimate transactions
            </p>
          </CardContent>
        </Card>

        {/* Models Trained */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Models Available</CardTitle>
            <Activity className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {modelsStatus ? modelsStatus.total_models : 0}
            </div>
            <p className="text-xs text-muted-foreground">
              ML models ready for prediction
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Class Imbalance Visualization */}
      {datasetInfo && (
        <Card>
          <CardHeader>
            <CardTitle>Dataset Class Distribution</CardTitle>
            <CardDescription>
              Visualization of fraud vs normal transaction distribution
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 bg-green-500 rounded"></div>
                  <span className="text-sm">Normal Transactions</span>
                </div>
                <span className="text-sm font-medium">
                  {((datasetInfo.normal_cases / datasetInfo.total_transactions) * 100).toFixed(2)}%
                </span>
              </div>
              <Progress 
                value={(datasetInfo.normal_cases / datasetInfo.total_transactions) * 100} 
                className="w-full h-2 bg-gray-200"
              />
              
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 bg-red-500 rounded"></div>
                  <span className="text-sm">Fraud Transactions</span>
                </div>
                <span className="text-sm font-medium">
                  {((datasetInfo.fraud_cases / datasetInfo.total_transactions) * 100).toFixed(2)}%
                </span>
              </div>
              <Progress 
                value={(datasetInfo.fraud_cases / datasetInfo.total_transactions) * 100} 
                className="w-full h-2 bg-gray-200"
              />
            </div>
            <Alert className="mt-4">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                This dataset shows extreme class imbalance (0.17% fraud), which is typical for fraud detection scenarios. 
                Our ML models use SMOTE (Synthetic Minority Oversampling Technique) to handle this imbalance.
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      )}

      {/* Models Status */}
      <Card>
        <CardHeader>
          <CardTitle>Machine Learning Models</CardTitle>
          <CardDescription>
            Status and performance of available fraud detection models
          </CardDescription>
        </CardHeader>
        <CardContent>
          {modelsStatus && modelsStatus.available_models.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {modelsStatus.available_models.map((model) => (
                <div key={model} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium capitalize">
                      {model.replace('_', ' ')}
                    </span>
                    <Badge variant="success">Ready</Badge>
                  </div>
                  <p className="text-sm text-gray-600">
                    {getModelDescription(model)}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Brain className="h-12 w-12 mx-auto text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Models Trained</h3>
              <p className="text-gray-600 mb-4">
                Train machine learning models to start detecting fraud
              </p>
              <Button onClick={startModelTraining} disabled={isTraining}>
                {isTraining ? 'Training...' : 'Train Models Now'}
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Model Performance */}
      {modelsStatus && modelsStatus.model_metrics && modelsStatus.model_metrics !== "No metrics available" && (
        <Card>
          <CardHeader>
            <CardTitle>Model Performance Metrics</CardTitle>
            <CardDescription>
              Comprehensive evaluation metrics for trained models
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full border-collapse border border-gray-300">
                <thead>
                  <tr className="bg-gray-50">
                    <th className="border border-gray-300 px-4 py-2 text-left">Model</th>
                    <th className="border border-gray-300 px-4 py-2 text-left">Accuracy</th>
                    <th className="border border-gray-300 px-4 py-2 text-left">Precision</th>
                    <th className="border border-gray-300 px-4 py-2 text-left">Recall</th>
                    <th className="border border-gray-300 px-4 py-2 text-left">F1 Score</th>
                    <th className="border border-gray-300 px-4 py-2 text-left">ROC AUC</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(modelsStatus.model_metrics).map(([modelName, metrics]) => (
                    <tr key={modelName}>
                      <td className="border border-gray-300 px-4 py-2 font-medium capitalize">
                        {modelName.replace('_', ' ')}
                      </td>
                      <td className="border border-gray-300 px-4 py-2">
                        {(metrics.accuracy * 100).toFixed(2)}%
                      </td>
                      <td className="border border-gray-300 px-4 py-2">
                        {(metrics.precision * 100).toFixed(2)}%
                      </td>
                      <td className="border border-gray-300 px-4 py-2">
                        {(metrics.recall * 100).toFixed(2)}%
                      </td>
                      <td className="border border-gray-300 px-4 py-2">
                        {(metrics.f1_score * 100).toFixed(2)}%
                      </td>
                      <td className="border border-gray-300 px-4 py-2">
                        {(metrics.roc_auc * 100).toFixed(2)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

const getModelDescription = (model) => {
  const descriptions = {
    'logistic_regression': 'Linear model for binary classification with statistical insights',
    'random_forest': 'Ensemble method combining multiple decision trees',
    'xgboost': 'Gradient boosting framework optimized for performance',
    'neural_network': 'Deep learning model with multiple hidden layers'
  };
  return descriptions[model] || 'Advanced machine learning model';
};

export default Dashboard;