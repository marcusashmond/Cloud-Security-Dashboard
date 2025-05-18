"""Audit logging service for compliance tracking."""
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
import json

from app.db.models import AuditLog, AuditAction, User


class AuditService:
    """Service for creating and managing audit logs."""
    
    @staticmethod
    def log_action(
        db: Session,
        action: AuditAction,
        user_id: Optional[int] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[dict] = None,
        success: bool = True
    ) -> AuditLog:
        """Create an audit log entry."""
        try:
            audit_log = AuditLog(
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                ip_address=ip_address,
                user_agent=user_agent,
                timestamp=datetime.utcnow(),
                details=json.dumps(details) if details else None,
                success=success
            )
            db.add(audit_log)
            db.commit()
            db.refresh(audit_log)
            return audit_log
        except Exception as e:
            # Should probably handle this better
            print(f"Audit log failed: {e}")
            db.rollback()
            return None
    
    @staticmethod
    def log_login(
        db: Session,
        user_id: int,
        ip_address: str,
        user_agent: str,
        success: bool = True
    ):
        """Log a login attempt."""
        return AuditService.log_action(
            db=db,
            action=AuditAction.LOGIN,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            details={"event": "user_login"}
        )
    
    @staticmethod
    def log_logout(
        db: Session,
        user_id: int,
        ip_address: str,
        user_agent: str
    ):
        """Log a logout."""
        return AuditService.log_action(
            db=db,
            action=AuditAction.LOGOUT,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details={"event": "user_logout"}
        )
    
    @staticmethod
    def log_access_denied(
        db: Session,
        user_id: Optional[int],
        resource_type: str,
        resource_id: Optional[int],
        ip_address: str,
        user_agent: str,
        reason: str
    ):
        """Log an access denied event."""
        return AuditService.log_action(
            db=db,
            action=AuditAction.ACCESS_DENIED,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            success=False,
            details={"reason": reason}
        )
    
    @staticmethod
    def log_resource_action(
        db: Session,
        action: AuditAction,
        user_id: int,
        resource_type: str,
        resource_id: int,
        ip_address: str,
        user_agent: str,
        changes: Optional[dict] = None
    ):
        """Log a resource modification action (create, update, delete)."""
        return AuditService.log_action(
            db=db,
            action=action,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details={"changes": changes} if changes else None
        )
    
    @staticmethod
    def get_user_audit_logs(
        db: Session,
        user_id: int,
        limit: int = 100,
        offset: int = 0
    ):
        """Get audit logs for a specific user."""
        return db.query(AuditLog).filter(
            AuditLog.user_id == user_id
        ).order_by(
            AuditLog.timestamp.desc()
        ).limit(limit).offset(offset).all()
    
    @staticmethod
    def get_audit_logs_by_action(
        db: Session,
        action: AuditAction,
        limit: int = 100,
        offset: int = 0
    ):
        """Get audit logs by action type."""
        return db.query(AuditLog).filter(
            AuditLog.action == action
        ).order_by(
            AuditLog.timestamp.desc()
        ).limit(limit).offset(offset).all()
    
    @staticmethod
    def get_recent_audit_logs(
        db: Session,
        limit: int = 100,
        offset: int = 0
    ):
        """Get recent audit logs."""
        return db.query(AuditLog).order_by(
            AuditLog.timestamp.desc()
        ).limit(limit).offset(offset).all()
