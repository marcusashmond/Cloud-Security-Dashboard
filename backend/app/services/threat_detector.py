"""
Threat Detection Service using Machine Learning
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
import os
from typing import Tuple, List
from datetime import datetime, timedelta
import random

from app.db.models import SecurityLog, SeverityLevel, EventType


class ThreatDetector:
    """ML-based threat detection system"""
    
    def __init__(self):
        self.model = None
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.model_path = "app/ml_models/threat_model.pkl"
        self.encoders_path = "app/ml_models/encoders.pkl"
        self.scaler_path = "app/ml_models/scaler.pkl"
        self.is_trained = False
        
        # Try to load existing model
        # NOTE: Falls back to heuristics if model doesn't exist - this saved us during demo
        self.load_model()
        # print(f"DEBUG: Model loaded: {self.is_trained}")  # Uncomment for debugging
        
        # Initialize with simple heuristic rules
        # These values were tuned based on our security team's feedback
        # TODO: should probably move these to a config file
        self.threat_rules = {
            EventType.FAILED_LOGIN: 0.3,  # bumped from 0.2 - too many false negatives
            EventType.BRUTE_FORCE: 0.9,
            EventType.MALWARE_DETECTED: 0.95,
            EventType.UNAUTHORIZED_ACCESS: 0.85,
            EventType.DATA_EXFILTRATION: 0.95,
            EventType.SUSPICIOUS_ACTIVITY: 0.6,
            EventType.POLICY_VIOLATION: 0.4,
            EventType.NETWORK_ANOMALY: 0.7,
            EventType.FILE_INTEGRITY: 0.5,
            EventType.LOGIN_ATTEMPT: 0.1,
        }
        
        self.severity_weights = {
            SeverityLevel.LOW: 0.25,
            SeverityLevel.MEDIUM: 0.5,
            SeverityLevel.HIGH: 0.75,
            SeverityLevel.CRITICAL: 1.0,
        }
    
    def predict_threat(self, log: SecurityLog) -> Tuple[bool, float, float]:
        """
        Predict if a log entry is a threat
        
        Returns:
            (is_threat, confidence_score, threat_score)
        """
        # If ML model is trained, use it
        if self.is_trained and self.model:
            try:
                features = self._extract_features(log)
                prediction = self.model.predict_proba([features])[0]
                threat_score = prediction[1]  # Probability of being a threat
                is_threat = threat_score > 0.6
                confidence = max(prediction)
                return is_threat, round(confidence, 3), round(threat_score, 3)
            except Exception as e:
                print(f"ML prediction error: {e}, falling back to heuristics")
        
        # Old approach - simple threshold-based detection
        # Left this here because ML doesn't always load on first run
        # if log.event_type in high_threat_types:
        #     return True, 0.8, 0.85
        # return False, 0.7, 0.2
        
        # Fallback to heuristic-based detection
        base_score = self.threat_rules.get(log.event_type, 0.5)
        severity_weight = self.severity_weights.get(log.severity, 0.5)
        
        # Combined threat score
        threat_score = (base_score * 0.7) + (severity_weight * 0.3)
        
        # Additional heuristics
        if log.source_ip:
            if self._is_suspicious_ip(log.source_ip):
                threat_score += 0.2
        
        if log.event_type == EventType.FAILED_LOGIN:
            threat_score += 0.2
        
        # Normalize threat score
        threat_score = min(threat_score, 1.0)
        
        # Determine if it's a threat (threshold = 0.6)
        is_threat = threat_score > 0.6
        confidence = threat_score if is_threat else (1 - threat_score)
        
        return is_threat, round(confidence, 3), round(threat_score, 3)
    
    def _is_suspicious_ip(self, ip: str) -> bool:
        """Check if IP is suspicious (simplified)"""
        suspicious_patterns = [
            '192.168.',  # Internal IPs shouldn't be external threats
            '10.',
            '172.16.',
        ]
        return not any(ip.startswith(pattern) for pattern in suspicious_patterns)
    
    def _extract_features(self, log: SecurityLog) -> List[float]:
        """Extract numerical features from a log entry for ML prediction."""
        features = []
        
        # Encode event type
        if 'event_type' in self.label_encoders:
            try:
                event_encoded = self.label_encoders['event_type'].transform([log.event_type.value])[0]
            except:
                event_encoded = 0
        else:
            event_encoded = 0
        features.append(event_encoded)
        
        # Encode severity
        if 'severity' in self.label_encoders:
            try:
                severity_encoded = self.label_encoders['severity'].transform([log.severity.value])[0]
            except:
                severity_encoded = 0
        else:
            severity_encoded = 0
        features.append(severity_encoded)
        
        # Threat score (if available)
        features.append(log.threat_score if log.threat_score else 0.0)
        
        # Hour of day (normalized 0-1)
        hour = log.timestamp.hour if log.timestamp else 0
        features.append(hour / 24.0)
        
        # Day of week (normalized 0-1)
        day_of_week = log.timestamp.weekday() if log.timestamp else 0
        features.append(day_of_week / 7.0)
        
        # Is anomaly flag
        features.append(1.0 if log.is_anomaly else 0.0)
        
        return features
    
    def generate_synthetic_data(self, num_samples: int = 1000) -> pd.DataFrame:
        """Generate synthetic training data for the ML model."""
        data = []
        
        for _ in range(num_samples):
            # Random event type
            event_type = random.choice(list(EventType))
            
            # Assign severity based on event type
            if event_type in [EventType.MALWARE_DETECTED, EventType.DATA_EXFILTRATION, 
                             EventType.BRUTE_FORCE]:
                severity = random.choice([SeverityLevel.HIGH, SeverityLevel.CRITICAL])
                is_threat = True
            elif event_type in [EventType.UNAUTHORIZED_ACCESS, EventType.NETWORK_ANOMALY]:
                severity = random.choice([SeverityLevel.MEDIUM, SeverityLevel.HIGH])
                is_threat = random.random() > 0.3  # 70% threat
            elif event_type in [EventType.FAILED_LOGIN, EventType.SUSPICIOUS_ACTIVITY]:
                severity = random.choice([SeverityLevel.LOW, SeverityLevel.MEDIUM])
                is_threat = random.random() > 0.6  # 40% threat
            else:
                severity = SeverityLevel.LOW
                is_threat = random.random() > 0.8  # 20% threat
            
            # Generate timestamp
            days_ago = random.randint(0, 365)
            timestamp = datetime.utcnow() - timedelta(days=days_ago, hours=random.randint(0, 23))
            
            # Threat score based on rules
            base_score = self.threat_rules.get(event_type, 0.5)
            severity_weight = self.severity_weights.get(severity, 0.5)
            threat_score = (base_score * 0.7) + (severity_weight * 0.3) + random.uniform(-0.1, 0.1)
            threat_score = max(0.0, min(1.0, threat_score))
            
            data.append({
                'event_type': event_type.value,
                'severity': severity.value,
                'threat_score': threat_score,
                'hour': timestamp.hour,
                'day_of_week': timestamp.weekday(),
                'is_anomaly': random.random() > 0.9,  # 10% anomalies
                'is_threat': is_threat
            })
        
        return pd.DataFrame(data)
    
    def train_model(self, num_samples: int = 5000):
        """Train the ML model with synthetic data."""
        print(f"Generating {num_samples} synthetic training samples...")
        df = self.generate_synthetic_data(num_samples)
        
        # Prepare features
        X = df[['event_type', 'severity', 'threat_score', 'hour', 'day_of_week', 'is_anomaly']].copy()
        y = df['is_threat'].astype(int)
        
        # Encode categorical features
        self.label_encoders['event_type'] = LabelEncoder()
        self.label_encoders['severity'] = LabelEncoder()
        
        X['event_type'] = self.label_encoders['event_type'].fit_transform(X['event_type'])
        X['severity'] = self.label_encoders['severity'].fit_transform(X['severity'])
        X['is_anomaly'] = X['is_anomaly'].astype(int)
        
        # Normalize numerical features
        numerical_cols = ['threat_score', 'hour', 'day_of_week']
        X[numerical_cols] = self.scaler.fit_transform(X[numerical_cols])
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train Random Forest model
        print("Training Random Forest model...")
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        
        print(f"\nModel Performance:")
        print(f"  Accuracy:  {accuracy:.3f}")
        print(f"  Precision: {precision:.3f}")
        print(f"  Recall:    {recall:.3f}")
        print(f"  F1 Score:  {f1:.3f}")
        
        self.is_trained = True
        self.save_model()
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'samples': num_samples
        }
    
    def load_model(self):
        """Load pre-trained model."""
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                self.label_encoders = joblib.load(self.encoders_path)
                self.scaler = joblib.load(self.scaler_path)
                self.is_trained = True
                print("✓ Pre-trained threat detection model loaded")
        except Exception as e:
            print(f"Could not load model: {e}")
            self.is_trained = False
    
    def save_model(self):
        """Save trained model and encoders."""
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.label_encoders, self.encoders_path)
            joblib.dump(self.scaler, self.scaler_path)
            print(f"✓ Model saved to {self.model_path}")
        except Exception as e:
            print(f"Error saving model: {e}")
