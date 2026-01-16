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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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
    
    # Timeline (events per day) - optimized with single query
    timeline = []
    timeline_data = db.query(
        func.date(SecurityLog.timestamp).label('date'),
        func.count(SecurityLog.id).label('count')
    ).filter(
        SecurityLog.timestamp >= start_date
    ).group_by(func.date(SecurityLog.timestamp)).all()
    
    # Create map for quick lookup
    date_counts = {str(date): count for date, count in timeline_data}
    
    # Fill in all days including zeros
    for i in range(days):
        day = start_date + timedelta(days=i)
        date_str = day.strftime("%Y-%m-%d")
        timeline.append({
            "date": date_str,
            "count": date_counts.get(date_str, 0)
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
    """Get hourly trends - optimized"""
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    # Get all data in single query
    hourly_counts = db.query(
        func.strftime('%Y-%m-%d %H:00', SecurityLog.timestamp).label('hour'),
        func.count(SecurityLog.id).label('total'),
        func.sum(func.cast(SecurityLog.is_threat, func.INTEGER())).label('threats')
    ).filter(
        SecurityLog.timestamp >= start_time
    ).group_by(func.strftime('%Y-%m-%d %H:00', SecurityLog.timestamp)).all()
    
    # Create map
    hour_map = {hour: {'total': total, 'threats': threats or 0} for hour, total, threats in hourly_counts}
    
    # Fill in all hours
    hourly_data = []
    for i in range(hours):
        hour_time = start_time + timedelta(hours=i)
        hour_str = hour_time.strftime("%Y-%m-%d %H:00")
        data = hour_map.get(hour_str, {'total': 0, 'threats': 0})
        hourly_data.append({
            "hour": hour_str,
            "total": data['total'],
            "threats": data['threats']
        })
    
    return {"hourly_trends": hourly_data}
