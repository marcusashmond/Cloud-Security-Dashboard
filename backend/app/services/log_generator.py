"""
Log Generator for Testing and Demo Purposes
"""
import random
from datetime import datetime, timedelta
from typing import List
import json

from app.db.models import EventType, SeverityLevel


class LogGenerator:
    """Generate realistic security log data"""
    
    def __init__(self):
        self.event_types = list(EventType)
        self.severity_levels = list(SeverityLevel)
        
        self.sample_ips = [
            "192.168.1.100", "10.0.0.50", "172.16.0.25",
            "203.0.113.42", "198.51.100.78", "45.33.32.156",
            "185.220.101.23", "89.248.165.12", "23.95.190.45"
        ]
        
        self.sample_usernames = [
            "admin", "user1", "john.doe", "jane.smith", 
            "dbadmin", "root", "service_account", "test_user"
        ]
        
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "curl/7.68.0",
            "python-requests/2.25.1",
            "PostmanRuntime/7.28.4"
        ]
        
        self.descriptions = {
            EventType.LOGIN_ATTEMPT: [
                "Successful login from {ip}",
                "User {user} logged in successfully",
                "Login attempt from {ip}"
            ],
            EventType.FAILED_LOGIN: [
                "Failed login attempt for user {user}",
                "Invalid password for {user} from {ip}",
                "Multiple failed login attempts detected"
            ],
            EventType.BRUTE_FORCE: [
                "Brute force attack detected from {ip}",
                "Multiple rapid login attempts from {ip}",
                "Potential brute force attack on account {user}"
            ],
            EventType.MALWARE_DETECTED: [
                "Malware signature detected in file",
                "Suspicious executable blocked",
                "Trojan detected and quarantined"
            ],
            EventType.UNAUTHORIZED_ACCESS: [
                "Unauthorized access attempt to {resource}",
                "Access denied for {user} to restricted area",
                "Privilege escalation attempt detected"
            ],
            EventType.DATA_EXFILTRATION: [
                "Large data transfer detected to {ip}",
                "Suspicious data export activity",
                "Unauthorized data access and download"
            ],
            EventType.SUSPICIOUS_ACTIVITY: [
                "Unusual user behavior detected",
                "Off-hours access from {user}",
                "Anomalous network traffic pattern"
            ],
            EventType.POLICY_VIOLATION: [
                "Security policy violation by {user}",
                "Unapproved software installation detected",
                "Policy breach: {detail}"
            ],
            EventType.NETWORK_ANOMALY: [
                "Unusual network traffic from {ip}",
                "Port scan detected from {ip}",
                "Abnormal bandwidth usage"
            ],
            EventType.FILE_INTEGRITY: [
                "File integrity check failed",
                "Unauthorized file modification detected",
                "Critical system file changed"
            ]
        }
    
    def generate_log(self, event_type: EventType = None) -> dict:
        """Generate a single log entry"""
        if event_type is None:
            event_type = random.choice(self.event_types)
        
        # Determine severity based on event type
        severity_map = {
            EventType.LOGIN_ATTEMPT: SeverityLevel.LOW,
            EventType.FAILED_LOGIN: random.choice([SeverityLevel.LOW, SeverityLevel.MEDIUM]),
            EventType.BRUTE_FORCE: random.choice([SeverityLevel.HIGH, SeverityLevel.CRITICAL]),
            EventType.MALWARE_DETECTED: SeverityLevel.CRITICAL,
            EventType.UNAUTHORIZED_ACCESS: random.choice([SeverityLevel.HIGH, SeverityLevel.CRITICAL]),
            EventType.DATA_EXFILTRATION: SeverityLevel.CRITICAL,
            EventType.SUSPICIOUS_ACTIVITY: random.choice([SeverityLevel.MEDIUM, SeverityLevel.HIGH]),
            EventType.POLICY_VIOLATION: SeverityLevel.MEDIUM,
            EventType.NETWORK_ANOMALY: random.choice([SeverityLevel.MEDIUM, SeverityLevel.HIGH]),
            EventType.FILE_INTEGRITY: SeverityLevel.HIGH,
        }
        
        severity = severity_map.get(event_type, SeverityLevel.MEDIUM)
        source_ip = random.choice(self.sample_ips)
        username = random.choice(self.sample_usernames)
        
        # Generate description
        desc_templates = self.descriptions.get(event_type, ["Security event detected"])
        description = random.choice(desc_templates).format(
            ip=source_ip,
            user=username,
            resource="database",
            detail="unauthorized software"
        )
        
        log_data = {
            "event_type": event_type.value,
            "severity": severity.value,
            "source_ip": source_ip,
            "destination_ip": random.choice(self.sample_ips),
            "user_agent": random.choice(self.user_agents),
            "username": username,
            "description": description,
            "raw_log": json.dumps({
                "timestamp": datetime.utcnow().isoformat(),
                "event": event_type.value,
                "details": description
            })
        }
        
        return log_data
    
    def generate_batch(self, count: int = 100) -> List[dict]:
        """Generate multiple log entries"""
        return [self.generate_log() for _ in range(count)]
    
    def generate_realistic_timeline(self, days: int = 7) -> List[dict]:
        """Generate logs with realistic timestamps over a time period"""
        logs = []
        start_date = datetime.utcnow() - timedelta(days=days)
        
        for _ in range(days * 50):  # ~50 logs per day
            # Random timestamp within the period
            random_seconds = random.randint(0, days * 24 * 60 * 60)
            timestamp = start_date + timedelta(seconds=random_seconds)
            
            log = self.generate_log()
            log['timestamp'] = timestamp.isoformat()
            logs.append(log)
        
        return sorted(logs, key=lambda x: x['timestamp'])
