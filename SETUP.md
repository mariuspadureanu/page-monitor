# IBM Page Monitor - Setup Guide

Quick setup guide to get the monitor running in 5 minutes.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Excel file with URLs (`all-offerings-pages.xlsx`)
- Slack workspace (for notifications)
- Email account with OAuth2 support (Gmail, Office 365, or IBM Cloud)

## Step-by-Step Setup

### 1. Install Dependencies (2 minutes)

```bash
# Navigate to project directory
cd wm-agent

# Install Python packages
pip install -r requirements.txt

# Install Playwright browsers (for JavaScript-dependent pages)
playwright install chromium
```

### 2. Configure Slack Webhook (1 minute)

1. Go to https://api.slack.com/apps
2. Create a new app or select existing
3. Enable "Incoming Webhooks"
4. Add webhook to your desired channel
5. Copy the webhook URL (looks like: `https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXX`)

### 3. Configure Email OAuth2 (2 minutes)

**For Gmail:**

```bash
# Follow detailed instructions in OAUTH2_SETUP.md
# Quick summary:
# 1. Go to Google Cloud Console
# 2. Create OAuth2 credentials
# 3. Get refresh token using oauth2.py helper script
```

**For Office 365 or IBM Cloud:**
See `OAUTH2_SETUP.md` for provider-specific instructions.

### 4. Set Environment Variables (1 minute)

```bash
# Copy example file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your preferred editor
```

Required variables:

```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
EMAIL_PROVIDER=gmail
EMAIL_CLIENT_ID=your-client-id.apps.googleusercontent.com
EMAIL_CLIENT_SECRET=your-client-secret
EMAIL_REFRESH_TOKEN=your-refresh-token
EMAIL_FROM=monitor@example.com
EMAIL_TO=team@example.com
```

### 5. Verify Excel File

Ensure `all-offerings-pages.xlsx` is in the project root with:

- **Column A**: Offering name
- **Column B**: URL (required)
- **Column C-I**: Additional metadata (optional)
- **Row 1**: Headers
- **Row 2+**: Data

### 6. Test Configuration

```bash
# Test configuration validity
python -c "from src.config import get_config; config = get_config('config/config.yaml'); print('✓ Config valid')"

# Test database connection
python -c "import asyncio; from src.database import Database; asyncio.run(Database('data/monitor.db').connect()); print('✓ Database OK')"
```

### 7. Run First Scan

```bash
# Run a single scan (manual mode)
python run.py

# Expected output:
# ============================================================
# IBM Page Monitor initialized successfully
# ============================================================
# Starting scan: scan_20260617_120000
# Loading pages from Excel file...
# [1/231] Checking: https://www.ibm.com/...
# ...
# Scan scan_20260617_120000 completed successfully
#   Pages scanned: 231
#   Links checked: 4620
#   Images checked: 1155
#   Issues found: 12
#   New issues: 12
# ============================================================
```

### 8. Check Results

```bash
# View logs
tail -f logs/monitor.log

# Check database
sqlite3 data/monitor.db "SELECT * FROM issues WHERE status='active';"

# View Slack notifications
# Check your configured Slack channel

# Check email
# Look for "IBM Page Monitor - Daily Summary" in your inbox
```

### 9. Enable Scheduler (Optional)

```bash
# Run with scheduler (continuous mode)
python run.py --schedule

# Or run in background
nohup python run.py --schedule > /dev/null 2>&1 &

# Check if running
ps aux | grep "python run.py"
```

### 10. Docker Deployment (Optional)

```bash
# Build and run with Docker
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Verification Checklist

- [ ] Python 3.8+ installed
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Playwright browsers installed (`playwright install chromium`)
- [ ] `.env` file created with all required variables
- [ ] Slack webhook URL configured and tested
- [ ] Email OAuth2 credentials configured
- [ ] Excel file present with correct format
- [ ] First scan completed successfully
- [ ] Slack notification received
- [ ] Email summary received
- [ ] Database created (`data/monitor.db`)
- [ ] Logs directory created (`logs/`)

## Common Issues

### Issue: "ModuleNotFoundError: No module named 'src'"

**Solution**: Run from project root directory:

```bash
cd wm-agent
python run.py
```

### Issue: "FileNotFoundError: all-offerings-pages.xlsx"

**Solution**: Place Excel file in project root or update path in `config/config.yaml`:

```yaml
excel:
  file_path: "/path/to/your/file.xlsx"
