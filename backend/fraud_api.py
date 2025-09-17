"""
FastAPI endpoints for fraud detection system
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import pandas as pd
import json
import io
import os
from datetime import datetime
import uuid
from .ml_models import FraudDetectionModel

# Initialize router
fraud_router = APIRouter(prefix="/fraud", tags=["fraud-detection"])

# Global model instance
ml_model = FraudDetectionModel()

# Pydantic models
class TransactionData(BaseModel):
    Time: float = Field(..., description="Time elapsed since first transaction")
    V1: float = Field(..., description="PCA feature V1")
    V2: float = Field(..., description="PCA feature V2")
    V3: float = Field(..., description="PCA feature V3")
    V4: float = Field(..., description="PCA feature V4")
    V5: float = Field(..., description="PCA feature V5")
    V6: float = Field(..., description="PCA feature V6")
    V7: float = Field(..., description="PCA feature V7")
    V8: float = Field(..., description="PCA feature V8")
    V9: float = Field(..., description="PCA feature V9")
    V10: float = Field(..., description="PCA feature V10")
    V11: float = Field(..., description="PCA feature V11")
    V12: float = Field(..., description="PCA feature V12")
    V13: float = Field(..., description="PCA feature V13")
    V14: float = Field(..., description="PCA feature V14")
    V15: float = Field(..., description="PCA feature V15")
    V16: float = Field(..., description="PCA feature V16")
    V17: float = Field(..., description="PCA feature V17")
    V18: float = Field(..., description="PCA feature V18")
    V19: float = Field(..., description="PCA feature V19")
    V20: float = Field(..., description="PCA feature V20")
    V21: float = Field(..., description="PCA feature V21")
    V22: float = Field(..., description="PCA feature V22")
    V23: float = Field(..., description="PCA feature V23")
    V24: float = Field(..., description="PCA feature V24")
    V25: float = Field(..., description="PCA feature V25")
    V26: float = Field(..., description="PCA feature V26")
    V27: float = Field(..., description="PCA feature V27")
    V28: float = Field(..., description="PCA feature V28")
    Amount: float = Field(..., description="Transaction amount")

class FraudPredictionRequest(BaseModel):
    transaction: TransactionData
    model_name: Optional[str] = Field(default="xgboost", description="Model to use for prediction")

class FraudPredictionResponse(BaseModel):
    transaction_id: str
    prediction: int
    probability: float
    risk_level: str
    model_used: str
    timestamp: str

class BatchPredictionRequest(BaseModel):
    transactions: List[TransactionData]
    model_name: Optional[str] = Field(default="xgboost", description="Model to use for prediction")

class ModelTrainingRequest(BaseModel):
    balance_method: Optional[str] = Field(default="smote", description="Method for handling class imbalance")
    retrain: Optional[bool] = Field(default=False, description="Whether to retrain existing models")

class ModelMetrics(BaseModel):
    model_name: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    confusion_matrix: List[List[int]]

# API Endpoints

@fraud_router.get("/")
async def get_fraud_detection_info():
    """Get information about the fraud detection system"""
    return {
        "message": "Credit Card Fraud Detection API",
        "version": "1.0.0",
        "available_models": ["logistic_regression", "random_forest", "xgboost", "neural_network"],
        "features": [
            "Real-time fraud prediction",
            "Batch processing",
            "Model training and retraining",
            "Performance metrics and visualization",
            "Feature importance analysis"
        ]
    }

@fraud_router.post("/predict", response_model=FraudPredictionResponse)
async def predict_fraud(request: FraudPredictionRequest):
    """Predict fraud for a single transaction"""
    try:
        if request.model_name not in ml_model.models:
            raise HTTPException(
                status_code=400, 
                detail=f"Model {request.model_name} not available. Please train models first."
            )
        
        # Convert transaction to dict
        transaction_dict = request.transaction.dict()
        
        # Make prediction
        result = ml_model.predict_single_transaction(
            transaction_dict, 
            model_name=request.model_name
        )
        
        return FraudPredictionResponse(
            transaction_id=str(uuid.uuid4()),
            prediction=result['prediction'],
            probability=result['probability'],
            risk_level=result['risk_level'],
            model_used=request.model_name,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@fraud_router.post("/predict/batch")
async def predict_fraud_batch(request: BatchPredictionRequest):
    """Predict fraud for multiple transactions"""
    try:
        if request.model_name not in ml_model.models:
            raise HTTPException(
                status_code=400, 
                detail=f"Model {request.model_name} not available. Please train models first."
            )
        
        results = []
        for transaction in request.transactions:
            transaction_dict = transaction.dict()
            result = ml_model.predict_single_transaction(
                transaction_dict, 
                model_name=request.model_name
            )
            
            results.append({
                "transaction_id": str(uuid.uuid4()),
                "prediction": result['prediction'],
                "probability": result['probability'],
                "risk_level": result['risk_level'],
                "timestamp": datetime.now().isoformat()
            })
        
        return {
            "model_used": request.model_name,
            "total_transactions": len(results),
            "fraud_detected": sum(1 for r in results if r['prediction'] == 1),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@fraud_router.post("/upload/csv")
async def upload_csv_for_prediction(file: UploadFile = File(...), model_name: str = "xgboost"):
    """Upload CSV file for batch fraud prediction"""
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV")
        
        if model_name not in ml_model.models:
            raise HTTPException(
                status_code=400, 
                detail=f"Model {model_name} not available. Please train models first."
            )
        
        # Read CSV file
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Validate columns
        expected_columns = [f'V{i}' for i in range(1, 29)] + ['Time', 'Amount']
        missing_columns = set(expected_columns) - set(df.columns)
        if missing_columns:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing columns: {list(missing_columns)}"
            )
        
        # Make predictions
        results = []
        for _, row in df.iterrows():
            transaction_dict = row[expected_columns].to_dict()
            result = ml_model.predict_single_transaction(
                transaction_dict, 
                model_name=model_name
            )
            
            results.append({
                "row_index": int(row.name),
                "prediction": result['prediction'],
                "probability": result['probability'],
                "risk_level": result['risk_level']
            })
        
        return {
            "filename": file.filename,
            "model_used": model_name,
            "total_transactions": len(results),
            "fraud_detected": sum(1 for r in results if r['prediction'] == 1),
            "fraud_percentage": f"{sum(1 for r in results if r['prediction'] == 1) / len(results) * 100:.2f}%",
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@fraud_router.post("/train")
async def train_models(background_tasks: BackgroundTasks, request: ModelTrainingRequest):
    """Train or retrain fraud detection models"""
    try:
        if not request.retrain and ml_model.models:
            return {
                "message": "Models already exist. Set retrain=true to retrain.",
                "existing_models": list(ml_model.models.keys())
            }
        
        # Add training task to background
        background_tasks.add_task(
            train_models_background, 
            request.balance_method
        )
        
        return {
            "message": "Model training started in background",
            "balance_method": request.balance_method,
            "estimated_time": "5-10 minutes"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def train_models_background(balance_method: str):
    """Background task for model training"""
    try:
        X_test, y_test, df = ml_model.train_all_models(balance_method=balance_method)
        print("Background model training completed successfully!")
    except Exception as e:
        print(f"Background model training failed: {e}")

@fraud_router.get("/models/status")
async def get_models_status():
    """Get status of trained models"""
    return {
        "available_models": list(ml_model.models.keys()),
        "model_metrics": ml_model.metrics if ml_model.metrics else "No metrics available",
        "total_models": len(ml_model.models)
    }

@fraud_router.get("/models/{model_name}/metrics", response_model=ModelMetrics)
async def get_model_metrics(model_name: str):
    """Get detailed metrics for a specific model"""
    if model_name not in ml_model.metrics:
        raise HTTPException(
            status_code=404, 
            detail=f"Metrics for model {model_name} not found"
        )
    
    metrics = ml_model.metrics[model_name]
    return ModelMetrics(**metrics)

@fraud_router.get("/models/{model_name}/feature-importance")
async def get_feature_importance(model_name: str):
    """Get feature importance for a specific model"""
    if model_name not in ml_model.models:
        raise HTTPException(
            status_code=404, 
            detail=f"Model {model_name} not found"
        )
    
    importance = ml_model.get_feature_importance(model_name)
    if importance is None:
        raise HTTPException(
            status_code=400, 
            detail=f"Feature importance not available for {model_name}"
        )
    
    return {
        "model_name": model_name,
        "feature_importance": importance
    }

@fraud_router.get("/visualizations/roc-curve")
async def get_roc_curve():
    """Get ROC curve data for all models"""
    try:
        if not ml_model.models:
            raise HTTPException(
                status_code=400, 
                detail="No trained models available"
            )
        
        # We need test data for ROC curve - this would be stored during training
        # For now, return a placeholder
        return {
            "message": "ROC curve data",
            "note": "ROC curve visualization requires test data from training session"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@fraud_router.get("/visualizations/feature-importance/{model_name}")
async def get_feature_importance_plot(model_name: str, top_n: int = 15):
    """Get feature importance plot data"""
    try:
        if model_name not in ml_model.models:
            raise HTTPException(
                status_code=404, 
                detail=f"Model {model_name} not found"
            )
        
        plot_data = ml_model.create_feature_importance_plot(model_name, top_n)
        if plot_data is None:
            raise HTTPException(
                status_code=400, 
                detail=f"Feature importance plot not available for {model_name}"
            )
        
        return {
            "model_name": model_name,
            "plot_data": json.loads(plot_data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@fraud_router.get("/dataset/info")
async def get_dataset_info():
    """Get information about the fraud dataset"""
    try:
        if os.path.exists("/app/data/creditcard.csv"):
            df = pd.read_csv("/app/data/creditcard.csv")
            
            return {
                "total_transactions": len(df),
                "fraud_cases": int(df['Class'].sum()),
                "normal_cases": int((df['Class'] == 0).sum()),
                "fraud_percentage": f"{df['Class'].sum() / len(df) * 100:.2f}%",
                "features": df.columns.tolist(),
                "dataset_size_mb": f"{os.path.getsize('/app/data/creditcard.csv') / (1024*1024):.2f} MB"
            }
        else:
            raise HTTPException(status_code=404, detail="Dataset not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@fraud_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "models_loaded": len(ml_model.models),
        "dataset_available": os.path.exists("/app/data/creditcard.csv")
    }