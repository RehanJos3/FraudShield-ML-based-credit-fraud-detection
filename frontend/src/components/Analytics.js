import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { BarChart, LineChart, Info, TrendingUp, Target } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const Analytics = () => {
  const [availableModels, setAvailableModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState('');
  const [modelMetrics, setModelMetrics] = useState(null);
  const [featureImportance, setFeatureImportance] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchAvailableModels();
  }, []);

  const fetchAvailableModels = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/fraud/models/status`);
      setAvailableModels(response.data.available_models);
      if (response.data.available_models.length > 0) {
        setSelectedModel(response.data.available_models[0]);
        fetchModelData(response.data.available_models[0]);
      }
    } catch (error) {
      console.error('Error fetching models:', error);
    }
  };

  const fetchModelData = async (modelName) => {
    if (!modelName) return;
    
    try {
      setLoading(true);
      const [metricsResponse, importanceResponse] = await Promise.all([
        axios.get(`${BACKEND_URL}/api/fraud/models/${modelName}/metrics`),
        axios.get(`${BACKEND_URL}/api/fraud/models/${modelName}/feature-importance`)
      ]);

      setModelMetrics(metricsResponse.data);
      setFeatureImportance(importanceResponse.data);
    } catch (error) {
      console.error('Error fetching model data:', error);
      setModelMetrics(null);
      setFeatureImportance(null);
    } finally {
      setLoading(false);
    }
  };

  const handleModelChange = (modelName) => {
    setSelectedModel(modelName);
    fetchModelData(modelName);
  };

  const getMetricColor = (metric, value) => {
    const thresholds = {
      accuracy: { good: 0.95, fair: 0.90 },
      precision: { good: 0.80, fair: 0.70 },
      recall: { good: 0.80, fair: 0.70 },
      f1_score: { good: 0.80, fair: 0.70 },
      roc_auc: { good: 0.90, fair: 0.80 }
    };

    const threshold = thresholds[metric];
    if (!threshold) return 'text-gray-600';

    if (value >= threshold.good) return 'text-green-600';
    if (value >= threshold.fair) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getMetricBadgeVariant = (metric, value) => {
    const thresholds = {
      accuracy: { good: 0.95, fair: 0.90 },
      precision: { good: 0.80, fair: 0.70 },
      recall: { good: 0.80, fair: 0.70 },
      f1_score: { good: 0.80, fair: 0.70 },
      roc_auc: { good: 0.90, fair: 0.80 }
    };

    const threshold = thresholds[metric];
    if (!threshold) return 'secondary';

    if (value >= threshold.good) return 'success';
    if (value >= threshold.fair) return 'secondary';
    return 'destructive';
  };

  if (availableModels.length === 0) {
    return (
      <div className="p-6">
        <Alert>
          <Info className="h-4 w-4" />
          <AlertDescription>
            No trained models available. Please train models first from the Dashboard.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Model Analytics</h1>
          <p className="text-gray-600 mt-1">Performance metrics and feature analysis</p>
        </div>
        <div className="flex items-center space-x-4">
          <label htmlFor="model-select" className="text-sm font-medium">Model:</label>
          <Select value={selectedModel} onValueChange={handleModelChange}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="Select a model" />
            </SelectTrigger>
            <SelectContent>
              {availableModels.map(model => (
                <SelectItem key={model} value={model}>
                  {model.replace('_', ' ').toUpperCase()}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {loading && (
        <div className="flex items-center justify-center h-32">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      )}

      {!loading && selectedModel && (
        <Tabs defaultValue="metrics" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="metrics">Performance Metrics</TabsTrigger>
            <TabsTrigger value="confusion">Confusion Matrix</TabsTrigger>
            <TabsTrigger value="features">Feature Importance</TabsTrigger>
          </TabsList>

          <TabsContent value="metrics">
            {modelMetrics && (
              <div className="space-y-6">
                {/* Key Metrics Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                  <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                      <CardTitle className="text-sm font-medium">Accuracy</CardTitle>
                      <Target className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                      <div className={`text-2xl font-bold ${getMetricColor('accuracy', modelMetrics.accuracy)}`}>
                        {(modelMetrics.accuracy * 100).toFixed(2)}%
                      </div>
                      <Badge variant={getMetricBadgeVariant('accuracy', modelMetrics.accuracy)} className="mt-2">
                        {modelMetrics.accuracy >= 0.95 ? 'Excellent' : 
                         modelMetrics.accuracy >= 0.90 ? 'Good' : 'Needs Improvement'}
                      </Badge>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                      <CardTitle className="text-sm font-medium">Precision</CardTitle>
                      <TrendingUp className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                      <div className={`text-2xl font-bold ${getMetricColor('precision', modelMetrics.precision)}`}>
                        {(modelMetrics.precision * 100).toFixed(2)}%
                      </div>
                      <Badge variant={getMetricBadgeVariant('precision', modelMetrics.precision)} className="mt-2">
                        {modelMetrics.precision >= 0.80 ? 'High' : 
                         modelMetrics.precision >= 0.70 ? 'Medium' : 'Low'}
                      </Badge>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                      <CardTitle className="text-sm font-medium">Recall</CardTitle>
                      <BarChart className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                      <div className={`text-2xl font-bold ${getMetricColor('recall', modelMetrics.recall)}`}>
                        {(modelMetrics.recall * 100).toFixed(2)}%
                      </div>
                      <Badge variant={getMetricBadgeVariant('recall', modelMetrics.recall)} className="mt-2">
                        {modelMetrics.recall >= 0.80 ? 'High' : 
                         modelMetrics.recall >= 0.70 ? 'Medium' : 'Low'}
                      </Badge>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                      <CardTitle className="text-sm font-medium">F1 Score</CardTitle>
                      <LineChart className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                      <div className={`text-2xl font-bold ${getMetricColor('f1_score', modelMetrics.f1_score)}`}>
                        {(modelMetrics.f1_score * 100).toFixed(2)}%
                      </div>
                      <Badge variant={getMetricBadgeVariant('f1_score', modelMetrics.f1_score)} className="mt-2">
                        {modelMetrics.f1_score >= 0.80 ? 'Excellent' : 
                         modelMetrics.f1_score >= 0.70 ? 'Good' : 'Fair'}
                      </Badge>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                      <CardTitle className="text-sm font-medium">ROC AUC</CardTitle>
                      <TrendingUp className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                      <div className={`text-2xl font-bold ${getMetricColor('roc_auc', modelMetrics.roc_auc)}`}>
                        {(modelMetrics.roc_auc * 100).toFixed(2)}%
                      </div>
                      <Badge variant={getMetricBadgeVariant('roc_auc', modelMetrics.roc_auc)} className="mt-2">
                        {modelMetrics.roc_auc >= 0.90 ? 'Outstanding' : 
                         modelMetrics.roc_auc >= 0.80 ? 'Good' : 'Acceptable'}
                      </Badge>
                    </CardContent>
                  </Card>
                </div>

                {/* Detailed Classification Report */}
                <Card>
                  <CardHeader>
                    <CardTitle>Detailed Classification Report</CardTitle>
                    <CardDescription>
                      Per-class performance metrics for {selectedModel.replace('_', ' ')}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="overflow-x-auto">
                      <table className="w-full border-collapse border border-gray-300">
                        <thead>
                          <tr className="bg-gray-50">
                            <th className="border border-gray-300 px-4 py-2 text-left">Class</th>
                            <th className="border border-gray-300 px-4 py-2 text-left">Precision</th>
                            <th className="border border-gray-300 px-4 py-2 text-left">Recall</th>
                            <th className="border border-gray-300 px-4 py-2 text-left">F1-Score</th>
                            <th className="border border-gray-300 px-4 py-2 text-left">Support</th>
                          </tr>
                        </thead>
                        <tbody>
                          {Object.entries(modelMetrics.classification_report).map(([className, metrics]) => {
                            if (className === 'accuracy' || className === 'macro avg' || className === 'weighted avg') return null;
                            return (
                              <tr key={className}>
                                <td className="border border-gray-300 px-4 py-2 font-medium">
                                  {className === '0' ? 'Normal' : className === '1' ? 'Fraud' : className}
                                </td>
                                <td className="border border-gray-300 px-4 py-2">
                                  {(metrics.precision * 100).toFixed(2)}%
                                </td>
                                <td className="border border-gray-300 px-4 py-2">
                                  {(metrics.recall * 100).toFixed(2)}%
                                </td>
                                <td className="border border-gray-300 px-4 py-2">
                                  {(metrics['f1-score'] * 100).toFixed(2)}%
                                </td>
                                <td className="border border-gray-300 px-4 py-2">
                                  {metrics.support}
                                </td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    </div>
                  </CardContent>
                </Card>

                {/* Model Interpretation */}
                <Card>
                  <CardHeader>
                    <CardTitle>Model Interpretation</CardTitle>
                    <CardDescription>
                      Understanding the performance characteristics
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <Alert>
                        <Info className="h-4 w-4" />
                        <AlertDescription>
                          <strong>Precision:</strong> Of all transactions predicted as fraud, {(modelMetrics.precision * 100).toFixed(1)}% were actually fraud. 
                          Higher precision means fewer false positives (normal transactions flagged as fraud).
                        </AlertDescription>
                      </Alert>
                      
                      <Alert>
                        <Info className="h-4 w-4" />
                        <AlertDescription>
                          <strong>Recall:</strong> Of all actual fraud cases, {(modelMetrics.recall * 100).toFixed(1)}% were correctly identified. 
                          Higher recall means fewer false negatives (fraud transactions missed).
                        </AlertDescription>
                      </Alert>
                      
                      <Alert>
                        <Info className="h-4 w-4" />
                        <AlertDescription>
                          <strong>F1 Score:</strong> The harmonic mean of precision and recall ({(modelMetrics.f1_score * 100).toFixed(1)}%). 
                          This provides a balanced measure when both false positives and false negatives are important.
                        </AlertDescription>
                      </Alert>
                      
                      <Alert>
                        <Info className="h-4 w-4" />
                        <AlertDescription>
                          <strong>ROC AUC:</strong> Area under the ROC curve ({(modelMetrics.roc_auc * 100).toFixed(1)}%). 
                          This measures the model's ability to distinguish between fraud and normal transactions across all thresholds.
                        </AlertDescription>
                      </Alert>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </TabsContent>

          <TabsContent value="confusion">
            {modelMetrics && (
              <Card>
                <CardHeader>
                  <CardTitle>Confusion Matrix</CardTitle>
                  <CardDescription>
                    Actual vs Predicted classifications for {selectedModel.replace('_', ' ')}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex justify-center">
                    <div className="bg-white rounded-lg shadow-sm border p-6">
                      <div className="text-center mb-4">
                        <h3 className="text-lg font-semibold">Confusion Matrix</h3>
                      </div>
                      <div className="grid grid-cols-3 gap-2 text-center">
                        {/* Header */}
                        <div></div>
                        <div className="font-semibold text-sm">Predicted Normal</div>
                        <div className="font-semibold text-sm">Predicted Fraud</div>
                        
                        {/* True Normal */}
                        <div className="font-semibold text-sm">Actual Normal</div>
                        <div className="bg-green-100 border border-green-300 p-4 rounded">
                          <div className="text-2xl font-bold text-green-800">
                            {modelMetrics.confusion_matrix[0][0]}
                          </div>
                          <div className="text-xs text-green-600">True Negative</div>
                        </div>
                        <div className="bg-red-100 border border-red-300 p-4 rounded">
                          <div className="text-2xl font-bold text-red-800">
                            {modelMetrics.confusion_matrix[0][1]}
                          </div>
                          <div className="text-xs text-red-600">False Positive</div>
                        </div>
                        
                        {/* True Fraud */}
                        <div className="font-semibold text-sm">Actual Fraud</div>
                        <div className="bg-red-100 border border-red-300 p-4 rounded">
                          <div className="text-2xl font-bold text-red-800">
                            {modelMetrics.confusion_matrix[1][0]}
                          </div>
                          <div className="text-xs text-red-600">False Negative</div>
                        </div>
                        <div className="bg-green-100 border border-green-300 p-4 rounded">
                          <div className="text-2xl font-bold text-green-800">
                            {modelMetrics.confusion_matrix[1][1]}
                          </div>
                          <div className="text-xs text-green-600">True Positive</div>
                        </div>
                      </div>
                      
                      <div className="mt-6 text-sm text-gray-600 space-y-2">
                        <div><strong>True Positive:</strong> Correctly identified fraud cases</div>
                        <div><strong>True Negative:</strong> Correctly identified normal transactions</div>
                        <div><strong>False Positive:</strong> Normal transactions incorrectly flagged as fraud</div>
                        <div><strong>False Negative:</strong> Fraud cases that were missed</div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="features">
            {featureImportance && (
              <Card>
                <CardHeader>
                  <CardTitle>Feature Importance</CardTitle>
                  <CardDescription>
                    Most influential features for {selectedModel.replace('_', ' ')} predictions
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {Object.entries(featureImportance.feature_importance).slice(0, 15).map(([feature, importance], index) => (
                      <div key={feature} className="flex items-center space-x-4">
                        <div className="w-8 text-sm text-gray-500 text-right">
                          #{index + 1}
                        </div>
                        <div className="w-20 text-sm font-medium">
                          {feature}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center space-x-2">
                            <div className="flex-1 bg-gray-200 rounded-full h-2">
                              <div 
                                className="bg-blue-600 h-2 rounded-full" 
                                style={{
                                  width: `${(importance / Math.max(...Object.values(featureImportance.feature_importance))) * 100}%`
                                }}
                              ></div>
                            </div>
                            <div className="text-sm text-gray-600 w-16 text-right">
                              {(importance * 100).toFixed(2)}%
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                  
                  <Alert className="mt-6">
                    <Info className="h-4 w-4" />
                    <AlertDescription>
                      Feature importance shows which variables have the most influence on fraud predictions. 
                      Higher values indicate features that are more critical for the model's decision-making process.
                      {selectedModel === 'logistic_regression' && ' (Based on coefficient magnitudes)'}
                      {(selectedModel === 'random_forest' || selectedModel === 'xgboost') && ' (Based on information gain)'}
                    </AlertDescription>
                  </Alert>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      )}
    </div>
  );
};

export default Analytics;