```

### Issue: "Slack webhook failed"

**Solution**: Test webhook manually:

```bash
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test message"}' \
  YOUR_WEBHOOK_URL
```

### Issue: "Email authentication failed"

**Solution**: Regenerate OAuth2 refresh token. See `OAUTH2_SETUP.md` section 4.

### Issue: "Permission denied: data/monitor.db"

**Solution**: Create data directory with write permissions:

```bash
mkdir -p data
chmod 755 data
```

## Configuration Tips

### Adjust Scan Frequency

Edit `config/config.yaml`:

```yaml
scheduler:
  interval_hours: 12 # Run every 12 hours instead of 24
  start_time: "02:00" # Start at 2 AM
```

### Reduce False Positives

Increase confidence threshold:

```yaml
verification:
  confidence_threshold: 90 # Default is 80
```

### Speed Up Scans

Increase concurrency (if servers allow):

```yaml
scraping:
  concurrent_pages: 20 # Default is 10
  concurrent_links: 50 # Default is 20
```

### Reduce Server Load

Decrease rate limits:

```yaml
scraping:
  rate_limit:
    requests_per_second: 20 # Default is 50
    per_domain_limit: 2 # Default is 5
```

## Next Steps

1. **Monitor First Week**: Watch for false positives and adjust thresholds
2. **Review Statistics**: Check daily/weekly reports for trends
3. **Optimize Configuration**: Tune settings based on results
4. **Set Up Alerts**: Configure additional notification channels if needed
5. **Schedule Maintenance**: Plan for log rotation and database cleanup

## Support

- **Documentation**: See `README.md` for detailed information
- **OAuth2 Setup**: See `OAUTH2_SETUP.md` for email configuration
- **Issues**: Create an issue in the repository
- **Questions**: Contact the development team

## Quick Reference

### Start/Stop Commands

```bash
# Manual scan
python run.py

# Scheduled mode
python run.py --schedule

# Custom config
python run.py --config /path/to/config.yaml

# Docker
docker-compose up -d      # Start
docker-compose logs -f    # View logs
docker-compose down       # Stop
```

### Log Files

```bash
# Main log
tail -f logs/monitor.log

# Performance log
tail -f logs/performance.log

# Scan-specific log
tail -f logs/scan_20260617_120000.log
```

### Database Queries

```bash
# Active issues
sqlite3 data/monitor.db "SELECT * FROM issues WHERE status='active';"

# Recent scans
sqlite3 data/monitor.db "SELECT * FROM scans ORDER BY start_time DESC LIMIT 5;"

# Statistics
sqlite3 data/monitor.db "SELECT * FROM statistics ORDER BY date DESC LIMIT 7;"
```

### Health Check

```bash
# Check if running
ps aux | grep "python run.py"

# Check last scan
sqlite3 data/monitor.db "SELECT * FROM scans ORDER BY start_time DESC LIMIT 1;"

# Check disk space
du -sh data/ logs/
```

## Maintenance

### Log Rotation

Logs are automatically rotated when they reach 10 MB. Old logs are kept for 30 days.

### Database Cleanup

```bash
# Remove old resolved issues (older than 90 days)
sqlite3 data/monitor.db "DELETE FROM issues WHERE status='resolved' AND resolved_at < datetime('now', '-90 days');"

# Vacuum database
sqlite3 data/monitor.db "VACUUM;"
```

### Backup

```bash
# Backup database
cp data/monitor.db data/monitor.db.backup

# Backup configuration
tar -czf config-backup.tar.gz config/ .env
```

## Production Deployment

### Systemd Service (Linux)

Create `/etc/systemd/system/ibm-page-monitor.service`:

```ini
[Unit]
Description=IBM Page Monitor
After=network.target

[Service]
Type=simple
User=monitor
WorkingDirectory=/opt/wm-agent
ExecStart=/usr/bin/python3 run.py --schedule
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable ibm-page-monitor
sudo systemctl start ibm-page-monitor
sudo systemctl status ibm-page-monitor
```

### Monitoring

Set up monitoring for:

- Process health (systemd, Docker)
- Disk space (logs, database)
- Scan completion (check last scan time)
- Notification delivery (Slack, email)

---

**Setup complete!** The monitor is now ready to scan 231 IBM pages every 24 hours and alert you to any issues.
