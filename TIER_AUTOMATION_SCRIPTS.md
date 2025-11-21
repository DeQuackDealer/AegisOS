# Tier-Specific Automation Scripts

## Freemium Automation
```bash
aegis-cli backup --auto --frequency weekly
aegis-cli update --check
aegis-cli status --report json
```

## Basic Automation
```bash
aegis-cli security scan --scheduled daily
aegis-cli backup --auto --frequency daily
aegis-cli firewall --monitor
aegis-cli 2fa --setup
aegis-cli audit --report weekly
```

## Gamer Automation
```bash
aegis-cli game-mode --enable --monitor
aegis-cli performance --tune gpu
aegis-cli latency --check --alert <5ms
aegis-cli profiles --update steam
aegis-cli backup --auto --frequency daily
```

## AI Dev Automation
```bash
aegis-cli docker --start
aegis-cli jupyter --launch
aegis-cli gpu --monitor --alert
aegis-cli model --train --auto-scale
aegis-cli backup --auto --frequency hourly
aegis-cli dev-support --enable 24/7
```

## Server Automation
```bash
aegis-cli nginx --monitor --alert
aegis-cli postgresql --backup hourly
aegis-cli prometheus --scrape 15s
aegis-cli grafana --dashboard auto
aegis-cli patch --apply rebootless
aegis-cli sla --monitor 99.95%
aegis-cli failover --test weekly
```
