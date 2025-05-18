"""
Database Models
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.database import Base


class SeverityLevel(str, enum.Enum):
    """Security event severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EventType(str, enum.Enum):
    """Security event types"""
    # Based on NIST cybersecurity framework categories
    # We might need to add more types as we encounter new threats
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


class UserRole(str, enum.Enum):
    """User roles for RBAC"""
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"


class AuditAction(str, enum.Enum):
    """Audit log action types"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    ACCESS_DENIED = "access_denied"


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    alerts = relationship("Alert", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")


class SecurityLog(Base):
    """Security log entries"""
    __tablename__ = "security_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    event_type = Column(SQLEnum(EventType), nullable=False, index=True)
    severity = Column(SQLEnum(SeverityLevel), default=SeverityLevel.LOW, index=True)
    source_ip = Column(String(45))  # IPv6 compatible
    destination_ip = Column(String(45))
    user_agent = Column(Text)
    username = Column(String(100), index=True)
    description = Column(Text)
    raw_log = Column(Text)
    threat_score = Column(Float, default=0.0)
    is_anomaly = Column(Boolean, default=False)
    country = Column(String(100))
    city = Column(String(100))
    
    # ML Detection
    is_threat = Column(Boolean, default=False)
    confidence_score = Column(Float)
    
    # Relationships
    alerts = relationship("Alert", back_populates="log")


class Alert(Base):
    """Security alerts"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    log_id = Column(Integer, ForeignKey("security_logs.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    severity = Column(SQLEnum(SeverityLevel), nullable=False, index=True)
    status = Column(String(50), default="open")  # open, investigating, resolved, false_positive
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime)
    resolved_by = Column(String(100))
    notes = Column(Text)
    
    # Relationships
    log = relationship("SecurityLog", back_populates="alerts")
    user = relationship("User", back_populates="alerts")


class ThreatIndicator(Base):
    """Known threat indicators (IOCs)"""
    __tablename__ = "threat_indicators"
    
    id = Column(Integer, primary_key=True, index=True)
    indicator_type = Column(String(50), nullable=False)  # ip, domain, hash, email
    value = Column(String(255), nullable=False, unique=True, index=True)
    threat_level = Column(SQLEnum(SeverityLevel), default=SeverityLevel.MEDIUM)
    description = Column(Text)
    source = Column(String(100))
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class AuditLog(Base):
    """Audit log for compliance tracking"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(SQLEnum(AuditAction), nullable=False, index=True)
    resource_type = Column(String(100))  # e.g., "security_log", "alert", "user"
    resource_id = Column(Integer)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    details = Column(Text)  # JSON string with additional details
    success = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")

