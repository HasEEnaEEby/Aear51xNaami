import pandas as pd
import numpy as np
import pickle
import os
from typing import Dict, List, Tuple, Any, Optional
import joblib
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
import shap
import warnings
warnings.filterwarnings('ignore')

class RiskScoringModel:
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the Risk Scoring Model.
        
        Args:
            model_path: Path to a saved model. If None, a new model will be created.
        """
        self.model = None
        self.feature_names = None
        self.text_vectorizer = None
        self.numerical_scaler = None
        self.explainer = None
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
    
    def preprocess_data(self, data: pd.DataFrame) -> Tuple[np.ndarray, List[str]]:
        """
        Preprocess data for model training or prediction.
        
        Args:
            data: DataFrame containing questionnaire responses and metadata
            
        Returns:
            Tuple of preprocessed features and feature names
        """
        # Extract text features
        text_columns = [col for col in data.columns if data[col].dtype == 'object']
        text_data = data[text_columns].fillna('')
        
        # Extract numerical features
        numerical_columns = [col for col in data.columns if data[col].dtype != 'object']
        numerical_data = data[numerical_columns].fillna(0)
        
        # Process text features
        if self.text_vectorizer is None:
            self.text_vectorizer = TfidfVectorizer(max_features=100)
            text_features = self.text_vectorizer.fit_transform(
                text_data.apply(lambda x: ' '.join(x), axis=1)
            )
        else:
            text_features = self.text_vectorizer.transform(
                text_data.apply(lambda x: ' '.join(x), axis=1)
            )
        
        # Process numerical features
        if self.numerical_scaler is None:
            self.numerical_scaler = StandardScaler()
            numerical_features = self.numerical_scaler.fit_transform(numerical_data)
        else:
            numerical_features = self.numerical_scaler.transform(numerical_data)
        
        # Combine features
        combined_features = np.hstack((text_features.toarray(), numerical_features))
        
        # Create feature names
        text_feature_names = [f"text_{i}" for i in range(text_features.shape[1])]
        numerical_feature_names = numerical_columns
        all_feature_names = text_feature_names + list(numerical_feature_names)
        
        return combined_features, all_feature_names
    
    def train(self, data: pd.DataFrame, target_column: str, model_save_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Train the risk scoring model.
        
        Args:
            data: DataFrame containing features and target
            target_column: Name of the column containing the risk score
            model_save_path: Path to save the trained model
            
        Returns:
            Dictionary with training metrics
        """
        # Prepare data
        X_data = data.drop(columns=[target_column])
        y_data = data[target_column]
        
        # Preprocess features
        X_processed, feature_names = self.preprocess_data(X_data)
        self.feature_names = feature_names
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_processed, y_data, test_size=0.2, random_state=42
        )
        
        # Train model
        self.model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=4,
            random_state=42
        )
        self.model.fit(X_train, y_train)
        
        # Create SHAP explainer
        self.explainer = shap.TreeExplainer(self.model)
        
        # Evaluate model
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        metrics = {
            "train_r2": train_score,
            "test_r2": test_score,
            "feature_importance": dict(zip(self.feature_names, self.model.feature_importances_))
        }
        
        # Save model if path provided
        if model_save_path:
            self.save_model(model_save_path)
        
        return metrics
    
    def predict(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate risk score and explanation for questionnaire responses.
        
        Args:
            data: DataFrame containing questionnaire responses and metadata
            
        Returns:
            Dictionary with risk score and explanation details
        """
        if self.model is None:
            raise ValueError("Model not trained or loaded. Call train() or load_model() first.")
        
        # Preprocess features
        X_processed, _ = self.preprocess_data(data)
        
        # Generate prediction
        risk_score = self.model.predict(X_processed)[0]
        
        # Generate SHAP values for explanation
        shap_values = self.explainer.shap_values(X_processed)
        
        # Get feature importances for this prediction
        feature_impacts = list(zip(self.feature_names, shap_values[0]))
        feature_impacts.sort(key=lambda x: abs(x[1]), reverse=True)
        
        # Determine top positive and negative factors
        positive_factors = [(f, v) for f, v in feature_impacts if v > 0][:5]
        negative_factors = [(f, v) for f, v in feature_impacts if v < 0][:5]
        
        return {
            "risk_score": float(risk_score),
            "risk_level": self._score_to_level(risk_score),
            "positive_factors": positive_factors,
            "negative_factors": negative_factors,
            "all_factors": feature_impacts
        }
    
    def _score_to_level(self, score: float) -> str:
        """Convert numerical score to risk level category"""
        if score < 0.3:
            return "Low Risk"
        elif score < 0.6:
            return "Medium Risk"
        else:
            return "High Risk"
    
    def save_model(self, model_path: str):
        """Save the model to disk"""
        model_data = {
            "model": self.model,
            "feature_names": self.feature_names,
            "text_vectorizer": self.text_vectorizer,
            "numerical_scaler": self.numerical_scaler
        }
        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)
    
    def load_model(self, model_path: str):
        """Load the model from disk"""
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data["model"]
        self.feature_names = model_data["feature_names"]
        self.text_vectorizer = model_data["text_vectorizer"]
        self.numerical_scaler = model_data["numerical_scaler"]
        
        if self.model is not None:
            self.explainer = shap.TreeExplainer(self.model)