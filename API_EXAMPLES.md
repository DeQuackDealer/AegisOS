# Aegis OS - Complete API Examples

## Authentication API

### Register User
```bash
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!"
  }'
```

Response:
```json
{
  "user_id": "uuid-123",
  "email": "user@example.com",
  "api_token": "token-hash"
}
```

### Login User
```bash
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!"
  }'
```

## Licensing API

### Validate License Key
```bash
curl -X POST http://localhost:5000/api/v1/license/validate \
  -H "Content-Type: application/json" \
  -d '{"key": "AEGIS-BASIC-2024-A1B2C3D4E5F6"}'
```

Response:
```json
{
  "valid": true,
  "tier": "basic",
  "price": 49,
  "features": ["security", "ai_detection", "firewall", "priority_support"],
  "expires": "2025-12-31"
}
```

### Get All Tiers
```bash
curl http://localhost:5000/api/v1/tiers
```

### Get Specific Tier
```bash
curl http://localhost:5000/api/v1/tier/basic
```

## Payment API

### Initiate Payment
```bash
curl -X POST http://localhost:5000/api/v1/payment/initiate \
  -H "Content-Type: application/json" \
  -d '{
    "tier": "basic",
    "email": "user@example.com"
  }'
```

Response:
```json
{
  "status": "ready_for_payment",
  "tier": "basic",
  "amount": 49,
  "currency": "USD",
  "payment_method": "stripe"
}
```

### Verify Payment
```bash
curl -X POST http://localhost:5000/api/v1/payment/verify \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "pi_3Kx1234567890",
    "tier": "basic"
  }'
```

Response:
```json
{
  "verified": true,
  "license_key": "AEGIS-BASIC-2024-A1B2C3D4E5F6",
  "message": "Payment verified. Use license key to activate."
}
```

## Webhook API

### Register Webhook
```bash
curl -X POST http://localhost:5000/api/v1/webhooks/register \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://yourapp.com/webhooks/aegis",
    "events": ["payment.completed", "license.activated", "security.threat_detected"]
  }'
```

### List Webhooks
```bash
curl http://localhost:5000/api/v1/webhooks \
  -H "X-API-Key: your-api-key"
```

### Delete Webhook
```bash
curl -X DELETE http://localhost:5000/api/v1/webhooks/webhook-id \
  -H "X-API-Key: your-api-key"
```

## Analytics API

### Get Dashboard
```bash
curl http://localhost:5000/api/v1/analytics/dashboard \
  -H "X-API-Key: your-api-key" \
  -H "X-User-ID: admin-user-id"
```

Response:
```json
{
  "downloads": 10247,
  "activations": 1823,
  "errors": 12,
  "active_users": 1823,
  "uptime_percent": 99.95,
  "avg_response_time_ms": 145
}
```

### Get Audit Log
```bash
curl http://localhost:5000/api/v1/analytics/audit?limit=50 \
  -H "X-API-Key: your-api-key" \
  -H "X-User-ID: admin-user-id"
```

## Backup API

### Schedule Backup
```bash
curl -X POST http://localhost:5000/api/v1/backup/schedule \
  -H "X-API-Key: your-api-key" \
  -H "X-User-ID: admin-user-id" \
  -H "Content-Type: application/json" \
  -d '{
    "schedule": "daily",
    "retention_days": 30
  }'
```

### List Backups
```bash
curl http://localhost:5000/api/v1/backup/list \
  -H "X-API-Key: your-api-key" \
  -H "X-User-ID: admin-user-id"
```

## Marketplace API

### List Available Apps
```bash
curl http://localhost:5000/api/v1/marketplace/apps
```

Response:
```json
{
  "apps": [
    {
      "id": "app-001",
      "name": "VSCode Integration",
      "version": "1.0.0",
      "downloads": 1250,
      "rating": 4.8,
      "price": 0
    },
    {
      "id": "app-002",
      "name": "Advanced Profiler",
      "version": "1.0.0",
      "downloads": 845,
      "rating": 4.9,
      "price": 29.99
    }
  ]
}
```

### Install App
```bash
curl -X POST http://localhost:5000/api/v1/marketplace/app/app-001/install \
  -H "X-API-Key: your-api-key"
```

## Security API

### Check Security Status
```bash
curl http://localhost:5000/api/v1/security/check
```

Response:
```json
{
  "system_secure": true,
  "threat_level": "LOW",
  "last_scan": "2025-11-21T10:30:00Z",
  "features": {
    "real_time_scanning": true,
    "ai_threat_detection": true,
    "firewall": true,
    "file_integrity": true,
    "network_monitoring": true
  }
}
```

## System API

### Get System Status
```bash
curl http://localhost:5000/api/v1/system/status
```

### Get System Health
```bash
curl http://localhost:5000/api/v1/system/health
```

Response:
```json
{
  "status": "healthy",
  "components": {
    "api": "ok",
    "database": "ok",
    "cache": "ok",
    "security_scanner": "ok",
    "ai_engine": "ok",
    "firewall": "ok"
  },
  "uptime_percent": 99.95,
  "error_rate_percent": 0.05
}
```

### Get Rate Limit Status
```bash
curl http://localhost:5000/api/v1/rate-limit/status \
  -H "X-API-Key: your-api-key"
```

Response:
```json
{
  "limit": 1000,
  "remaining": 987,
  "reset": "2025-11-21T11:30:00Z",
  "plan": "pro"
}
```

## Error Responses

### Bad Request
```json
{
  "error": "Invalid tier"
}
```

### Unauthorized
```json
{
  "error": "Unauthorized"
}
```

### Not Found
```json
{
  "error": "Tier not found"
}
```

---

**Aegis OS API v2.0 - 30+ Endpoints, Production Ready**
