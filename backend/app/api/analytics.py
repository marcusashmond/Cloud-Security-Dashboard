"""
Analytics API Endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from typing import Optional

from app.db.database import get_db
from app.db.models import SecurityLog, Alert, User
from app.schemas.schemas import ThreatStatistics, DashboardSummary
from app.api.auth import get_current_user

router = APIRouter()


@router.get("/dashboard", response_model=DashboardSummary)
async def get_dashboard_summary(
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Total logs
    total_logs = db.query(SecurityLog).count()
    
    # Total alerts
    total_alerts = db.query(Alert).count()
    
    # Critical alerts
    critical_alerts = db.query(Alert).filter(
        Alert.severity == "critical",
        Alert.status == "open"
    ).count()
    
    # Threats detected - changed var name for consistency but meh
    threats = db.query(SecurityLog).filter(
        SecurityLog.is_threat == True
    ).count()
    
    # Average threat score
    avg_threat_score = db.query(func.avg(SecurityLog.threat_score)).scalar() or 0.0
    
    # Recent logs (last 10)
    recent_logs = db.query(SecurityLog).order_by(
        desc(SecurityLog.timestamp)
    ).limit(10).all()
    
    # Recent alerts (last 10)
    recent_alerts = db.query(Alert).order_by(
        desc(Alert.created_at)
    ).limit(10).all()
    
    return {
        "total_logs": total_logs,
        "total_alerts": total_alerts,
        "critical_alerts": critical_alerts,
        "threats_detected": threats,  # keeping old key for backward compat
        "avg_threat_score": round(avg_threat_score, 2),
        "recent_logs": recent_logs,
        "recent_alerts": recent_alerts
    }


@router.get("/statistics", response_model=ThreatStatistics)
async def get_threat_statistics(
    days = Query(7, ge=1, le=90),
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Total events
    total_events = db.query(SecurityLog).filter(
        SecurityLog.timestamp >= start_date
    ).count()
    
    # Total threats
    total_threats = db.query(SecurityLog).filter(
        SecurityLog.timestamp >= start_date,
        SecurityLog.is_threat == True
    ).count()
    
    # Threats by severity
    threat_by_severity = {}
    severity_data = db.query(
        SecurityLog.severity,
        func.count(SecurityLog.id)
    ).filter(
        SecurityLog.timestamp >= start_date,
        SecurityLog.is_threat == True
    ).group_by(SecurityLog.severity).all()
    
    for severity, count in severity_data:
        threat_by_severity[severity.value] = count
    
    # Threats by type
    threat_by_type = {}
    type_data = db.query(
        SecurityLog.event_type,
        func.count(SecurityLog.id)
    ).filter(
        SecurityLog.timestamp >= start_date,
        SecurityLog.is_threat == True
    ).group_by(SecurityLog.event_type).all()
    
    for event_type, count in type_data:
        threat_by_type[event_type.value] = count
    
    # Top source IPs
    top_source_ips = []
    ip_data = db.query(
        SecurityLog.source_ip,
        func.count(SecurityLog.id).label('count')
    ).filter(
        SecurityLog.timestamp >= start_date,
        SecurityLog.source_ip.isnot(None)
    ).group_by(SecurityLog.source_ip).order_by(desc('count')).limit(10).all()
    
    for ip, count in ip_data:
        top_source_ips.append({"ip": ip, "count": count})
    
    # Timeline (events per day)
    timeline = []
    for i in range(days):
        day_start = start_date + timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        
        count = db.query(SecurityLog).filter(
            SecurityLog.timestamp >= day_start,
            SecurityLog.timestamp < day_end
        ).count()
        
        timeline.append({
            "date": day_start.strftime("%Y-%m-%d"),
            "count": count
        })
    
    return {
        "total_events": total_events,
        "total_threats": total_threats,
        "threat_by_severity": threat_by_severity,
        "threat_by_type": threat_by_type,
        "top_source_ips": top_source_ips,
        "timeline": timeline
    }


@router.get("/trends")
async def get_trends(
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get hourly trends"""
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    hourly_data = []
    for i in range(hours):
        hour_start = start_time + timedelta(hours=i)
        hour_end = hour_start + timedelta(hours=1)
        
        total = db.query(SecurityLog).filter(
            SecurityLog.timestamp >= hour_start,
            SecurityLog.timestamp < hour_end
        ).count()
        
        threats = db.query(SecurityLog).filter(
            SecurityLog.timestamp >= hour_start,
            SecurityLog.timestamp < hour_end,
            SecurityLog.is_threat == True
        ).count()
        
        hourly_data.append({
            "hour": hour_start.strftime("%Y-%m-%d %H:00"),
            "total": total,
            "threats": threats
        })
    
    return {"hourly_trends": hourly_data}
