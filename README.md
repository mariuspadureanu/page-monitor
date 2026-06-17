# IBM Page Monitor

Automated monitoring agent for IBM web pages that detects broken links, images, and redirects.

## Features

- **Comprehensive Link Checking**: Validates all links and images on monitored pages
- **Multi-stage Verification**: 4-stage validation process to prevent false positives
- **Smart Notifications**: Slack alerts for immediate issues, email summaries for daily/weekly/monthly reports
- **Deduplication**: Only alerts on NEW issues, not recurring ones
- **Retry Strategies**: Intelligent retry logic for different HTTP error codes
- **Rate Limiting**: Respects server limits with configurable rate limiting
- **OAuth2 Authentication**: Secure email authentication (Gmail, Office 365, IBM Cloud)
- **Statistics & Reporting**: Comprehensive analytics and health scoring
- **Scheduler**: Automated 24-hour scanning intervals
- **Browser Fallback**: Playwright integration for JavaScript-dependent resources

## Quick Start

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers (for JavaScript-dependent pages)
playwright install chromium
```

### 2. Configure

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
# - Slack webhook URL
# - Email OAuth2 credentials (see OAUTH2_SETUP.md)

# Review and customize config/config.yaml
# - Adjust verification thresholds
# - Configure notification preferences
# - Set scheduler timing
```

### 3. Prepare Excel File

Place your `all-offerings-pages.xlsx` file in the project root with:

- Column A: Offering name
- Column B: URL (required)
- Column C-I: Additional metadata (optional)

### 4. Run

```bash
# Run a single scan (manual mode)
python run.py

# Run with scheduler (continuous mode - recommended for production)
python run.py --schedule

# Use custom config file
python run.py --config /path/to/config.yaml
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     IBM Page Monitor                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────┐                     │
│  │  Scheduler   │─────▶│ Main         │                     │
│  │  (24h cycle) │      │ Orchestrator │                     │
│  └──────────────┘      └──────┬───────┘                     │
│                               │                              │
│                               ▼                              │
│                    ┌──────────────────┐                     │
│                    │   URL Parser     │                     │
│                    │  (Excel Reader)  │                     │
│                    └────────┬─────────┘                     │
│                             │                               │
│                             ▼                               │
│                    ┌──────────────────┐                     │
│                    │   Web Scraper    │                     │
│                    │  (Async HTTP)    │                     │
│                    └────────┬─────────┘                     │
│                             │                               │
│                             ▼                               │
│                    ┌──────────────────┐                     │
│                    │  Link Validator  │                     │
│                    │  (4-stage check) │                     │
│                    └────────┬─────────┘                     │
│                             │                               │
│                    ┌────────┴─────────┐                     │
│                    ▼                  ▼                     │
│           ┌─────────────┐    ┌──────────────┐              │
│           │  Database   │    │  Notifier    │              │
│           │  (SQLite)   │    │ (Slack/Email)│              │
│           └─────────────┘    └──────────────┘              │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## Components

### 1. Main Orchestrator (`src/main.py`)

- Coordinates all modules
- Manages scan lifecycle
- Handles graceful shutdown
- CLI interface

### 2. Configuration (`src/config.py`)

- YAML-based configuration
- Environment variable substitution
- Validation and defaults

### 3. Database (`src/database.py`)

- SQLite with async support
- Issue tracking and deduplication
- Statistics storage
- Page metadata

### 4. URL Parser (`src/url_parser.py`)

- Excel file parsing
- URL extraction and validation
- Metadata extraction

### 5. Web Scraper (`src/scraper.py`)

- Async HTTP requests
- Rate limiting (global + per-domain)
- User-Agent rotation
- Retry strategies

### 6. Link Validator (`src/validator.py`)

- 4-stage verification:
  1. HEAD request (fast check)
  2. GET request (full check)
  3. Browser rendering (JavaScript)
  4. Confidence scoring
- False positive prevention

### 7. Notifier (`src/notifier.py`)

- Slack webhooks (immediate alerts)
- Email with OAuth2 (summaries)
- Smart deduplication

### 8. Scheduler (`src/scheduler.py`)

- APScheduler integration
- Configurable intervals
- Timezone support

### 9. Logger (`src/logger.py`)

- Colored console output
- File rotation
- Performance tracking
- Scan-specific logs

### 10. Statistics (`src/statistics.py`)

- Daily/weekly/monthly reports
- Health scoring (0-100)
- Trend analysis

## Configuration

### Main Config (`config/config.yaml`)

```yaml
# Excel file settings
excel:
  file_path: "all-offerings-pages.xlsx"
  sheet_name: "Pages"
  url_column: "B"
  start_row: 2

# Scraping settings
scraping:
  timeout: 30
  max_retries: 3
  concurrent_pages: 10
  concurrent_links: 20
  rate_limit:
    requests_per_second: 50
    per_domain_limit: 5

# Verification settings
verification:
  confidence_threshold: 80
  enable_browser_fallback: true
  browser_timeout: 30

# Notifications
notifications:
  slack:
    enabled: true
    webhook_url: "${SLACK_WEBHOOK_URL}"
  email:
    enabled: true
    provider: "gmail" # or "office365", "ibm_cloud"
    send_daily_summary: true
    send_weekly_report: true
    send_monthly_report: true

# Scheduler
scheduler:
  enabled: true
  interval_hours: 24
  start_time: "02:00"
  timezone: "UTC"
```

### Environment Variables (`.env`)

```bash
# Slack
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Email OAuth2 (see OAUTH2_SETUP.md for setup instructions)
EMAIL_PROVIDER=gmail
EMAIL_CLIENT_ID=your-client-id
EMAIL_CLIENT_SECRET=your-client-secret
EMAIL_REFRESH_TOKEN=your-refresh-token
EMAIL_FROM=monitor@example.com
EMAIL_TO=team@example.com
```

## Usage Examples

### Manual Scan

```bash
# Run once and exit
python run.py --once

