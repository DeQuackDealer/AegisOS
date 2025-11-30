#!/usr/bin/env python3
"""
Aegis OS Security Utilities
Shared security functions for all Aegis tools including:
- Secure temporary file handling
- Input validation and sanitization
- Audit logging
- Secure configuration handling
"""

import os
import sys
import re
import json
import hashlib
import tempfile
import stat
import logging
import shutil
import fcntl
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from contextlib import contextmanager


TIER_LIMIT = "full"  # "freemium" or "full"


class InputValidator:
    """Secure input validation utilities"""
    
    SAFE_FILENAME_PATTERN = re.compile(r'^[\w\-. ]+$')
    SAFE_PATH_PATTERN = re.compile(r'^[\w\-./]+$')
    IP_ADDRESS_PATTERN = re.compile(
        r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
        r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    )
    HOSTNAME_PATTERN = re.compile(
        r'^(?=.{1,253}$)(?:(?!-)[A-Za-z0-9-]{1,63}(?<!-)\.)*'
        r'(?:(?!-)[A-Za-z0-9-]{1,63}(?<!-))$'
    )
    
    @classmethod
    def sanitize_string(cls, value: str, max_length: int = 1024,
                       allow_chars: str = "") -> str:
        """
        Sanitize a string by removing dangerous characters
        
        Args:
            value: Input string to sanitize
            max_length: Maximum allowed length
            allow_chars: Additional characters to allow
        
        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            return ""
        
        value = value[:max_length]
        
        safe_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
                        '0123456789-_. ' + allow_chars)
        return ''.join(c for c in value if c in safe_chars)
    
    @classmethod
    def validate_path(cls, path: str, must_exist: bool = False,
                     allowed_prefixes: Optional[List[str]] = None) -> bool:
        """
        Validate a file path
        
        Args:
            path: Path to validate
            must_exist: Whether path must exist
            allowed_prefixes: List of allowed path prefixes
        
        Returns:
            True if path is valid
        """
        if not path or not isinstance(path, str):
            return False
        
        if '\x00' in path:
            return False
        
        try:
            resolved = Path(path).resolve()
            
            if '..' in Path(path).parts:
                real_parts = resolved.parts
                given_parts = Path(path).parts
                normalized = Path(*[p for p in given_parts if p != '..'])
                if str(normalized.resolve()) != str(resolved):
                    return False
            
            if allowed_prefixes:
                if not any(str(resolved).startswith(p) for p in allowed_prefixes):
                    return False
            
            if must_exist and not resolved.exists():
                return False
            
            return True
        except (ValueError, OSError, RuntimeError):
            return False
    
    @classmethod
    def validate_filename(cls, filename: str) -> bool:
        """Validate a filename (no path components)"""
        if not filename or not isinstance(filename, str):
            return False
        
        if '/' in filename or '\\' in filename:
            return False
        
        if filename in ('.', '..'):
            return False
        
        if len(filename) > 255:
            return False
        
        return bool(cls.SAFE_FILENAME_PATTERN.match(filename))
    
    @classmethod
    def validate_ip_address(cls, ip: str) -> bool:
        """Validate an IPv4 address"""
        if not ip or not isinstance(ip, str):
            return False
        return bool(cls.IP_ADDRESS_PATTERN.match(ip))
    
    @classmethod
    def validate_hostname(cls, hostname: str) -> bool:
        """Validate a hostname"""
        if not hostname or not isinstance(hostname, str):
            return False
        if len(hostname) > 253:
            return False
        return bool(cls.HOSTNAME_PATTERN.match(hostname))
    
    @classmethod
    def validate_port(cls, port: Union[int, str]) -> bool:
        """Validate a network port number"""
        try:
            port_num = int(port)
            return 1 <= port_num <= 65535
        except (ValueError, TypeError):
            return False
    
    @classmethod
    def validate_json(cls, data: str, max_size: int = 1024 * 1024) -> Optional[Any]:
        """
        Safely parse JSON with size limit
        
        Args:
            data: JSON string to parse
            max_size: Maximum allowed size in bytes
        
        Returns:
            Parsed JSON or None if invalid
        """
        if not data or not isinstance(data, str):
            return None
        
        if len(data) > max_size:
            return None
        
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return None
    
    @classmethod
    def sanitize_shell_arg(cls, arg: str) -> str:
        """Sanitize an argument for shell use (quote it properly)"""
        if not isinstance(arg, str):
            return ""
        
        return "'" + arg.replace("'", "'\"'\"'") + "'"


class SecureTempFile:
    """
    Secure temporary file handling with automatic cleanup
    and proper permissions
    """
    
    def __init__(self, suffix: str = "", prefix: str = "aegis-",
                 dir: Optional[str] = None, mode: int = 0o600,
                 delete_on_close: bool = True):
        """
        Initialize secure temp file
        
        Args:
            suffix: File suffix
            prefix: File prefix
            dir: Directory to create file in
            mode: File permissions (default: owner read/write only)
            delete_on_close: Whether to delete file on close
        """
        self.suffix = suffix
        self.prefix = prefix
        self.dir = dir or tempfile.gettempdir()
        self.mode = mode
        self.delete_on_close = delete_on_close
        self.path: Optional[str] = None
        self._fd: Optional[int] = None
        self._file: Optional[Any] = None
    
    def __enter__(self):
        self._fd, self.path = tempfile.mkstemp(
            suffix=self.suffix, prefix=self.prefix, dir=self.dir
        )
        
        os.fchmod(self._fd, self.mode)
        
        self._file = os.fdopen(self._fd, 'w+b')
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        if self.delete_on_close:
            self.secure_delete()
    
    def write(self, data: Union[str, bytes]):
        """Write data to temp file"""
        if self._file is None:
            raise ValueError("File not open")
        
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        self._file.write(data)
        self._file.flush()
    
    def read(self) -> bytes:
        """Read data from temp file"""
        if self._file is None:
            raise ValueError("File not open")
        
        self._file.seek(0)
        return self._file.read()
    
    def close(self):
        """Close the temp file"""
        if self._file is not None:
            try:
                self._file.close()
            except (OSError, IOError):
                pass
            self._file = None
            self._fd = None
    
    def secure_delete(self):
        """Securely delete the temp file by overwriting with zeros"""
        if self.path is None:
            return
        
        path = Path(self.path)
        if not path.exists():
            self.path = None
            return
        
        try:
            size = path.stat().st_size
            if size > 0:
                with open(self.path, 'wb') as f:
                    f.write(b'\x00' * size)
                    f.flush()
                    os.fsync(f.fileno())
        except (OSError, IOError):
            pass
        
        try:
            os.unlink(self.path)
        except OSError:
            pass
        
        self.path = None


class SecureTempDir:
    """Secure temporary directory with automatic cleanup"""
    
    def __init__(self, prefix: str = "aegis-", dir: Optional[str] = None,
                 mode: int = 0o700):
        self.prefix = prefix
        self.dir = dir or tempfile.gettempdir()
        self.mode = mode
        self.path: Optional[str] = None
    
    def __enter__(self):
        self.path = tempfile.mkdtemp(prefix=self.prefix, dir=self.dir)
        os.chmod(self.path, self.mode)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
    
    def cleanup(self):
        """Securely cleanup the temp directory"""
        if self.path and Path(self.path).exists():
            try:
                for root, dirs, files in os.walk(self.path, topdown=False):
                    for name in files:
                        file_path = Path(root) / name
                        try:
                            size = file_path.stat().st_size
                            if size > 0:
                                with open(file_path, 'wb') as f:
                                    f.write(b'\x00' * min(size, 1024 * 1024))
                        except (OSError, IOError):
                            pass
                
                shutil.rmtree(self.path, ignore_errors=True)
            except (OSError, IOError):
                pass
            self.path = None


class AuditLogger:
    """
    Secure audit logging with tamper detection and structured events
    """
    
    def __init__(self, log_file: Path, component: str = "aegis"):
        """
        Initialize audit logger
        
        Args:
            log_file: Path to log file
            component: Component name for logging
        """
        self.log_file = log_file
        self.component = component
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging handlers"""
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        handlers = [logging.StreamHandler()]
        
        try:
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            ))
            handlers.append(file_handler)
            
            try:
                os.chmod(self.log_file, stat.S_IRUSR | stat.S_IWUSR)
            except (OSError, PermissionError):
                pass
        except (OSError, PermissionError):
            pass
        
        self.logger = logging.getLogger(self.component)
        self.logger.setLevel(logging.INFO)
        
        for handler in handlers:
            self.logger.addHandler(handler)
    
    def log_event(self, event_type: str, message: str,
                  severity: str = "INFO", details: Optional[Dict] = None):
        """
        Log a security event with structured data
        
        Args:
            event_type: Type of event (e.g., "AUTH_FAILURE", "FILE_ACCESS")
            message: Human-readable message
            severity: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            details: Additional structured data
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "component": self.component,
            "message": message,
            "pid": os.getpid(),
            "uid": os.getuid(),
        }
        
        if details:
            event["details"] = details
        
        event_hash = hashlib.sha256(
            json.dumps(event, sort_keys=True).encode()
        ).hexdigest()[:16]
        event["checksum"] = event_hash
        
        log_level = getattr(logging, severity.upper(), logging.INFO)
        self.logger.log(log_level, json.dumps(event))
    
    def log_access(self, resource: str, action: str,
                   success: bool, user: Optional[str] = None):
        """Log a resource access event"""
        self.log_event(
            "RESOURCE_ACCESS",
            f"{action} on {resource}: {'success' if success else 'denied'}",
            severity="INFO" if success else "WARNING",
            details={
                "resource": resource,
                "action": action,
                "success": success,
                "user": user or os.getenv("USER", "unknown")
            }
        )
    
    def log_auth(self, method: str, success: bool,
                 user: Optional[str] = None, source: Optional[str] = None):
        """Log an authentication event"""
        self.log_event(
            "AUTHENTICATION",
            f"Auth via {method}: {'success' if success else 'failure'}",
            severity="INFO" if success else "WARNING",
            details={
                "method": method,
                "success": success,
                "user": user,
                "source": source
            }
        )


class SecureConfig:
    """Secure configuration file handling with locking"""
    
    def __init__(self, config_path: Path, default_config: Optional[Dict] = None):
        """
        Initialize secure config handler
        
        Args:
            config_path: Path to configuration file
            default_config: Default configuration values
        """
        self.config_path = config_path
        self.default_config = default_config or {}
        self._lock_fd: Optional[int] = None
        self.config: Dict = {}
    
    @contextmanager
    def _file_lock(self, exclusive: bool = True):
        """Context manager for file locking"""
        lock_path = self.config_path.with_suffix('.lock')
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._lock_fd = os.open(
            str(lock_path),
            os.O_RDWR | os.O_CREAT,
            0o600
        )
        
        try:
            lock_type = fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH
            fcntl.flock(self._lock_fd, lock_type)
            yield
        finally:
            fcntl.flock(self._lock_fd, fcntl.LOCK_UN)
            os.close(self._lock_fd)
            self._lock_fd = None
    
    def load(self) -> Dict:
        """Load configuration with locking"""
        self.config = self.default_config.copy()
        
        if not self.config_path.exists():
            return self.config
        
        try:
            with self._file_lock(exclusive=False):
                content = self.config_path.read_text()
                loaded = json.loads(content)
                
                if isinstance(loaded, dict):
                    self.config.update(loaded)
        except (json.JSONDecodeError, OSError, PermissionError):
            pass
        
        return self.config
    
    def save(self):
        """Save configuration atomically with locking"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with self._file_lock(exclusive=True):
                with SecureTempFile(
                    dir=str(self.config_path.parent),
                    prefix='.config-',
                    suffix='.tmp',
                    mode=0o600,
                    delete_on_close=False
                ) as tmp:
                    tmp.write(json.dumps(self.config, indent=2))
                    tmp.close()
                    
                    os.rename(tmp.path, self.config_path)
                    tmp.path = None
        except (OSError, PermissionError, IOError) as e:
            raise RuntimeError(f"Failed to save config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set a configuration value"""
        self.config[key] = value
    
    def update(self, updates: Dict):
        """Update multiple configuration values"""
        self.config.update(updates)


def compute_file_hash(path: str, algorithm: str = "sha256") -> Optional[str]:
    """
    Compute hash of a file securely
    
    Args:
        path: Path to file
        algorithm: Hash algorithm (sha256, sha512, md5)
    
    Returns:
        Hex digest of hash or None on error
    """
    if not InputValidator.validate_path(path, must_exist=True):
        return None
    
    try:
        hasher = hashlib.new(algorithm)
        with open(path, 'rb') as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()
    except (OSError, ValueError):
        return None


def secure_compare(a: str, b: str) -> bool:
    """
    Constant-time string comparison to prevent timing attacks
    
    Args:
        a: First string
        b: Second string
    
    Returns:
        True if strings are equal
    """
    if not isinstance(a, str) or not isinstance(b, str):
        return False
    
    if len(a) != len(b):
        return False
    
    result = 0
    for x, y in zip(a.encode(), b.encode()):
        result |= x ^ y
    
    return result == 0


def drop_privileges(target_user: str = "nobody",
                   target_group: str = "nogroup") -> bool:
    """
    Drop root privileges to specified user/group
    
    Args:
        target_user: Target username
        target_group: Target group name
    
    Returns:
        True if successful
    """
    if os.getuid() != 0:
        return True
    
    import pwd
    import grp
    
    try:
        target_gid = grp.getgrnam(target_group).gr_gid
    except KeyError:
        target_gid = 65534
    
    try:
        target_uid = pwd.getpwnam(target_user).pw_uid
    except KeyError:
        target_uid = 65534
    
    try:
        os.setgroups([])
        os.setgid(target_gid)
        os.setuid(target_uid)
        
        try:
            os.setuid(0)
            return False
        except OSError:
            return True
    except OSError:
        return False


if __name__ == "__main__":
    print(f"Aegis Security Utilities")
    print(f"Tier: {TIER_LIMIT}")
    print(f"Module path: {__file__}")
