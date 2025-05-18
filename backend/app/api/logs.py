"""
Security Logs API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from typing import Optional, List
from datetime import datetime, timedelta

from app.db.database import get_db
from app.db.models import SecurityLog, User
from app.schemas.schemas import SecurityLog as SecurityLogSchema, SecurityLogCreate, SecurityLogList
from app.api.auth import get_current_user
from app.services.threat_detector import ThreatDetector
from app.core.websocket_manager import manager

router = APIRouter()
threat_detector = ThreatDetector()


@router.get("/", response_model=SecurityLogList)
async def get_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    severity: Optional[str] = None,
    event_type: Optional[str] = None,
    is_threat: Optional[bool] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get security logs with filtering"""
    query = db.query(SecurityLog)
    
    # Apply filters
    if severity:
        query = query.filter(SecurityLog.severity == severity)
    if event_type:
        query = query.filter(SecurityLog.event_type == event_type)
    if is_threat is not None:
        query = query.filter(SecurityLog.is_threat == is_threat)
    if start_date:
        query = query.filter(SecurityLog.timestamp >= start_date)
    if end_date:
        query = query.filter(SecurityLog.timestamp <= end_date)
    
    # Get total count
    total = query.count()
    
    # Get paginated results
    logs = query.order_by(desc(SecurityLog.timestamp)).offset(skip).limit(limit).all()
    
    return {
        "logs": logs,
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit
    }


@router.get("/{log_id}", response_model=SecurityLogSchema)
async def get_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific security log"""
    log = db.query(SecurityLog).filter(SecurityLog.id == log_id).first()
    
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    
    return log


@router.post("/", response_model=SecurityLogSchema)
async def create_log(
    log: SecurityLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new security log entry"""
    # Create log entry
    db_log = SecurityLog(**log.dict())
    
    # Run threat detection
    is_threat, confidence, threat_score = threat_detector.predict_threat(db_log)
    db_log.is_threat = is_threat
    db_log.confidence_score = confidence
    db_log.threat_score = threat_score
    db_log.is_anomaly = threat_score > 0.7
    
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    
    # Broadcast to WebSocket clients
    await manager.broadcast_json({
        "type": "new_log",
        "data": {
            "id": db_log.id,
            "event_type": db_log.event_type.value,
            "severity": db_log.severity.value,
            "is_threat": db_log.is_threat,
            "timestamp": db_log.timestamp.isoformat()
        }
    })
    
    return db_log


@router.delete("/{log_id}")
async def delete_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a security log"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    log = db.query(SecurityLog).filter(SecurityLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    
    db.delete(log)
    db.commit()
    
    return {"message": "Log deleted successfully"}


@router.get("/export/csv")
async def export_logs_csv(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export logs to CSV format"""
    from fastapi.responses import StreamingResponse
    import io
    import csv
    
    query = db.query(SecurityLog)
    if start_date:
        query = query.filter(SecurityLog.timestamp >= start_date)
    if end_date:
        query = query.filter(SecurityLog.timestamp <= end_date)
    
    logs = query.order_by(desc(SecurityLog.timestamp)).all()
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'ID', 'Timestamp', 'Event Type', 'Severity', 'Source IP',
        'Destination IP', 'Username', 'Description', 'Threat Score',
        'Is Threat', 'Is Anomaly'
    ])
    
    # Write data
    for log in logs:
        writer.writerow([
            log.id, log.timestamp, log.event_type.value, log.severity.value,
            log.source_ip, log.destination_ip, log.username, log.description,
            log.threat_score, log.is_threat, log.is_anomaly
        ])
    
    output.seek(0)
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=security_logs.csv"}
    )
