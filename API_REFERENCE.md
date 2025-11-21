# Aegis OS - Complete API Reference v3.0

## Base URL
```
http://localhost:5000
http://your-domain.com (production)
```

## Authentication
Header: `X-API-Key: your-api-key`

## Response Format
All responses are JSON with consistent structure:
```json
{
  "status": "ok|error",
  "data": {...},
  "timestamp": "2025-11-21T07:04:00Z",
  "code": "ERROR_CODE (if error)"
}
```

## Core Endpoints

### Health & Status
**GET /health**
- Description: Health check
- No auth required
- Response: `{status: "ok", version: "3.0"}`

**GET /api/v1/status**
- Description: Metrics and uptime
- No auth required
- Response: Metrics, uptime seconds, error rate

### Tier Management

**GET /api/v1/tiers**
- Description: Get all tiers
- Response: All 5 tiers with features, price, API limits
- Example: `{count: 5, tiers: {...}}`

**GET /api/v1/tier/basic**
- Description: Get specific tier
- Params: tier name (freemium|basic|gamer|ai-dev|server)
- Response: Tier details including features and price

### Authentication

**POST /api/v1/auth/register**
- Description: Register new user
- Body: `{email, password (min 8 chars)}`
- Response: `{user_id, email, tier: "freemium"}`
- Status: 201 Created

**POST /api/v1/auth/login**
- Description: User login
- Body: `{email, password}`
- Response: `{user_id, token, tier}`
- Status: 200 OK

### Automation

**POST /api/v1/automation/backup/schedule**
- Description: Schedule automated backup
- Auth: Required (API key)
- Body: `{frequency: "hourly|daily|weekly"}`
- Response: `{backup_id, status: "scheduled", next_run}`

**POST /api/v1/automation/monitoring/setup**
- Description: Setup automated monitoring
- Auth: Required (API key)
- Body: `{monitors: [...]}`
- Response: `{monitors_configured, status: "active"}`

**POST /api/v1/automation/deploy**
- Description: Trigger automated deployment
- Auth: Required (API key)
- Body: `{tier: "tier-name"}`
- Response: `{deployment_id, status: "initiated"}`

### Security

**GET /api/v1/security/audit**
- Description: Security audit status
- Auth: Required (API key)
- Response: `{audit_status: "passed", checks: {...}}`

**GET /api/v1/security/threats**
- Description: Threat detection status
- Auth: Required (API key)
- Response: `{threat_level: "LOW", threats_detected: 0}`

### Optimization

**POST /api/v1/optimization/cache**
- Description: Cache optimization settings
- Auth: Required (API key)
- Response: `{cache_enabled: true, ttl: 3600, hit_rate: "98.5%"}`

**GET /api/v1/optimization/performance**
- Description: Performance metrics
- Response: Response time, throughput, CPU/memory, optimization score

### Static Files

**GET /html/index.html**
- Description: Get HTML page

**GET /css/styles.css**
- Description: Get stylesheet

**GET /js/main.js**
- Description: Get JavaScript

**GET /assets/logo.svg**
- Description: Get asset

## Error Codes

```
200 - OK
201 - Created
400 - Bad Request (missing params, validation failed)
401 - Unauthorized (invalid API key)
403 - Forbidden (insufficient permissions)
404 - Not Found
429 - Rate Limit Exceeded
500 - Internal Server Error
```

## Rate Limits

Per-endpoint limits:
- Static assets: 1000 req/hour
- API endpoints: 100-500 req/hour
- Authentication: 50 req/hour
- Admin operations: 10 req/hour

Per-IP limits:
- 10,000 requests per hour

## Webhook Support

Future webhooks for:
- Payment completion
- License activation
- Deployment status
- Security alerts
- Monitoring updates

## Example Requests

**Get all tiers:**
```bash
curl http://localhost:5000/api/v1/tiers
```

**Register user:**
```bash
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"securepass123"}'
```

**Get health status:**
```bash
curl http://localhost:5000/health
```

**Schedule backup (auth required):**
```bash
curl -X POST http://localhost:5000/api/v1/automation/backup/schedule \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"frequency":"daily"}'
```

---

Complete API reference for Aegis OS promotional website and backend.
