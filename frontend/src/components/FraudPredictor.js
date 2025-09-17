import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Textarea } from '@/components/ui/textarea';
import { Shield, AlertTriangle, CheckCircle, Upload, Download, Brain } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const FraudPredictor = () => {
  const [selectedModel, setSelectedModel] = useState('xgboost');
  const [availableModels, setAvailableModels] = useState([]);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [csvFile, setCsvFile] = useState(null);
  const [csvResults, setCsvResults] = useState(null);

  // Single transaction form data
  const [transactionData, setTransactionData] = useState({
    Time: '',
    Amount: '',
    V1: '', V2: '', V3: '', V4: '', V5: '', V6: '', V7: '', V8: '', V9: '', V10: '',
    V11: '', V12: '', V13: '', V14: '', V15: '', V16: '', V17: '', V18: '', V19: '', V20: '',
    V21: '', V22: '', V23: '', V24: '', V25: '', V26: '', V27: '', V28: ''
  });

  useEffect(() => {
    fetchAvailableModels();
  }, []);

  const fetchAvailableModels = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/fraud/models/status`);
      setAvailableModels(response.data.available_models);
      if (response.data.available_models.length > 0 && !response.data.available_models.includes(selectedModel)) {
        setSelectedModel(response.data.available_models[0]);
      }
    } catch (error) {
      console.error('Error fetching models:', error);
    }
  };

  const handleInputChange = (field, value) => {
    setTransactionData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const loadSampleTransaction = () => {
    // Sample transaction data (non-fraud)
    const sampleData = {
      Time: '0',
      Amount: '149.62',
      V1: '-1.359807134', V2: '-0.072781173', V3: '2.536346738', V4: '1.378155224',
      V5: '-0.33832077', V6: '0.462387778', V7: '0.239598554', V8: '0.098697901',
      V9: '0.36378697', V10: '0.090794172', V11: '-0.551599533', V12: '-0.617800856',
      V13: '-0.991389847', V14: '-0.311169354', V15: '1.468176972', V16: '-0.470400525',
      V17: '0.207971242', V18: '0.02579058', V19: '0.40399296', V20: '0.251412098',
      V21: '-0.018306778', V22: '0.277837576', V23: '-0.11047391', V24: '0.066928075',
      V25: '0.128539358', V26: '-0.189114844', V27: '0.133558377', V28: '-0.021053053'
    };
    setTransactionData(sampleData);
  };

  const loadFraudSample = () => {
    // Sample fraud transaction
    const fraudSample = {
      Time: '406',
      Amount: '0.00',
      V1: '2.288644', V2: '1.359805', V3: '-0.072781', V4: '2.536347',
      V5: '1.378155', V6: '-0.338321', V7: '0.462388', V8: '0.239599',
      V9: '0.098698', V10: '0.363787', V11: '0.090794', V12: '-0.551600',
      V13: '-0.617801', V14: '-0.991390', V15: '-0.311169', V16: '1.468177',
      V17: '-0.470401', V18: '0.207971', V19: '0.025791', V20: '0.403993',
      V21: '0.251412', V22: '-0.018307', V23: '0.277838', V24: '-0.110474',
      V25: '0.066928', V26: '0.128539', V27: '-0.189115', V28: '0.133558'
    };
    setTransactionData(fraudSample);
  };

  const predictSingleTransaction = async () => {
    if (availableModels.length === 0) {
      alert('No models available. Please train models first.');
      return;
    }

    try {
      setLoading(true);
      setPrediction(null);

      // Convert all string values to numbers
      const transactionPayload = {};
      Object.keys(transactionData).forEach(key => {
        const value = parseFloat(transactionData[key]);
        if (isNaN(value)) {
          throw new Error(`Invalid value for ${key}: ${transactionData[key]}`);
        }
        transactionPayload[key] = value;
      });

      const response = await axios.post(`${BACKEND_URL}/api/fraud/predict`, {
        transaction: transactionPayload,
        model_name: selectedModel
      });

      setPrediction(response.data);
    } catch (error) {
      console.error('Error making prediction:', error);
      alert('Error making prediction: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleCsvUpload = async () => {
    if (!csvFile) {
      alert('Please select a CSV file');
      return;
    }

    if (availableModels.length === 0) {
      alert('No models available. Please train models first.');
      return;
    }

    try {
      setLoading(true);
      setCsvResults(null);

      const formData = new FormData();
      formData.append('file', csvFile);

      const response = await axios.post(
        `${BACKEND_URL}/api/fraud/upload/csv?model_name=${selectedModel}`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      setCsvResults(response.data);
    } catch (error) {
      console.error('Error uploading CSV:', error);
      alert('Error processing CSV: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const downloadResultsCSV = () => {
    if (!csvResults) return;

    const csvContent = [
      ['Row Index', 'Prediction', 'Probability', 'Risk Level'],
      ...csvResults.results.map(result => [
        result.row_index,
        result.prediction === 1 ? 'Fraud' : 'Normal',
        (result.probability * 100).toFixed(2) + '%',
        result.risk_level
      ])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `fraud_predictions_${new Date().getTime()}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Fraud Prediction</h1>
          <p className="text-gray-600 mt-1">Real-time and batch fraud detection</p>
        </div>
        <div className="flex items-center space-x-4">
          <Label htmlFor="model-select">Model:</Label>
          <Select value={selectedModel} onValueChange={setSelectedModel}>
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

      {availableModels.length === 0 && (
        <Alert>
          <Brain className="h-4 w-4" />
          <AlertDescription>
            No models are currently available. Please train models first from the Dashboard.
          </AlertDescription>
        </Alert>
      )}

      <Tabs defaultValue="single" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="single">Single Transaction</TabsTrigger>
          <TabsTrigger value="batch">Batch Processing</TabsTrigger>
        </TabsList>

        <TabsContent value="single">
          <Card>
            <CardHeader>
              <CardTitle>Single Transaction Prediction</CardTitle>
              <CardDescription>
                Enter transaction details to predict fraud probability
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Sample Data Buttons */}
              <div className="flex space-x-4">
                <Button 
                  variant="outline" 
                  onClick={loadSampleTransaction}
                  className="flex items-center space-x-2"
                >
                  <CheckCircle className="h-4 w-4" />
                  <span>Load Normal Sample</span>
                </Button>
                <Button 
                  variant="outline" 
                  onClick={loadFraudSample}
                  className="flex items-center space-x-2"
                >
                  <AlertTriangle className="h-4 w-4" />
                  <span>Load Fraud Sample</span>
                </Button>
              </div>

              {/* Transaction Inputs */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div>
                  <Label htmlFor="time">Time</Label>
                  <Input
                    id="time"
                    type="number"
                    step="any"
                    value={transactionData.Time}
                    onChange={(e) => handleInputChange('Time', e.target.value)}
                    placeholder="Time since first transaction"
                  />
                </div>
                <div>
                  <Label htmlFor="amount">Amount</Label>
                  <Input
                    id="amount"
                    type="number"
                    step="any"
                    value={transactionData.Amount}
                    onChange={(e) => handleInputChange('Amount', e.target.value)}
                    placeholder="Transaction amount"
                  />
                </div>
                
                {/* PCA Features V1-V28 */}
                {Array.from({ length: 28 }, (_, i) => i + 1).map(num => (
                  <div key={`V${num}`}>
                    <Label htmlFor={`v${num}`}>V{num}</Label>
                    <Input
                      id={`v${num}`}
                      type="number"
                      step="any"
                      value={transactionData[`V${num}`]}
                      onChange={(e) => handleInputChange(`V${num}`, e.target.value)}
                      placeholder={`PCA feature V${num}`}
                    />
                  </div>
                ))}
              </div>

              <Button 
                onClick={predictSingleTransaction} 
                disabled={loading || availableModels.length === 0}
                className="w-full"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Analyzing Transaction...
                  </>
                ) : (
                  <>
                    <Brain className="h-4 w-4 mr-2" />
                    Predict Fraud
                  </>
                )}
              </Button>

              {/* Prediction Results */}
              {prediction && (
                <Card className="mt-6">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      {prediction.prediction === 1 ? (
                        <>
                          <AlertTriangle className="h-5 w-5 text-red-500" />
                          <span className="text-red-600">FRAUD DETECTED</span>
                        </>
                      ) : (
                        <>
                          <Shield className="h-5 w-5 text-green-500" />
                          <span className="text-green-600">NORMAL TRANSACTION</span>
                        </>
                      )}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <Label>Fraud Probability</Label>
                        <div className="text-2xl font-bold">
                          {(prediction.probability * 100).toFixed(2)}%
                        </div>
                      </div>
                      <div>
                        <Label>Risk Level</Label>
                        <div>
                          <Badge 
                            variant={
                              prediction.risk_level === 'HIGH' ? 'destructive' :
                              prediction.risk_level === 'MEDIUM' ? 'secondary' : 'success'
                            }
                          >
                            {prediction.risk_level}
                          </Badge>
                        </div>
                      </div>
                      <div>
                        <Label>Model Used</Label>
                        <div className="font-medium capitalize">
                          {prediction.model_used.replace('_', ' ')}
                        </div>
                      </div>
                    </div>
                    <div className="mt-4">
                      <Label>Transaction ID</Label>
                      <div className="text-sm text-gray-600 font-mono">
                        {prediction.transaction_id}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="batch">
          <Card>
            <CardHeader>
              <CardTitle>Batch Processing</CardTitle>
              <CardDescription>
                Upload a CSV file to analyze multiple transactions at once
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6">
                <div className="text-center">
                  <Upload className="mx-auto h-12 w-12 text-gray-400" />
                  <div className="mt-4">
                    <Label htmlFor="csv-upload" className="cursor-pointer">
                      <span className="text-sm font-medium text-blue-600 hover:text-blue-500">
                        Upload CSV file
                      </span>
                      <Input
                        id="csv-upload"
                        type="file"
                        accept=".csv"
                        onChange={(e) => setCsvFile(e.target.files[0])}
                        className="sr-only"
                      />
                    </Label>
                    <p className="text-sm text-gray-500 mt-1">
                      CSV must contain all required features (Time, V1-V28, Amount)
                    </p>
                  </div>
                </div>
                {csvFile && (
                  <div className="mt-4 text-center">
                    <p className="text-sm text-gray-700">
                      Selected: <span className="font-medium">{csvFile.name}</span>
                    </p>
                  </div>
                )}
              </div>

              <Button 
                onClick={handleCsvUpload} 
                disabled={!csvFile || loading || availableModels.length === 0}
                className="w-full"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Processing CSV...
                  </>
                ) : (
                  <>
                    <Upload className="h-4 w-4 mr-2" />
                    Analyze CSV
                  </>
                )}
              </Button>

              {/* CSV Results */}
              {csvResults && (
                <Card>
                  <CardHeader>
                    <CardTitle>Batch Analysis Results</CardTitle>
                    <div className="flex justify-between items-center">
                      <CardDescription>
                        Analysis complete for {csvResults.filename}
                      </CardDescription>
                      <Button 
                        variant="outline" 
                        onClick={downloadResultsCSV}
                        className="flex items-center space-x-2"
                      >
                        <Download className="h-4 w-4" />
                        <span>Download Results</span>
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-blue-600">
                          {csvResults.total_transactions}
                        </div>
                        <div className="text-sm text-gray-600">Total Transactions</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-red-600">
                          {csvResults.fraud_detected}
                        </div>
                        <div className="text-sm text-gray-600">Fraud Detected</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-purple-600">
                          {csvResults.fraud_percentage}
                        </div>
                        <div className="text-sm text-gray-600">Fraud Rate</div>
                      </div>
                    </div>

                    <div className="max-h-64 overflow-y-auto">
                      <table className="w-full border-collapse border border-gray-300">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="border border-gray-300 px-4 py-2 text-left">Row</th>
                            <th className="border border-gray-300 px-4 py-2 text-left">Prediction</th>
                            <th className="border border-gray-300 px-4 py-2 text-left">Probability</th>
                            <th className="border border-gray-300 px-4 py-2 text-left">Risk Level</th>
                          </tr>
                        </thead>
                        <tbody>
                          {csvResults.results.slice(0, 50).map((result, index) => (
                            <tr key={index}>
                              <td className="border border-gray-300 px-4 py-2">
                                {result.row_index}
                              </td>
                              <td className="border border-gray-300 px-4 py-2">
                                <Badge 
                                  variant={result.prediction === 1 ? "destructive" : "success"}
                                >
                                  {result.prediction === 1 ? 'Fraud' : 'Normal'}
                                </Badge>
                              </td>
                              <td className="border border-gray-300 px-4 py-2">
                                {(result.probability * 100).toFixed(2)}%
                              </td>
                              <td className="border border-gray-300 px-4 py-2">
                                <Badge 
                                  variant={
                                    result.risk_level === 'HIGH' ? 'destructive' :
                                    result.risk_level === 'MEDIUM' ? 'secondary' : 'default'
                                  }
                                >
                                  {result.risk_level}
                                </Badge>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                      {csvResults.results.length > 50 && (
                        <p className="text-sm text-gray-500 mt-2 text-center">
                          Showing first 50 results. Download CSV for complete results.
                        </p>
                      )}
                    </div>
                  </CardContent>
                </Card>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default FraudPredictor;