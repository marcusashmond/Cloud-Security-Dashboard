export interface SecurityLog {
  id: number
  timestamp: string
  event_type: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  source_ip?: string
  destination_ip?: string
  username?: string
  description?: string
  threat_score: number
  is_threat: boolean
  is_anomaly: boolean
  confidence_score?: number
}

export interface Alert {
  id: number
  log_id: number
  title: string
  description?: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  status: string
  created_at: string
  updated_at: string
}

export interface DashboardStats {
  total_logs: number
  total_alerts: number
  critical_alerts: number
  threats_detected: number
  avg_threat_score: number
  recent_logs: SecurityLog[]
  recent_alerts: Alert[]
}

export interface ThreatStatistics {
  total_events: number
  total_threats: number
  threat_by_severity: Record<string, number>
  threat_by_type: Record<string, number>
  top_source_ips: Array<{ ip: string; count: number }>
  timeline: Array<{ date: string; count: number }>
}
