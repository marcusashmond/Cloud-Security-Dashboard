# API Testing with curl

## Authentication

### Register User
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "full_name": "Test User"
  }'
```

### Login
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

Save the token from response:
```bash
export TOKEN="your-jwt-token-here"
```

## Security Logs

### Get All Logs
```bash
curl -X GET "http://localhost:8000/api/logs" \
  -H "Authorization: Bearer $TOKEN"
```

### Get Logs with Filters
```bash
# Filter by severity
curl -X GET "http://localhost:8000/api/logs?severity=critical" \
  -H "Authorization: Bearer $TOKEN"

# Filter by threat status
curl -X GET "http://localhost:8000/api/logs?is_threat=true" \
  -H "Authorization: Bearer $TOKEN"

# Date range filter
curl -X GET "http://localhost:8000/api/logs?start_date=2026-01-01T00:00:00&end_date=2026-01-15T23:59:59" \
  -H "Authorization: Bearer $TOKEN"
```

### Create Log Entry
```bash
curl -X POST "http://localhost:8000/api/logs" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "failed_login",
    "severity": "medium",
    "source_ip": "192.168.1.100",
    "username": "testuser",
    "description": "Failed login attempt detected"
  }'
```

### Export Logs to CSV
```bash
curl -X GET "http://localhost:8000/api/logs/export/csv" \
  -H "Authorization: Bearer $TOKEN" \
  -o security_logs.csv
```

## Alerts

### Get All Alerts
```bash
curl -X GET "http://localhost:8000/api/alerts" \
  -H "Authorization: Bearer $TOKEN"
```

### Get Alerts by Status
```bash
curl -X GET "http://localhost:8000/api/alerts?status=open" \
  -H "Authorization: Bearer $TOKEN"
```

### Create Alert
```bash
curl -X POST "http://localhost:8000/api/alerts" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "log_id": 1,
    "title": "Critical Threat Detected",
    "description": "Brute force attack from suspicious IP",
    "severity": "critical"
  }'
```

### Update Alert Status
```bash
curl -X PUT "http://localhost:8000/api/alerts/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "resolved",
    "notes": "False positive - legitimate user"
  }'
```

## Analytics

### Dashboard Summary
```bash
curl -X GET "http://localhost:8000/api/analytics/dashboard" \
  -H "Authorization: Bearer $TOKEN"
```

### Threat Statistics
```bash
# Last 7 days (default)
curl -X GET "http://localhost:8000/api/analytics/statistics" \
  -H "Authorization: Bearer $TOKEN"

# Last 30 days
curl -X GET "http://localhost:8000/api/analytics/statistics?days=30" \
  -H "Authorization: Bearer $TOKEN"
```

### Hourly Trends
```bash
# Last 24 hours (default)
curl -X GET "http://localhost:8000/api/analytics/trends" \
  -H "Authorization: Bearer $TOKEN"

# Last 7 days (168 hours)
curl -X GET "http://localhost:8000/api/analytics/trends?hours=168" \
  -H "Authorization: Bearer $TOKEN"
```

## Health Check

```bash
curl -X GET "http://localhost:8000/health"
```

## API Documentation

Visit in browser:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