# View logs in real-time
tail -f logs/monitor.log
```

### Scheduled Operation

```bash
# Start scheduler (runs every 24 hours)
python run.py --schedule

# Run in background
nohup python run.py --schedule > /dev/null 2>&1 &

# Check status
ps aux | grep "python run.py"
```

### Docker Deployment

```bash
# Build image
docker-compose build

# Run once
docker-compose run --rm monitor

# Run scheduled
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Custom Configuration

```bash
# Use different config file
python run.py --config config/production.yaml

# Override specific settings
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/NEW/URL"
python run.py
```

## Notifications

### Slack Alerts (Immediate)

Sent when NEW issues are detected:

- Broken links (404, 410)
- Server errors (500, 502, 503)
- Redirects (301, 302, 307, 308)
- Broken images
- Confidence score and verification details

### Email Summaries

**Daily Summary** (every day):

- Total active issues
- Issues by type
- Top affected pages
- Health score trends

**Weekly Report** (Monday):

- Week-over-week comparison
- New vs resolved issues
- Performance metrics
- Detailed issue list

**Monthly Report** (1st of month):

- Month-over-month trends
- Long-term statistics
- Health score history
- Recommendations

## Database Schema

### Tables

1. **pages** - Monitored pages
2. **issues** - Detected issues with deduplication
3. **scans** - Scan history and statistics
4. **statistics** - Daily/weekly/monthly aggregates
5. **notifications** - Notification history
6. **page_health** - Health scores over time

### Queries

```python
# Get active issues
active_issues = await db.get_active_issues()

# Get page health
health = await db.get_page_health(page_id)

# Get statistics
stats = await db.get_daily_statistics(date)
```

## Troubleshooting

### Issue: False Positives

**Solution**: Adjust confidence threshold in `config.yaml`:

```yaml
verification:
  confidence_threshold: 90 # Increase for fewer false positives
```

### Issue: Rate Limiting (429 errors)

**Solution**: Reduce request rate:

```yaml
scraping:
  rate_limit:
    requests_per_second: 20 # Reduce from 50
    per_domain_limit: 2 # Reduce from 5
```

### Issue: Timeouts

**Solution**: Increase timeout values:

```yaml
scraping:
  timeout: 60 # Increase from 30
verification:
  browser_timeout: 60 # Increase from 30
```

### Issue: OAuth2 Email Errors

**Solution**: See `OAUTH2_SETUP.md` for detailed setup instructions. Common issues:

- Expired refresh token (regenerate)
- Incorrect client credentials
- Missing API permissions

### Issue: Memory Usage

**Solution**: Reduce concurrency:

```yaml
scraping:
  concurrent_pages: 5 # Reduce from 10
  concurrent_links: 10 # Reduce from 20
```

## Development

### Project Structure

```
wm-agent/
├── src/
│   ├── __init__.py
│   ├── main.py              # Main orchestrator
│   ├── config.py            # Configuration management
│   ├── database.py          # Database operations
│   ├── url_parser.py        # Excel parser
│   ├── scraper.py           # Web scraper
│   ├── validator.py         # Link validator
│   ├── notifier.py          # Notifications
│   ├── email_oauth2.py      # OAuth2 authentication
│   ├── scheduler.py         # Scheduler
│   ├── logger.py            # Logging
│   └── statistics.py        # Statistics generator
├── config/
│   └── config.yaml          # Main configuration
├── data/
│   └── monitor.db           # SQLite database
├── logs/                    # Log files
├── all-offerings-pages.xlsx # Input file
├── requirements.txt         # Python dependencies
├── run.py                   # CLI entry point
├── Dockerfile               # Docker image
├── docker-compose.yml       # Docker Compose
├── README.md                # This file
└── OAUTH2_SETUP.md          # OAuth2 setup guide
```

### Adding New Features

1. **New Issue Type**: Add to `IssueType` enum in `validator.py`
2. **New Notification Channel**: Extend `Notifier` class in `notifier.py`
3. **New Statistics**: Add methods to `StatisticsGenerator` in `statistics.py`

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run tests
pytest tests/

# With coverage
pytest --cov=src tests/
```

## Performance

### Benchmarks (231 pages)

- **Scan Duration**: ~15-20 minutes
- **Memory Usage**: ~200-300 MB
- **Database Size**: ~10-50 MB (depends on history)
- **Log Files**: ~5-10 MB per day

### Optimization Tips

1. **Increase Concurrency** (if server allows):

   ```yaml
   scraping:
     concurrent_pages: 20
     concurrent_links: 50
   ```

2. **Disable Browser Fallback** (if not needed):

   ```yaml
   verification:
     enable_browser_fallback: false
   ```

3. **Reduce Verification Stages**:
   ```yaml
   verification:
     skip_head_request: true # Go straight to GET
   ```

## Security

- **OAuth2**: No password storage, token-based authentication
- **Environment Variables**: Sensitive data in `.env` (not committed)
- **Rate Limiting**: Prevents overwhelming target servers
- **User-Agent**: Identifies bot for transparency

## License

IBM Internal Use Only

## Support

For issues or questions:

- Create an issue in the repository
- Contact the development team
- See `OAUTH2_SETUP.md` for OAuth2 help

## Changelog

### v1.0.0 (2026-06-17)

- Initial release
- 231 pages monitoring
- Multi-stage verification
- Slack + Email notifications
- Daily/weekly/monthly reports
- OAuth2 authentication
- Docker support
