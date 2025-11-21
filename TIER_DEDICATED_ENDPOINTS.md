# Tier-Dedicated API Endpoints

## Freemium (/api/v1/freemium)
- GET /status - System status
- GET /version - Current version

## Basic (/api/v1/basic)
- POST /security/scan - Run security scan
- GET /security/status - Security status
- POST /firewall/rules - Manage firewall
- GET /audit/log - View audit log
- POST /backup/create - Manual backup

## Gamer (/api/v1/gamer)
- GET /game/profiles - List game profiles
- POST /game/optimize - Optimize for game
- GET /latency/check - Check input latency
- POST /gpu/benchmark - GPU benchmark
- GET /performance/metrics - Performance stats

## AI Dev (/api/v1/ai-dev)
- POST /docker/start - Start Docker
- GET /jupyter/status - Jupyter status
- POST /model/train - Start model training
- GET /gpu/utilization - GPU stats
- POST /docker/deploy - Deploy container

## Server (/api/v1/server)
- POST /nginx/reload - Reload Nginx
- GET /postgresql/status - DB status
- POST /backup/schedule - Schedule backup
- GET /uptime/sla - SLA status
- POST /failover/test - Test failover
