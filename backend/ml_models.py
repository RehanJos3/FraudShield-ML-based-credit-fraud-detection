"""
Machine Learning models for fraud detection.
Implements multiple models: Logistic Regression, Random Forest, XGBoost, Neural Network
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
import xgboost as xgb
import tensorflow as tf
from tensorflow import keras
import joblib
import os
import json
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder

class FraudDetectionModel:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.metrics = {}
        self.feature_names = None
        self.model_path = "/app/data/models"
        self.ensure_model_directory()
        
    def ensure_model_directory(self):
        """Create model directory if it doesn't exist"""
        os.makedirs(self.model_path, exist_ok=True)
        
    def load_and_preprocess_data(self, file_path="/app/data/creditcard.csv"):
        """Load and preprocess the credit card fraud dataset"""
        print("Loading dataset...")
        df = pd.read_csv(file_path)
        
        # Basic data info
        print(f"Dataset shape: {df.shape}")
        print(f"Fraud cases: {df['Class'].sum()} ({df['Class'].sum()/len(df)*100:.2f}%)")
        print(f"Normal cases: {(df['Class'] == 0).sum()} ({(df['Class'] == 0).sum()/len(df)*100:.2f}%)")
        
        # Separate features and target
        X = df.drop('Class', axis=1)
        y = df['Class']
        
        self.feature_names = X.columns.tolist()
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        return X_train, X_test, y_train, y_test, df
        
    def handle_class_imbalance(self, X_train, y_train, method='smote'):
        """Handle class imbalance using SMOTE or undersampling"""
        if method == 'smote':
            print("Applying SMOTE for class imbalance...")
            smote = SMOTE(random_state=42)
            X_resampled, y_resampled = smote.fit_resample(X_train, y_train)
        elif method == 'undersample':
            print("Applying Random Undersampling...")
            rus = RandomUnderSampler(random_state=42)
            X_resampled, y_resampled = rus.fit_resample(X_train, y_train)
        else:
            X_resampled, y_resampled = X_train, y_train
            
        print(f"Resampled data shape: {X_resampled.shape}")
        print(f"Fraud cases after resampling: {y_resampled.sum()}")
        
        return X_resampled, y_resampled
        
    def train_logistic_regression(self, X_train, y_train, X_test, y_test):
        """Train Logistic Regression model"""
        print("Training Logistic Regression...")
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        lr_model = LogisticRegression(random_state=42, max_iter=1000)
        lr_model.fit(X_train_scaled, y_train)
        
        # Store model and scaler
        self.models['logistic_regression'] = lr_model
        self.scalers['logistic_regression'] = scaler
        
        # Evaluate
        y_pred = lr_model.predict(X_test_scaled)
        y_prob = lr_model.predict_proba(X_test_scaled)[:, 1]
        
        metrics = self.calculate_metrics(y_test, y_pred, y_prob, "Logistic Regression")
        self.metrics['logistic_regression'] = metrics
        
        return lr_model, scaler, metrics
        
    def train_random_forest(self, X_train, y_train, X_test, y_test):
        """Train Random Forest model"""
        print("Training Random Forest...")
        
        # Train model
        rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        rf_model.fit(X_train, y_train)
        
        # Store model
        self.models['random_forest'] = rf_model
        
        # Evaluate
        y_pred = rf_model.predict(X_test)
        y_prob = rf_model.predict_proba(X_test)[:, 1]
        
        metrics = self.calculate_metrics(y_test, y_pred, y_prob, "Random Forest")
        self.metrics['random_forest'] = metrics
        
        return rf_model, metrics
        
    def train_xgboost(self, X_train, y_train, X_test, y_test):
        """Train XGBoost model"""
        print("Training XGBoost...")
        
        # Train model
        xgb_model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            eval_metric='logloss'
        )
        xgb_model.fit(X_train, y_train)
        
        # Store model
        self.models['xgboost'] = xgb_model
        
        # Evaluate
        y_pred = xgb_model.predict(X_test)
        y_prob = xgb_model.predict_proba(X_test)[:, 1]
        
        metrics = self.calculate_metrics(y_test, y_pred, y_prob, "XGBoost")
        self.metrics['xgboost'] = metrics
        
        return xgb_model, metrics
        
    def train_neural_network(self, X_train, y_train, X_test, y_test):
        """Train Neural Network model"""
        print("Training Neural Network...")
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Build model
        model = keras.Sequential([
            keras.layers.Dense(64, activation='relu', input_shape=(X_train_scaled.shape[1],)),
            keras.layers.Dropout(0.3),
            keras.layers.Dense(32, activation='relu'),
            keras.layers.Dropout(0.3),
            keras.layers.Dense(16, activation='relu'),
            keras.layers.Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        # Train model
        history = model.fit(
            X_train_scaled, y_train,
            epochs=50,
            batch_size=32,
            validation_split=0.2,
            verbose=0
        )
        
        # Store model and scaler
        self.models['neural_network'] = model
        self.scalers['neural_network'] = scaler
        
        # Evaluate
        y_prob = model.predict(X_test_scaled).flatten()
        y_pred = (y_prob > 0.5).astype(int)
        
        metrics = self.calculate_metrics(y_test, y_pred, y_prob, "Neural Network")
        self.metrics['neural_network'] = metrics
        
        return model, scaler, metrics
        
    def calculate_metrics(self, y_true, y_pred, y_prob, model_name):
        """Calculate comprehensive metrics for model evaluation"""
        from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
        
        metrics = {
            'model_name': model_name,
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred),
            'recall': recall_score(y_true, y_pred),
            'f1_score': f1_score(y_true, y_pred),
            'roc_auc': roc_auc_score(y_true, y_prob),
            'confusion_matrix': confusion_matrix(y_true, y_pred).tolist(),
            'classification_report': classification_report(y_true, y_pred, output_dict=True)
        }
        
        print(f"\n{model_name} Metrics:")
        print(f"Accuracy: {metrics['accuracy']:.4f}")
        print(f"Precision: {metrics['precision']:.4f}")
        print(f"Recall: {metrics['recall']:.4f}")
        print(f"F1 Score: {metrics['f1_score']:.4f}")
        print(f"ROC AUC: {metrics['roc_auc']:.4f}")
        
        return metrics
        
    def get_feature_importance(self, model_name):
        """Get feature importance for tree-based models"""
        if model_name not in self.models:
            return None
            
        model = self.models[model_name]
        
        if hasattr(model, 'feature_importances_'):
            importance = model.feature_importances_
            feature_importance = dict(zip(self.feature_names, importance))
            # Sort by importance
            feature_importance = dict(sorted(feature_importance.items(), key=lambda x: x[1], reverse=True))
            return feature_importance
        elif hasattr(model, 'coef_'):
            # For logistic regression
            importance = np.abs(model.coef_[0])
            feature_importance = dict(zip(self.feature_names, importance))
            feature_importance = dict(sorted(feature_importance.items(), key=lambda x: x[1], reverse=True))
            return feature_importance
        
        return None
        
    def create_roc_curve_plot(self, X_test, y_test):
        """Create ROC curve plot for all models"""
        fig = go.Figure()
        
        for model_name, model in self.models.items():
            if model_name in ['logistic_regression', 'neural_network']:
                # Use scaled data
                scaler = self.scalers[model_name]
                X_test_scaled = scaler.transform(X_test)
                if model_name == 'neural_network':
                    y_prob = model.predict(X_test_scaled).flatten()
                else:
                    y_prob = model.predict_proba(X_test_scaled)[:, 1]
            else:
                y_prob = model.predict_proba(X_test)[:, 1]
                
            fpr, tpr, _ = roc_curve(y_test, y_prob)
            auc_score = roc_auc_score(y_test, y_prob)
            
            fig.add_trace(go.Scatter(
                x=fpr, y=tpr,
                mode='lines',
                name=f'{model_name} (AUC = {auc_score:.3f})',
                line=dict(width=2)
            ))
        
        # Add diagonal line
        fig.add_trace(go.Scatter(
            x=[0, 1], y=[0, 1],
            mode='lines',
            name='Random Classifier',
            line=dict(dash='dash', color='gray')
        ))
        
        fig.update_layout(
            title='ROC Curves Comparison',
            xaxis_title='False Positive Rate',
            yaxis_title='True Positive Rate',
            width=800,
            height=600
        )
        
        return json.dumps(fig, cls=PlotlyJSONEncoder)
        
    def create_feature_importance_plot(self, model_name, top_n=15):
        """Create feature importance plot"""
        importance = self.get_feature_importance(model_name)
        if not importance:
            return None
            
        # Get top N features
        top_features = list(importance.items())[:top_n]
        features, values = zip(*top_features)
        
        fig = go.Figure(data=[
            go.Bar(
                x=list(values),
                y=list(features),
                orientation='h',
                marker_color='steelblue'
            )
        ])
        
        fig.update_layout(
            title=f'Feature Importance - {model_name}',
            xaxis_title='Importance',
            yaxis_title='Features',
            height=600,
            yaxis={'categoryorder': 'total ascending'}
        )
        
        return json.dumps(fig, cls=PlotlyJSONEncoder)
        
    def predict_single_transaction(self, transaction_data, model_name='xgboost'):
        """Predict fraud for a single transaction"""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found")
            
        model = self.models[model_name]
        
        # Convert to DataFrame if it's a dict
        if isinstance(transaction_data, dict):
            transaction_df = pd.DataFrame([transaction_data])
        else:
            transaction_df = pd.DataFrame(transaction_data)
            
        # Scale if needed
        if model_name in self.scalers:
            scaler = self.scalers[model_name]
            transaction_scaled = scaler.transform(transaction_df)
            if model_name == 'neural_network':
                probability = model.predict(transaction_scaled)[0][0]
            else:
                probability = model.predict_proba(transaction_scaled)[0][1]
        else:
            probability = model.predict_proba(transaction_df)[0][1]
            
        prediction = 1 if probability > 0.5 else 0
        
        return {
            'prediction': prediction,
            'probability': float(probability),
            'risk_level': 'HIGH' if probability > 0.7 else 'MEDIUM' if probability > 0.3 else 'LOW'
        }
        
    def save_models(self):
        """Save all trained models"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for model_name, model in self.models.items():
            if model_name == 'neural_network':
                model.save(f"{self.model_path}/{model_name}_{timestamp}.h5")
            else:
                joblib.dump(model, f"{self.model_path}/{model_name}_{timestamp}.pkl")
                
        # Save scalers
        for scaler_name, scaler in self.scalers.items():
            joblib.dump(scaler, f"{self.model_path}/{scaler_name}_scaler_{timestamp}.pkl")
            
        # Save metrics
        with open(f"{self.model_path}/metrics_{timestamp}.json", 'w') as f:
            json.dump(self.metrics, f, indent=2)
            
        print(f"Models saved with timestamp: {timestamp}")
        return timestamp
        
    def load_models(self, timestamp):
        """Load saved models"""
        model_files = {
            'logistic_regression': f"{self.model_path}/logistic_regression_{timestamp}.pkl",
            'random_forest': f"{self.model_path}/random_forest_{timestamp}.pkl",
            'xgboost': f"{self.model_path}/xgboost_{timestamp}.pkl",
            'neural_network': f"{self.model_path}/neural_network_{timestamp}.h5"
        }
        
        for model_name, file_path in model_files.items():
            if os.path.exists(file_path):
                if model_name == 'neural_network':
                    self.models[model_name] = keras.models.load_model(file_path)
                else:
                    self.models[model_name] = joblib.load(file_path)
                    
        # Load scalers
        scaler_files = {
            'logistic_regression': f"{self.model_path}/logistic_regression_scaler_{timestamp}.pkl",
            'neural_network': f"{self.model_path}/neural_network_scaler_{timestamp}.pkl"
        }
        
        for scaler_name, file_path in scaler_files.items():
            if os.path.exists(file_path):
                self.scalers[scaler_name] = joblib.load(file_path)
                
        # Load metrics
        metrics_file = f"{self.model_path}/metrics_{timestamp}.json"
        if os.path.exists(metrics_file):
            with open(metrics_file, 'r') as f:
                self.metrics = json.load(f)
                
        print(f"Models loaded from timestamp: {timestamp}")
        
    def train_all_models(self, balance_method='smote'):
        """Train all models with the complete pipeline"""
        print("Starting comprehensive fraud detection model training...")
        
        # Load and preprocess data
        X_train, X_test, y_train, y_test, df = self.load_and_preprocess_data()
        
        # Handle class imbalance
        X_train_balanced, y_train_balanced = self.handle_class_imbalance(
            X_train, y_train, method=balance_method
        )
        
        # Train all models
        print("\n" + "="*50)
        self.train_logistic_regression(X_train_balanced, y_train_balanced, X_test, y_test)
        
        print("\n" + "="*50)
        self.train_random_forest(X_train_balanced, y_train_balanced, X_test, y_test)
        
        print("\n" + "="*50)
        self.train_xgboost(X_train_balanced, y_train_balanced, X_test, y_test)
        
        print("\n" + "="*50)
        self.train_neural_network(X_train_balanced, y_train_balanced, X_test, y_test)
        
        # Save models
        timestamp = self.save_models()
        
        print(f"\n{'='*50}")
        print("Training completed successfully!")
        print(f"Models saved with timestamp: {timestamp}")
        
        # Return test data for visualization
        return X_test, y_test, df