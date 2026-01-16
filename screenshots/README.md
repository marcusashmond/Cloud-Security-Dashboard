# Screenshots Guide

## Required Screenshots

To make your portfolio project stand out, take the following screenshots:

### 1. Dashboard Overview (`dashboard.png`)
**What to capture:**
- Main dashboard page at `http://localhost:3000/dashboard`
- Show threat statistics cards (total logs, threats detected, critical alerts)
- Include at least 2-3 charts (threat trends, severity distribution)
- Make sure recent logs/alerts are visible

**Tips:**
- Use full browser window (1920x1080 recommended)
- Log in as admin to show all features
- Generate some sample data first (run the seed script)

### 2. Security Logs (`logs.png`)
**What to capture:**
- Logs page showing the table with multiple entries
- Show filters in use (severity, threat status)
- Highlight threat indicators (red badges for threats)
- Include pagination controls

**Tips:**
- Show mix of threat and safe events
- Display different severity levels (low, medium, high, critical)
- Capture the export CSV button

### 3. Analytics (`analytics.png`)
**What to capture:**
- Analytics page with multiple interactive charts
- Show time range selector (7 days, 30 days, etc.)
- Include threat trends over time graph
- Display threat type distribution pie chart
- Show top threat sources

**Tips:**
- Select a 30-day view for more data
- Make sure charts are colorful and populated
- Zoom out enough to show the full page

### 4. Alert Management (`alerts.png`)
**What to capture:**
- Alerts page with list of generated alerts
- Show different alert severities
- Include alert status (open, acknowledged, resolved)
- Display alert details or preview

**Tips:**
- Create multiple alerts with different priorities
- Show the alert creation modal if possible
- Include timestamps to show real-time updates

## How to Take Screenshots

### Option 1: Built-in Screenshot (Mac)
```bash
# Full screen
Cmd + Shift + 3

# Selected area
Cmd + Shift + 4

# Specific window
Cmd + Shift + 4, then Space, then click window
```

### Option 2: Browser Developer Tools
1. Open Chrome DevTools (F12)
2. Click the three dots menu
3. Select "Capture screenshot" or "Capture full size screenshot"

### Option 3: Use a Screenshot Tool
- **Mac**: Use Preview or Skitch
- **Windows**: Use Snipping Tool
- **Cross-platform**: Use Lightshot or ShareX

## After Taking Screenshots

1. Name files exactly as shown:
   - `dashboard.png`
   - `logs.png`
   - `analytics.png`
   - `alerts.png`

2. Save them in the `screenshots/` directory

3. Optimize images (optional):
   ```bash
   # Install imagemagick if needed
   brew install imagemagick
   
   # Resize to reasonable size (keeps aspect ratio)
   mogrify -resize 1920x1080\> screenshots/*.png
   ```

4. Commit and push:
   ```bash
   git add screenshots/
   git commit -m "docs: add application screenshots"
   git push
   ```

## Sample Data Generation

If you don't have enough data to show, run:

```bash
# Backend
cd backend
python -c "from app.services.threat_detector import ThreatDetector; ThreatDetector().train_model()"

# Or use the API to create sample logs
# (Create a script to POST to /api/logs endpoint)
```
