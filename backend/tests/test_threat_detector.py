"""Tests for threat detection service."""
import pytest
from datetime import datetime

from app.services.threat_detector import ThreatDetector
from app.db.models import SecurityLog, EventType, SeverityLevel


def test_threat_detector_initialization():
    """Test threat detector initializes correctly."""
    detector = ThreatDetector()
    assert detector is not None
    assert detector.threat_rules is not None
    assert len(detector.threat_rules) > 0


def test_predict_high_threat():
    """Test prediction for high threat events."""
    detector = ThreatDetector()
    
    # Create a high-threat log
    log = SecurityLog(
        event_type=EventType.MALWARE_DETECTED,
        severity=SeverityLevel.CRITICAL,
        source_ip="203.0.113.1",
        timestamp=datetime.utcnow()
    )
    
    is_threat, confidence, threat_score = detector.predict_threat(log)
    assert is_threat is True
    assert confidence > 0.7
    assert threat_score > 0.6


def test_predict_low_threat():
    """Test prediction for low threat events."""
    detector = ThreatDetector()
    
    # Create a low-threat log
    log = SecurityLog(
        event_type=EventType.LOGIN_ATTEMPT,
        severity=SeverityLevel.LOW,
        source_ip="192.168.1.1",
        timestamp=datetime.utcnow()
    )
    
    is_threat, confidence, threat_score = detector.predict_threat(log)
    assert is_threat is False
    assert threat_score < 0.6


def test_suspicious_ip_detection():
    """Test suspicious IP detection."""
    detector = ThreatDetector()
    
    # External IP should be flagged as suspicious
    assert detector._is_suspicious_ip("203.0.113.1") is True
    
    # Internal IPs should not be suspicious
    assert detector._is_suspicious_ip("192.168.1.1") is False
    assert detector._is_suspicious_ip("10.0.0.1") is False


def test_generate_synthetic_data():
    """Test synthetic data generation."""
    detector = ThreatDetector()
    df = detector.generate_synthetic_data(num_samples=100)
    
    assert len(df) == 100
    assert "event_type" in df.columns
    assert "severity" in df.columns
    assert "is_threat" in df.columns
    assert "threat_score" in df.columns


def test_model_training():
    """Test ML model training with synthetic data."""
    detector = ThreatDetector()
    results = detector.train_model(num_samples=500)
    
    assert detector.is_trained is True
    assert detector.model is not None
    assert "accuracy" in results
    assert results["accuracy"] > 0.5  # Should achieve better than random
    assert results["samples"] == 500
