"""
Pydantic Schemas for Request/Response Validation
"""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EventType(str, Enum):
    LOGIN_ATTEMPT = "login_attempt"
    FAILED_LOGIN = "failed_login"
    BRUTE_FORCE = "brute_force"
    MALWARE_DETECTED = "malware_detected"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_EXFILTRATION = "data_exfiltration"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    POLICY_VIOLATION = "policy_violation"
    NETWORK_ANOMALY = "network_anomaly"
    FILE_INTEGRITY = "file_integrity"


# User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class User(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


# Security Log Schemas
class SecurityLogBase(BaseModel):
    event_type: EventType
    severity: SeverityLevel = SeverityLevel.LOW
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    user_agent: Optional[str] = None
    username: Optional[str] = None
    description: Optional[str] = None


class SecurityLogCreate(SecurityLogBase):
    raw_log: Optional[str] = None


class SecurityLog(SecurityLogBase):
    id: int
    timestamp: datetime
    threat_score: float
    is_anomaly: bool
    is_threat: bool
    confidence_score: Optional[float] = None
    country: Optional[str] = None
    city: Optional[str] = None
    
    class Config:
        from_attributes = True


class SecurityLogList(BaseModel):
    logs: List[SecurityLog]
    total: int
    page: int
    page_size: int


# Alert Schemas
class AlertBase(BaseModel):
    title: str
    description: Optional[str] = None
    severity: SeverityLevel


class AlertCreate(AlertBase):
    log_id: int


class Alert(AlertBase):
    id: int
    log_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    
    class Config:
        from_attributes = True


class AlertUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    resolved_by: Optional[str] = None


# Analytics Schemas
class ThreatStatistics(BaseModel):
    total_events: int
    total_threats: int
    threat_by_severity: dict
    threat_by_type: dict
    top_source_ips: List[dict]
    timeline: List[dict]


class DashboardSummary(BaseModel):
    total_logs: int
    total_alerts: int
    critical_alerts: int
    threats_detected: int
    avg_threat_score: float
    recent_logs: List[SecurityLog]
    recent_alerts: List[Alert]
