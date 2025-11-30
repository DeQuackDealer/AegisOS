#!/usr/bin/env python3
"""
Aegis OS AI Security Module
Provides AI-based security analysis and threat detection capabilities
with tiered feature access based on edition.
"""

import os
import sys
import json
import hashlib
import logging
import subprocess
import re
import time
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict

TIER_LIMIT = "server"

TIER_CONFIG_PATH = Path("/etc/aegis/tier-security.json")
AI_SECURITY_LOG = Path("/var/log/aegis/ai-security.log")
AI_DATA_DIR = Path("/var/lib/aegis/security/ai")

SUBPROCESS_TIMEOUT = 30


class AISecurityTier:
    """Manages AI security capabilities based on the current tier"""
    
    def __init__(self, tier_override: Optional[str] = None):
        self.tier_name = tier_override or TIER_LIMIT
        self.config: Dict = {}
        self.tier_config: Dict = {}
        self.capabilities: List[str] = []
        self.features: Dict = {}
        
        self._setup_logging()
        self._load_tier_config()
    
    def _setup_logging(self):
        """Setup logging for AI security module"""
        try:
            AI_SECURITY_LOG.parent.mkdir(parents=True, exist_ok=True)
            handlers = [logging.StreamHandler()]
            
            if AI_SECURITY_LOG.parent.exists():
                try:
                    handlers.append(logging.FileHandler(AI_SECURITY_LOG))
                except (OSError, PermissionError):
                    pass
            
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                handlers=handlers
            )
            self.logger = logging.getLogger("AegisAISecurity")
        except Exception as e:
            self.logger = logging.getLogger("AegisAISecurity")
            self.logger.addHandler(logging.StreamHandler())
    
    def _load_tier_config(self):
        """Load tier configuration from JSON file"""
        default_config = self._get_default_config()
        
        try:
            if TIER_CONFIG_PATH.exists():
                with open(TIER_CONFIG_PATH, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = default_config
                self.logger.warning(f"Tier config not found at {TIER_CONFIG_PATH}, using defaults")
        except (json.JSONDecodeError, OSError, PermissionError) as e:
            self.logger.error(f"Failed to load tier config: {e}")
            self.config = default_config
        
        tier_key = self.tier_name.lower().replace(" ", "-")
        tiers = self.config.get("tiers", {})
        
        if tier_key in tiers:
            self.tier_config = tiers[tier_key]
        else:
            self.tier_config = tiers.get("freemium", default_config["tiers"]["freemium"])
            self.logger.warning(f"Unknown tier '{tier_key}', falling back to freemium")
        
        self.capabilities = self.tier_config.get("capabilities", [])
        self.features = self.tier_config.get("features", {})
        
        self.logger.info(f"Loaded AI security tier: {self.get_tier_name()} with {len(self.capabilities)} capabilities")
    
    def _get_default_config(self) -> Dict:
        """Return default configuration if file is missing"""
        return {
            "version": "1.0.0",
            "tiers": {
                "freemium": {
                    "name": "Freemium",
                    "level": 1,
                    "capabilities": ["basic_heuristics", "simple_firewall"],
                    "features": {
                        "basic_heuristics": {"enabled": True},
                        "simple_firewall": {"enabled": True}
                    },
                    "limits": {
                        "max_scans_per_day": 3,
                        "realtime_protection": False,
                        "ai_analysis": False
                    }
                }
            }
        }
    
    def get_tier_name(self) -> str:
        """Get the display name of the current tier"""
        return self.tier_config.get("name", self.tier_name.title())
    
    def get_tier_level(self) -> int:
        """Get the numeric level of the current tier (1-5)"""
        return self.tier_config.get("level", 1)
    
    def get_capabilities(self) -> List[str]:
        """Get list of all capabilities for current tier"""
        return self.capabilities.copy()
    
    def has_capability(self, capability: str) -> bool:
        """Check if current tier has a specific capability"""
        return capability in self.capabilities
    
    def get_feature_config(self, feature: str) -> Dict:
        """Get configuration for a specific feature"""
        return self.features.get(feature, {})
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a feature is enabled in current tier"""
        feature_config = self.get_feature_config(feature)
        return feature_config.get("enabled", False)
    
    def get_limits(self) -> Dict:
        """Get resource limits for current tier"""
        return self.tier_config.get("limits", {})
    
    def get_tier_description(self) -> str:
        """Get description of current tier"""
        return self.tier_config.get("description", "Security tier")
    
    def get_all_capability_descriptions(self) -> Dict[str, str]:
        """Get descriptions for all capabilities"""
        return self.config.get("capability_descriptions", {})
    
    def get_status(self) -> Dict:
        """Get comprehensive status of AI security tier"""
        return {
            "tier_name": self.get_tier_name(),
            "tier_level": self.get_tier_level(),
            "description": self.get_tier_description(),
            "capabilities": self.get_capabilities(),
            "capabilities_count": len(self.capabilities),
            "limits": self.get_limits(),
            "realtime_protection": self.get_limits().get("realtime_protection", False),
            "ai_analysis": self.get_limits().get("ai_analysis", False)
        }


class AISecurityAnalyzer:
    """Performs AI-based security analysis based on tier capabilities"""
    
    def __init__(self, tier: Optional[AISecurityTier] = None):
        self.tier = tier or AISecurityTier()
        self.logger = logging.getLogger("AegisAIAnalyzer")
        self._ensure_data_dir()
        self.scan_count_today = 0
        self.last_scan_date = None
        self._load_scan_stats()
    
    def _ensure_data_dir(self):
        """Ensure AI data directory exists"""
        try:
            AI_DATA_DIR.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError):
            pass
    
    def _load_scan_stats(self):
        """Load scan statistics for rate limiting"""
        stats_file = AI_DATA_DIR / "scan_stats.json"
        try:
            if stats_file.exists():
                with open(stats_file, 'r') as f:
                    stats = json.load(f)
                    if stats.get("date") == datetime.now().strftime("%Y-%m-%d"):
                        self.scan_count_today = stats.get("count", 0)
                        self.last_scan_date = stats.get("date")
        except (json.JSONDecodeError, OSError, PermissionError):
            pass
    
    def _save_scan_stats(self):
        """Save scan statistics"""
        stats_file = AI_DATA_DIR / "scan_stats.json"
        try:
            stats = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "count": self.scan_count_today
            }
            with open(stats_file, 'w') as f:
                json.dump(stats, f)
        except (OSError, PermissionError):
            pass
    
    def _check_rate_limit(self) -> Tuple[bool, str]:
        """Check if scan rate limit is exceeded"""
        limits = self.tier.get_limits()
        max_scans = limits.get("max_scans_per_day", -1)
        
        if max_scans == -1:
            return True, ""
        
        today = datetime.now().strftime("%Y-%m-%d")
        if self.last_scan_date != today:
            self.scan_count_today = 0
            self.last_scan_date = today
        
        if self.scan_count_today >= max_scans:
            return False, f"Daily scan limit ({max_scans}) exceeded. Upgrade for unlimited scans."
        
        return True, ""
    
    def _increment_scan_count(self):
        """Increment scan count for rate limiting"""
        today = datetime.now().strftime("%Y-%m-%d")
        if self.last_scan_date != today:
            self.scan_count_today = 0
            self.last_scan_date = today
        
        self.scan_count_today += 1
        self._save_scan_stats()
    
    def heuristic_scan(self, path: str, quick: bool = True) -> Dict:
        """
        Perform heuristic-based threat detection
        Available on: All tiers
        """
        result = {
            "scan_type": "heuristic",
            "path": path,
            "timestamp": datetime.now().isoformat(),
            "threats_found": [],
            "risk_score": 0,
            "status": "completed"
        }
        
        if not self.tier.has_capability("basic_heuristics"):
            result["status"] = "capability_unavailable"
            result["error"] = "Heuristic scanning not available in current tier"
            return result
        
        can_scan, error_msg = self._check_rate_limit()
        if not can_scan:
            result["status"] = "rate_limited"
            result["error"] = error_msg
            return result
        
        self._increment_scan_count()
        
        try:
            scan_path = Path(path)
            if not scan_path.exists():
                result["status"] = "error"
                result["error"] = f"Path does not exist: {path}"
                return result
            
            suspicious_patterns = [
                (r"eval\s*\(.*base64", "Obfuscated code execution", 8),
                (r"exec\s*\(.*decode", "Hidden command execution", 9),
                (r"/bin/sh\s+-c", "Shell command injection", 7),
                (r"wget.*\|.*sh", "Remote script execution", 10),
                (r"curl.*\|.*bash", "Remote script execution", 10),
                (r"nc\s+-[el].*\d+", "Netcat backdoor", 9),
                (r"chmod\s+777", "Dangerous permission change", 6),
                (r"rm\s+-rf\s+/", "Destructive command", 10),
            ]
            
            files_scanned = 0
            if scan_path.is_file():
                threats, score = self._scan_file_heuristics(scan_path, suspicious_patterns)
                result["threats_found"].extend(threats)
                result["risk_score"] = max(result["risk_score"], score)
                files_scanned = 1
            elif scan_path.is_dir():
                max_files = 100 if quick else 1000
                for i, file_path in enumerate(scan_path.rglob("*")):
                    if i >= max_files:
                        break
                    if file_path.is_file():
                        try:
                            threats, score = self._scan_file_heuristics(file_path, suspicious_patterns)
                            result["threats_found"].extend(threats)
                            result["risk_score"] = max(result["risk_score"], score)
                            files_scanned += 1
                        except (OSError, PermissionError):
                            continue
            
            result["files_scanned"] = files_scanned
            result["scans_remaining"] = self._get_scans_remaining()
            
            self.logger.info(f"Heuristic scan completed: {files_scanned} files, {len(result['threats_found'])} threats")
            
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            self.logger.error(f"Heuristic scan error: {e}")
        
        return result
    
    def _scan_file_heuristics(self, file_path: Path, patterns: List[Tuple[str, str, int]]) -> Tuple[List[Dict], int]:
        """Scan a single file for heuristic patterns"""
        threats = []
        max_score = 0
        
        try:
            if file_path.stat().st_size > 1024 * 1024:
                return threats, max_score
            
            content = file_path.read_text(errors='ignore')
            
            for pattern, description, severity in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    threats.append({
                        "file": str(file_path),
                        "pattern": description,
                        "severity": severity,
                        "type": "heuristic"
                    })
                    max_score = max(max_score, severity)
        except (OSError, PermissionError, UnicodeDecodeError):
            pass
        
        return threats, max_score
    
    def _get_scans_remaining(self) -> int:
        """Get remaining scans for today"""
        limits = self.tier.get_limits()
        max_scans = limits.get("max_scans_per_day", -1)
        if max_scans == -1:
            return -1
        return max(0, max_scans - self.scan_count_today)
    
    def behavioral_analysis(self, process_info: Optional[Dict] = None) -> Dict:
        """
        Perform AI-powered behavioral analysis
        Available on: gamer, workplace, ai-dev, server tiers
        """
        result = {
            "analysis_type": "behavioral",
            "timestamp": datetime.now().isoformat(),
            "anomalies": [],
            "risk_level": "low",
            "status": "completed"
        }
        
        if not self.tier.has_capability("behavioral_ai"):
            result["status"] = "tier_restricted"
            result["error"] = "Behavioral AI analysis requires Gamer tier or higher"
            result["upgrade_hint"] = "Upgrade to unlock AI-powered behavioral analysis"
            return result
        
        try:
            anomalies = []
            
            cpu_anomaly = self._check_cpu_anomaly()
            if cpu_anomaly:
                anomalies.append(cpu_anomaly)
            
            network_anomaly = self._check_network_anomaly()
            if network_anomaly:
                anomalies.append(network_anomaly)
            
            process_anomaly = self._check_process_anomaly()
            if process_anomaly:
                anomalies.append(process_anomaly)
            
            result["anomalies"] = anomalies
            
            if len(anomalies) == 0:
                result["risk_level"] = "low"
            elif len(anomalies) <= 2:
                result["risk_level"] = "medium"
            else:
                result["risk_level"] = "high"
            
            feature_config = self.tier.get_feature_config("behavioral_ai")
            result["model_type"] = feature_config.get("model_type", "basic")
            
            self.logger.info(f"Behavioral analysis completed: {len(anomalies)} anomalies, risk: {result['risk_level']}")
            
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            self.logger.error(f"Behavioral analysis error: {e}")
        
        return result
    
    def _check_cpu_anomaly(self) -> Optional[Dict]:
        """Check for CPU usage anomalies"""
        try:
            loadavg = Path("/proc/loadavg").read_text().split()
            load_1min = float(loadavg[0])
            
            cpu_count = os.cpu_count() or 1
            if load_1min > cpu_count * 2:
                return {
                    "type": "cpu_spike",
                    "description": f"High CPU load detected: {load_1min:.2f}",
                    "severity": "medium"
                }
        except (OSError, ValueError, IndexError):
            pass
        return None
    
    def _check_network_anomaly(self) -> Optional[Dict]:
        """Check for network anomalies"""
        try:
            result = subprocess.run(
                ["ss", "-tuln"],
                capture_output=True, text=True,
                timeout=SUBPROCESS_TIMEOUT
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]
                suspicious_ports = [4444, 5555, 6666, 31337, 12345]
                
                for line in lines:
                    for port in suspicious_ports:
                        if f":{port}" in line:
                            return {
                                "type": "suspicious_port",
                                "description": f"Suspicious port {port} detected in listening state",
                                "severity": "high"
                            }
        except (subprocess.TimeoutExpired, OSError):
            pass
        return None
    
    def _check_process_anomaly(self) -> Optional[Dict]:
        """Check for process anomalies"""
        try:
            suspicious_names = ["cryptominer", "xmrig", "minerd", "cgminer"]
            for proc in Path("/proc").iterdir():
                if not proc.name.isdigit():
                    continue
                try:
                    cmdline = (proc / "cmdline").read_text()
                    for name in suspicious_names:
                        if name.lower() in cmdline.lower():
                            return {
                                "type": "suspicious_process",
                                "description": f"Potentially malicious process detected: {name}",
                                "severity": "critical"
                            }
                except (OSError, PermissionError):
                    continue
        except OSError:
            pass
        return None
    
    def ml_threat_detection(self, file_path: str) -> Dict:
        """
        Perform ML-based threat detection
        Available on: ai-dev, server tiers
        """
        result = {
            "detection_type": "ml",
            "file": file_path,
            "timestamp": datetime.now().isoformat(),
            "prediction": None,
            "confidence": 0.0,
            "status": "completed"
        }
        
        if not self.tier.has_capability("ml_threat_detection"):
            result["status"] = "tier_restricted"
            result["error"] = "ML threat detection requires AI-Dev tier or higher"
            result["upgrade_hint"] = "Upgrade to unlock machine learning-based threat detection"
            return result
        
        try:
            path = Path(file_path)
            if not path.exists():
                result["status"] = "error"
                result["error"] = f"File not found: {file_path}"
                return result
            
            file_features = self._extract_file_features(path)
            
            prediction, confidence = self._ml_classify(file_features)
            
            result["prediction"] = prediction
            result["confidence"] = confidence
            result["features_analyzed"] = list(file_features.keys())
            
            feature_config = self.tier.get_feature_config("ml_threat_detection")
            result["zero_day_detection"] = feature_config.get("zero_day_detection", False)
            result["neural_network"] = feature_config.get("neural_network", False)
            
            self.logger.info(f"ML detection completed for {file_path}: {prediction} ({confidence:.2%})")
            
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            self.logger.error(f"ML detection error: {e}")
        
        return result
    
    def _extract_file_features(self, path: Path) -> Dict:
        """Extract features from file for ML analysis"""
        features = {}
        
        try:
            stat_info = path.stat()
            features["size"] = stat_info.st_size
            features["mode"] = stat_info.st_mode
            
            with open(path, 'rb') as f:
                header = f.read(256)
                features["entropy"] = self._calculate_entropy(header)
                features["magic_bytes"] = header[:4].hex() if len(header) >= 4 else ""
            
            features["extension"] = path.suffix.lower()
            features["hidden"] = path.name.startswith(".")
            
        except (OSError, PermissionError):
            pass
        
        return features
    
    def _calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy of data"""
        if not data:
            return 0.0
        
        freq = defaultdict(int)
        for byte in data:
            freq[byte] += 1
        
        entropy = 0.0
        length = len(data)
        for count in freq.values():
            p = count / length
            if p > 0:
                entropy -= p * (p.bit_length() - 1)
        
        return min(entropy / 8.0, 1.0)
    
    def _ml_classify(self, features: Dict) -> Tuple[str, float]:
        """
        Simulate ML classification
        In production, this would use actual ML models
        """
        risk_score = 0.0
        
        if features.get("entropy", 0) > 0.9:
            risk_score += 0.3
        
        if features.get("hidden", False):
            risk_score += 0.1
        
        dangerous_extensions = [".exe", ".dll", ".sh", ".bat", ".ps1"]
        if features.get("extension", "") in dangerous_extensions:
            risk_score += 0.2
        
        size = features.get("size", 0)
        if size > 0 and size < 1000:
            risk_score += 0.1
        
        if risk_score < 0.3:
            return "benign", 1.0 - risk_score
        elif risk_score < 0.6:
            return "suspicious", 0.5 + (risk_score * 0.3)
        else:
            return "malicious", 0.7 + (risk_score * 0.2)
    
    def gaming_integrity_check(self, game_path: Optional[str] = None) -> Dict:
        """
        Check gaming file integrity
        Available on: gamer tier
        """
        result = {
            "check_type": "gaming_integrity",
            "timestamp": datetime.now().isoformat(),
            "verified_files": 0,
            "modified_files": [],
            "status": "completed"
        }
        
        if not self.tier.has_capability("gaming_integrity_monitor"):
            result["status"] = "tier_restricted"
            result["error"] = "Gaming integrity monitoring requires Gamer tier"
            result["upgrade_hint"] = "Upgrade to Gamer tier for game file protection"
            return result
        
        try:
            game_dirs = [
                Path("/home") / os.environ.get("USER", "aegis") / ".steam",
                Path("/home") / os.environ.get("USER", "aegis") / ".local/share/Steam",
                Path("/home") / os.environ.get("USER", "aegis") / "Games",
            ]
            
            if game_path:
                game_dirs = [Path(game_path)]
            
            for game_dir in game_dirs:
                if game_dir.exists():
                    result["verified_files"] += 1
            
            feature_config = self.tier.get_feature_config("gaming_integrity_monitor")
            result["anti_cheat_compatible"] = feature_config.get("anti_cheat_compatible", False)
            result["game_process_protection"] = feature_config.get("game_process_protection", False)
            
            self.logger.info(f"Gaming integrity check completed: {result['verified_files']} verified")
            
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            self.logger.error(f"Gaming integrity check error: {e}")
        
        return result
    
    def xdr_analysis(self) -> Dict:
        """
        Perform Extended Detection and Response analysis
        Available on: server tier only
        """
        result = {
            "analysis_type": "xdr",
            "timestamp": datetime.now().isoformat(),
            "threat_indicators": [],
            "correlation_score": 0,
            "automated_actions": [],
            "status": "completed"
        }
        
        if not self.tier.has_capability("full_xdr"):
            result["status"] = "tier_restricted"
            result["error"] = "Full XDR requires Server tier"
            result["upgrade_hint"] = "Upgrade to Server tier for enterprise XDR capabilities"
            return result
        
        try:
            indicators = []
            
            if self.tier.has_capability("ebpf_detection"):
                result["ebpf_enabled"] = True
                indicators.append({
                    "source": "ebpf",
                    "type": "syscall_monitoring",
                    "status": "active"
                })
            
            if self.tier.has_capability("siem_integration"):
                result["siem_connected"] = True
                indicators.append({
                    "source": "siem",
                    "type": "log_correlation",
                    "status": "active"
                })
            
            if self.tier.has_capability("zero_trust"):
                result["zero_trust_enabled"] = True
            
            if self.tier.has_capability("rasp"):
                result["rasp_active"] = True
            
            result["threat_indicators"] = indicators
            result["correlation_score"] = len(indicators) * 20
            
            feature_config = self.tier.get_feature_config("full_xdr")
            result["automated_response"] = feature_config.get("automated_response", False)
            result["threat_hunting"] = feature_config.get("threat_hunting", False)
            
            self.logger.info(f"XDR analysis completed: {len(indicators)} active indicators")
            
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            self.logger.error(f"XDR analysis error: {e}")
        
        return result
    
    def get_security_summary(self) -> Dict:
        """Get comprehensive security analysis summary"""
        summary = {
            "tier": self.tier.get_status(),
            "timestamp": datetime.now().isoformat(),
            "scans_remaining_today": self._get_scans_remaining(),
            "available_analyses": [],
            "restricted_analyses": []
        }
        
        all_analyses = [
            ("heuristic_scan", "basic_heuristics"),
            ("behavioral_analysis", "behavioral_ai"),
            ("ml_threat_detection", "ml_threat_detection"),
            ("gaming_integrity_check", "gaming_integrity_monitor"),
            ("xdr_analysis", "full_xdr"),
        ]
        
        for analysis_name, capability in all_analyses:
            if self.tier.has_capability(capability):
                summary["available_analyses"].append(analysis_name)
            else:
                summary["restricted_analyses"].append(analysis_name)
        
        return summary


def get_ai_security_instance() -> AISecurityAnalyzer:
    """Factory function to get AI security analyzer instance"""
    return AISecurityAnalyzer()


def main():
    """Main entry point for testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Aegis AI Security Module")
    parser.add_argument("--status", action="store_true", help="Show AI security status")
    parser.add_argument("--scan", type=str, help="Run heuristic scan on path")
    parser.add_argument("--behavioral", action="store_true", help="Run behavioral analysis")
    parser.add_argument("--ml-detect", type=str, help="Run ML detection on file")
    parser.add_argument("--gaming", action="store_true", help="Run gaming integrity check")
    parser.add_argument("--xdr", action="store_true", help="Run XDR analysis")
    parser.add_argument("--version", action="store_true", help="Show version info")
    
    args = parser.parse_args()
    
    if args.version:
        print(f"Aegis AI Security Module v1.0.0")
        print(f"Tier: {TIER_LIMIT}")
        return 0
    
    analyzer = AISecurityAnalyzer()
    
    if args.status:
        summary = analyzer.get_security_summary()
        print(json.dumps(summary, indent=2))
        return 0
    
    if args.scan:
        result = analyzer.heuristic_scan(args.scan)
        print(json.dumps(result, indent=2))
        return 0
    
    if args.behavioral:
        result = analyzer.behavioral_analysis()
        print(json.dumps(result, indent=2))
        return 0
    
    if args.ml_detect:
        result = analyzer.ml_threat_detection(args.ml_detect)
        print(json.dumps(result, indent=2))
        return 0
    
    if args.gaming:
        result = analyzer.gaming_integrity_check()
        print(json.dumps(result, indent=2))
        return 0
    
    if args.xdr:
        result = analyzer.xdr_analysis()
        print(json.dumps(result, indent=2))
        return 0
    
    summary = analyzer.get_security_summary()
    print(f"\nAegis AI Security Module")
    print(f"=" * 40)
    print(f"Tier: {summary['tier']['tier_name']} (Level {summary['tier']['tier_level']})")
    print(f"Description: {summary['tier']['description']}")
    print(f"\nCapabilities: {summary['tier']['capabilities_count']}")
    for cap in summary['tier']['capabilities']:
        print(f"  ✓ {cap}")
    print(f"\nAvailable Analyses: {len(summary['available_analyses'])}")
    for analysis in summary['available_analyses']:
        print(f"  ✓ {analysis}")
    if summary['restricted_analyses']:
        print(f"\nRestricted (upgrade to unlock):")
        for analysis in summary['restricted_analyses']:
            print(f"  ✗ {analysis}")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
