# Aegis OS - Complete Testing Guide

## API Testing

### Test Authentication
```bash
# Register
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}'

# Login
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}'

# Enable 2FA
curl -X POST http://localhost:5000/api/v1/user/2fa/enable \
  -H "X-API-Key: test-key" \
  -H "X-User-ID: user-123"
```

### Test Licensing
```bash
# Validate license
curl -X POST http://localhost:5000/api/v1/license/validate \
  -H "Content-Type: application/json" \
  -d '{"key":"AEGIS-BASIC-2024-A1B2C3D4E5F6"}'

# Get tiers
curl http://localhost:5000/api/v1/tiers

# Get specific tier
curl http://localhost:5000/api/v1/tier/basic
```

### Test Payments
```bash
# Initiate payment
curl -X POST http://localhost:5000/api/v1/payment/initiate \
  -H "Content-Type: application/json" \
  -d '{"tier":"basic","email":"user@example.com"}'

# Verify payment
curl -X POST http://localhost:5000/api/v1/payment/verify \
  -H "Content-Type: application/json" \
  -d '{"transaction_id":"pi_test123","tier":"basic"}'
```

### Test Webhooks
```bash
# Register webhook
curl -X POST http://localhost:5000/api/v1/webhooks/register \
  -H "X-API-Key: test-key" \
  -H "Content-Type: application/json" \
  -d '{
    "url":"https://example.com/webhook",
    "events":["payment.completed","license.activated"]
  }'

# List webhooks
curl http://localhost:5000/api/v1/webhooks \
  -H "X-API-Key: test-key"

# Delete webhook
curl -X DELETE http://localhost:5000/api/v1/webhooks/webhook-id \
  -H "X-API-Key: test-key"
```

### Test Analytics
```bash
# Get dashboard
curl http://localhost:5000/api/v1/analytics/dashboard \
  -H "X-API-Key: test-key" \
  -H "X-User-ID: admin-user"

# Get audit log
curl http://localhost:5000/api/v1/analytics/audit?limit=50 \
  -H "X-API-Key: test-key" \
  -H "X-User-ID: admin-user"
```

## Performance Testing

### Load Test with Apache Bench
```bash
# 1000 requests, 10 concurrent
ab -n 1000 -c 10 http://localhost:5000/

# API endpoint
ab -n 1000 -c 10 -H "X-API-Key: test" http://localhost:5000/api/v1/tiers
```

### Load Test with wrk
```bash
# Install wrk
git clone https://github.com/wg/wrk.git
cd wrk
make

# Run test
./wrk -t4 -c100 -d30s http://localhost:5000/api/v1/tiers

# With custom script
./wrk -t4 -c100 -d30s -s script.lua http://localhost:5000/
```

### Load Test with Locust
```python
from locust import HttpUser, task, between

class AegisUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def get_tiers(self):
        self.client.get("/api/v1/tiers")
    
    @task
    def validate_license(self):
        self.client.post("/api/v1/license/validate", 
            json={"key": "AEGIS-BASIC-2024-TEST"})
```

## Security Testing

### SQLi Testing
```bash
# Should return 400 error
curl -X POST http://localhost:5000/api/v1/auth/login \
  -d '{"email":"test@example.com' OR '1'='1","password":"x"}'
```

### XSS Testing
```bash
# Should sanitize input
curl -X POST http://localhost:5000/api/v1/auth/register \
  -d '{"email":"<script>alert(1)</script>","password":"test"}'
```

### Rate Limiting
```bash
# Should get 429 after 1000 requests
for i in {1..1100}; do
  curl http://localhost:5000/api/v1/tiers \
    -H "X-API-Key: test-key"
done
```

## Integration Testing

### Test Payment Flow
1. Register user
2. Get available tiers
3. Initiate payment
4. Verify payment
5. Check license issued
6. Validate license

### Test Webhook Flow
1. Register webhook
2. Trigger event (payment)
3. Verify webhook called
4. Check webhook logs
5. Delete webhook

### Test Backup Flow
1. Schedule backup
2. Create manual backup
3. List backups
4. Verify backup exists
5. Restore from backup

## Unit Tests (Python)

```python
import unittest
from aegis_promotional.server import app

class TestAegisAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
    
    def test_get_tiers(self):
        response = self.app.get('/api/v1/tiers')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('tiers', data)
    
    def test_validate_invalid_license(self):
        response = self.app.post('/api/v1/license/validate',
            json={'key': 'invalid'})
        self.assertEqual(response.status_code, 401)
    
    def test_payment_missing_email(self):
        response = self.app.post('/api/v1/payment/initiate',
            json={'tier': 'basic'})
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()
```

## End-to-End Tests

### Test Tier Selection Flow
1. Visit website
2. View all tiers
3. Select "Basic" tier
4. Click "Get Started"
5. Fill registration form
6. Submit payment
7. Verify license issued
8. Login to dashboard
9. Verify license active

### Test Admin Dashboard
1. Login as admin
2. View analytics
3. Check metrics accuracy
4. View user list
5. View payment history
6. Check system health
7. Verify audit log

## Browser Testing

### Chrome DevTools
```javascript
// Test API
fetch('/api/v1/tiers')
  .then(r => r.json())
  .then(d => console.log(d))

// Test auth
fetch('/api/v1/auth/register', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    email: 'test@example.com',
    password: 'Test123!'
  })
}).then(r => r.json()).then(d => console.log(d))
```

### Lighthouse Audit
```bash
# Install
npm install -g lighthouse

# Run audit
lighthouse http://localhost:5000 --chrome-flags="--headless"
```

## Performance Benchmarks

### Target Metrics
- API response time: < 150ms (p95)
- Database query time: < 50ms (p95)
- Page load time: < 2s
- Time to Interactive: < 3s
- Lighthouse score: > 90

### Measure Response Time
```bash
# Using curl
curl -w "Total time: %{time_total}s\n" http://localhost:5000/api/v1/tiers

# Using Apache Bench
ab -n 100 http://localhost:5000/api/v1/tiers
```

## Continuous Integration

### GitHub Actions Example
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: pytest
      - run: ab -n 100 http://localhost:5000/
```

## Test Checklist

- [ ] Authentication works (register, login, 2FA)
- [ ] Licensing validation works
- [ ] Payment flow works end-to-end
- [ ] Webhooks trigger on events
- [ ] Analytics dashboard shows real data
- [ ] Backup scheduling works
- [ ] Marketplace apps install correctly
- [ ] Admin panel has correct permissions
- [ ] All 30+ API endpoints respond
- [ ] Rate limiting works
- [ ] Error handling is comprehensive
- [ ] Performance meets targets
- [ ] Security vulnerabilities checked
- [ ] Database queries optimized
- [ ] Cache is working
- [ ] Logs are being written
- [ ] Backups are being created
- [ ] All SDKs work correctly

---

**Aegis OS Testing Guide - Complete**
