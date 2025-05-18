"""
Script to initialize the database with sample data
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.database import SessionLocal, engine, Base
from app.db.models import User, SecurityLog, Alert, ThreatIndicator
from app.core.security import get_password_hash
from app.services.log_generator import LogGenerator
from datetime import datetime, timedelta
import random

def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created")

def create_default_users(db):
    """Create default users"""
    print("Creating default users...")
    
    users = [
        {
            "username": "admin",
            "email": "admin@security.com",
            "password": "admin123",
            "full_name": "Admin User",
            "is_admin": True
        },
        {
            "username": "analyst",
            "email": "analyst@security.com",
            "password": "analyst123",
            "full_name": "Security Analyst",
            "is_admin": False
        }
    ]
    
    for user_data in users:
        existing_user = db.query(User).filter(User.username == user_data["username"]).first()
        if not existing_user:
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                hashed_password=get_password_hash(user_data["password"]),
                full_name=user_data["full_name"],
                is_admin=user_data["is_admin"],
                is_active=True
            )
            db.add(user)
            print(f"✓ Created user: {user_data['username']}")
    
    db.commit()

def generate_sample_logs(db):
    """Generate sample security logs"""
    print("Generating sample security logs...")
    
    log_gen = LogGenerator()
    logs_data = log_gen.generate_realistic_timeline(days=7)
    
    from app.services.threat_detector import ThreatDetector
    detector = ThreatDetector()
    
    for log_data in logs_data:
        # Convert timestamp string to datetime
        timestamp = datetime.fromisoformat(log_data['timestamp'])
        
        # Create log entry
        log = SecurityLog(
            timestamp=timestamp,
            event_type=log_data['event_type'],
            severity=log_data['severity'],
            source_ip=log_data.get('source_ip'),
            destination_ip=log_data.get('destination_ip'),
            user_agent=log_data.get('user_agent'),
            username=log_data.get('username'),
            description=log_data.get('description'),
            raw_log=log_data.get('raw_log')
        )
        
        # Run threat detection
        is_threat, confidence, threat_score = detector.predict_threat(log)
        log.is_threat = is_threat
        log.confidence_score = confidence
        log.threat_score = threat_score
        log.is_anomaly = threat_score > 0.7
        
        db.add(log)
    
    db.commit()
    print(f"✓ Generated {len(logs_data)} sample logs")

def create_sample_alerts(db):
    """Create sample alerts from threat logs"""
    print("Creating sample alerts...")
    
    threat_logs = db.query(SecurityLog).filter(
        SecurityLog.is_threat == True,
        SecurityLog.threat_score > 0.7
    ).limit(20).all()
    
    admin_user = db.query(User).filter(User.username == "admin").first()
    
    for log in threat_logs:
        alert = Alert(
            log_id=log.id,
            user_id=admin_user.id,
            title=f"{log.event_type.value.replace('_', ' ').title()} Detected",
            description=f"Threat detected from {log.source_ip or 'unknown source'}. {log.description}",
            severity=log.severity,
            status=random.choice(["open", "open", "investigating", "resolved"])
        )
        db.add(alert)
    
    db.commit()
    print(f"✓ Created {len(threat_logs)} sample alerts")

def create_threat_indicators(db):
    """Create sample threat indicators"""
    print("Creating threat indicators...")
    
    indicators = [
        {"type": "ip", "value": "185.220.101.23", "threat_level": "high", "description": "Known malicious IP"},
        {"type": "ip", "value": "89.248.165.12", "threat_level": "critical", "description": "C2 server"},
        {"type": "domain", "value": "malicious-site.evil", "threat_level": "high", "description": "Phishing domain"},
        {"type": "hash", "value": "d41d8cd98f00b204e9800998ecf8427e", "threat_level": "medium", "description": "Suspicious file hash"},
    ]
    
    for indicator_data in indicators:
        existing = db.query(ThreatIndicator).filter(
            ThreatIndicator.value == indicator_data["value"]
        ).first()
        
        if not existing:
            indicator = ThreatIndicator(
                indicator_type=indicator_data["type"],
                value=indicator_data["value"],
                threat_level=indicator_data["threat_level"],
                description=indicator_data["description"],
                source="Manual Entry",
                is_active=True
            )
            db.add(indicator)
    
    db.commit()
    print(f"✓ Created {len(indicators)} threat indicators")

def main():
    """Main initialization function"""
    print("\n" + "="*50)
    print("Security Dashboard - Database Initialization")
    print("="*50 + "\n")
    
    db = SessionLocal()
    
    try:
        create_tables()
        create_default_users(db)
        generate_sample_logs(db)
        create_sample_alerts(db)
        create_threat_indicators(db)
        
        print("\n" + "="*50)
        print("✓ Database initialization complete!")
        print("="*50)
        print("\nDefault credentials:")
        print("  Admin:    username: admin    password: admin123")
        print("  Analyst:  username: analyst  password: analyst123")
        print("\n")
        
    except Exception as e:
        print(f"\n✗ Error during initialization: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
