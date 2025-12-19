#!/usr/bin/env python3
"""
Aegis OS Kernel Optimizer
Advanced kernel optimization service for gaming performance

WARNING: This is raw source code. Do not run directly.
Build with: ./build.sh

PREMIUM FEATURE - Requires Gamer Edition license
"""

import os
import subprocess
import logging
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass, field
from enum import Enum


class KernelScheduler(Enum):
    """Available kernel schedulers"""
    CFS = "cfs"           # Completely Fair Scheduler (default)
    LAVD = "lavd"         # Latency-Aware Virtual Deadline (experimental)
    BORE = "bore"         # Burst-Oriented Response Enhancer
    EEVDF = "eevdf"       # Earliest Eligible Virtual Deadline First


class CPUGovernor(Enum):
    """CPU frequency governors"""
    PERFORMANCE = "performance"
    POWERSAVE = "powersave"
    SCHEDUTIL = "schedutil"
    ONDEMAND = "ondemand"
    CONSERVATIVE = "conservative"


class TicklessMode(Enum):
    """Kernel tickless (nohz) modes"""
    OFF = "off"
    IDLE = "idle"
    FULL = "full"


@dataclass
class CPUTopology:
    """CPU topology information"""
    physical_cores: int = 0
    logical_cores: int = 0
    sockets: int = 1
    cores_per_socket: int = 0
    threads_per_core: int = 1
    isolated_cores: List[int] = field(default_factory=list)
    gaming_cores: List[int] = field(default_factory=list)
    housekeeping_cores: List[int] = field(default_factory=list)


@dataclass
class KernelOptimizationProfile:
    """Kernel optimization profile"""
    name: str
    governor: CPUGovernor
    tickless_mode: TicklessMode
    isolate_cores: bool
    rcu_offload: bool
    irq_balance: bool
    scheduler_tuning: bool
    lavd_enabled: bool


class KernelOptimizer:
    """
    Kernel Optimizer - Advanced kernel-level gaming optimizations.
    
    Features:
    - CPU core isolation for dedicated gaming
    - Tickless kernel mode configuration
    - RCU callback offloading
    - LAVD scheduler detection and activation (experimental)
    - CPU governor management
    - IRQ affinity optimization
    - Scheduler latency tuning
    """
    
    SYSCTL_CONF_PATH = Path("/etc/sysctl.d/99-aegis-gaming.conf")
    GRUB_CONF_PATH = Path("/etc/default/grub")
    CPU_PATH = Path("/sys/devices/system/cpu")
    PROC_PATH = Path("/proc")
    
    PROFILES = {
        "gaming": KernelOptimizationProfile(
            name="Gaming",
            governor=CPUGovernor.PERFORMANCE,
            tickless_mode=TicklessMode.FULL,
            isolate_cores=True,
            rcu_offload=True,
            irq_balance=False,
            scheduler_tuning=True,
            lavd_enabled=False
        ),
        "competitive": KernelOptimizationProfile(
            name="Competitive",
            governor=CPUGovernor.PERFORMANCE,
            tickless_mode=TicklessMode.FULL,
            isolate_cores=True,
            rcu_offload=True,
            irq_balance=False,
            scheduler_tuning=True,
            lavd_enabled=True
        ),
        "balanced": KernelOptimizationProfile(
            name="Balanced",
            governor=CPUGovernor.SCHEDUTIL,
            tickless_mode=TicklessMode.IDLE,
            isolate_cores=False,
            rcu_offload=False,
            irq_balance=True,
            scheduler_tuning=False,
            lavd_enabled=False
        ),
        "power_saving": KernelOptimizationProfile(
            name="Power Saving",
            governor=CPUGovernor.POWERSAVE,
            tickless_mode=TicklessMode.IDLE,
            isolate_cores=False,
            rcu_offload=False,
            irq_balance=True,
            scheduler_tuning=False,
            lavd_enabled=False
        )
    }
    
    def __init__(self):
        self._logger = logging.getLogger("aegis-kernel-optimizer")
        self._topology: Optional[CPUTopology] = None
        self._current_profile: Optional[KernelOptimizationProfile] = None
        self._original_governors: Dict[int, str] = {}
        self._lavd_available: bool = False
        
    def initialize(self) -> bool:
        """Initialize kernel optimizer and detect system capabilities"""
        self._logger.info("Initializing Aegis Kernel Optimizer")
        
        # Detect CPU topology
        self._topology = self._detect_cpu_topology()
        
        # Check for LAVD scheduler support
        self._lavd_available = self._detect_lavd_scheduler()
        
        # Store original governors for restore
        self._store_original_governors()
        
        return True
    
    def _detect_cpu_topology(self) -> CPUTopology:
        """Detect CPU topology for core isolation planning"""
        topology = CPUTopology()
        
        try:
            # Count logical CPUs
            cpu_dirs = list(self.CPU_PATH.glob("cpu[0-9]*"))
            topology.logical_cores = len(cpu_dirs)
            
            # Detect physical cores
            physical_ids = set()
            core_ids = set()
            
            for cpu_dir in cpu_dirs:
                topo_path = cpu_dir / "topology"
                
                if (topo_path / "physical_package_id").exists():
                    pkg_id = int((topo_path / "physical_package_id").read_text().strip())
                    physical_ids.add(pkg_id)
                    
                if (topo_path / "core_id").exists():
                    core_id = int((topo_path / "core_id").read_text().strip())
                    core_ids.add(core_id)
                    
            topology.sockets = len(physical_ids) if physical_ids else 1
            topology.physical_cores = len(core_ids) if core_ids else topology.logical_cores
            topology.threads_per_core = topology.logical_cores // topology.physical_cores if topology.physical_cores else 1
            topology.cores_per_socket = topology.physical_cores // topology.sockets if topology.sockets else topology.physical_cores
            
            # Plan core isolation (reserve 2 cores for system, rest for gaming)
            if topology.logical_cores >= 4:
                topology.housekeeping_cores = [0, 1]
                topology.gaming_cores = list(range(2, topology.logical_cores))
            else:
                topology.housekeeping_cores = [0]
                topology.gaming_cores = list(range(1, topology.logical_cores))
                
            self._logger.info(f"Detected: {topology.physical_cores} physical, {topology.logical_cores} logical cores")
            
        except Exception as e:
            self._logger.error(f"Failed to detect CPU topology: {e}")
            
        return topology
    
    def _detect_lavd_scheduler(self) -> bool:
        """Detect LAVD scheduler availability (experimental)"""
        lavd_indicators = [
            Path("/sys/kernel/sched_ext"),
            Path("/sys/fs/bpf/sched_ext"),
            Path("/proc/sched_lavd")
        ]
        
        for indicator in lavd_indicators:
            if indicator.exists():
                self._logger.info("LAVD scheduler detected (experimental)")
                return True
                
        # Check kernel config
        try:
            result = subprocess.run(
                ["zgrep", "CONFIG_SCHED_CLASS_EXT", "/proc/config.gz"],
                capture_output=True, text=True
            )
            if "=y" in result.stdout or "=m" in result.stdout:
                self._logger.info("LAVD scheduler support available in kernel")
                return True
        except Exception:
            pass
            
        return False
    
    def _store_original_governors(self) -> None:
        """Store original CPU governors for later restoration"""
        try:
            for cpu_dir in self.CPU_PATH.glob("cpu[0-9]*"):
                governor_path = cpu_dir / "cpufreq/scaling_governor"
                if governor_path.exists():
                    cpu_num = int(cpu_dir.name.replace("cpu", ""))
                    self._original_governors[cpu_num] = governor_path.read_text().strip()
        except Exception as e:
            self._logger.warning(f"Failed to store original governors: {e}")
    
    def apply_profile(self, profile_name: str) -> bool:
        """Apply kernel optimization profile"""
        profile = self.PROFILES.get(profile_name)
        if not profile:
            self._logger.error(f"Unknown profile: {profile_name}")
            return False
            
        self._logger.info(f"Applying kernel profile: {profile.name}")
        
        success = True
        
        # Apply CPU governor
        if not self._set_cpu_governor(profile.governor):
            self._logger.warning("Failed to set CPU governor")
            success = False
            
        # Configure tickless mode
        if not self._configure_tickless_mode(profile.tickless_mode):
            self._logger.warning("Tickless mode configuration requires reboot")
            
        # Configure RCU offload
        if profile.rcu_offload:
            if not self._configure_rcu_offload():
                self._logger.warning("RCU offload configuration requires reboot")
                
        # Configure IRQ balancing
        self._configure_irq_balance(profile.irq_balance)
        
        # Apply scheduler tuning
        if profile.scheduler_tuning:
            self._apply_scheduler_tuning()
            
        # Enable LAVD if available and requested
        if profile.lavd_enabled and self._lavd_available:
            self._enable_lavd_scheduler()
            
        self._current_profile = profile
        return success
    
    def _set_cpu_governor(self, governor: CPUGovernor) -> bool:
        """Set CPU frequency governor for all cores"""
        success = True
        
        try:
            for cpu_dir in self.CPU_PATH.glob("cpu[0-9]*"):
                governor_path = cpu_dir / "cpufreq/scaling_governor"
                available_path = cpu_dir / "cpufreq/scaling_available_governors"
                
                if not governor_path.exists():
                    continue
                    
                # Check if governor is available
                if available_path.exists():
                    available = available_path.read_text().strip()
                    if governor.value not in available:
                        self._logger.warning(f"Governor {governor.value} not available on {cpu_dir.name}")
                        continue
                        
                try:
                    governor_path.write_text(governor.value)
                except PermissionError:
                    # Try via cpupower
                    subprocess.run(
                        ["cpupower", "frequency-set", "-g", governor.value],
                        capture_output=True
                    )
                    
        except Exception as e:
            self._logger.error(f"Failed to set CPU governor: {e}")
            success = False
            
        return success
    
    def _configure_tickless_mode(self, mode: TicklessMode) -> bool:
        """Configure tickless kernel mode (requires boot parameter changes)"""
        # Tickless mode is configured via boot parameters
        # This function prepares the GRUB configuration
        
        if not self._topology:
            return False
            
        if mode == TicklessMode.FULL and self._topology.gaming_cores:
            cores_str = self._cores_to_string(self._topology.gaming_cores)
            self._logger.info(f"Tickless full mode prepared for cores: {cores_str}")
            # Actual change requires GRUB update and reboot
            return True
            
        return True
    
    def _configure_rcu_offload(self) -> bool:
        """Configure RCU callback offloading"""
        # RCU offload is configured via boot parameters
        # This validates current configuration
        
        try:
            cmdline = Path("/proc/cmdline").read_text()
            
            if "rcu_nocbs=" in cmdline:
                self._logger.info("RCU callback offload is active")
                return True
            else:
                self._logger.info("RCU callback offload requires boot parameter: rcu_nocbs=all")
                return False
                
        except Exception:
            return False
    
    def _configure_irq_balance(self, enable: bool) -> None:
        """Enable or disable IRQ balancing"""
        try:
            if enable:
                subprocess.run(["systemctl", "enable", "--now", "irqbalance"], 
                              capture_output=True)
            else:
                subprocess.run(["systemctl", "disable", "--now", "irqbalance"],
                              capture_output=True)
                # Pin IRQs to housekeeping cores
                self._pin_irqs_to_housekeeping()
        except Exception as e:
            self._logger.warning(f"IRQ balance configuration failed: {e}")
    
    def _pin_irqs_to_housekeeping(self) -> None:
        """Pin IRQs to housekeeping cores for gaming"""
        if not self._topology or not self._topology.housekeeping_cores:
            return
            
        mask = self._cores_to_mask(self._topology.housekeeping_cores)
        
        try:
            for irq_dir in Path("/proc/irq").iterdir():
                if irq_dir.is_dir() and irq_dir.name.isdigit():
                    affinity_path = irq_dir / "smp_affinity"
                    if affinity_path.exists():
                        try:
                            affinity_path.write_text(mask)
                        except Exception:
                            pass
        except Exception as e:
            self._logger.warning(f"IRQ pinning failed: {e}")
    
    def _apply_scheduler_tuning(self) -> None:
        """Apply scheduler tuning parameters"""
        sysctl_params = {
            "kernel.sched_autogroup_enabled": "0",
            "kernel.sched_latency_ns": "4000000",
            "kernel.sched_min_granularity_ns": "500000",
            "kernel.sched_wakeup_granularity_ns": "500000",
            "kernel.sched_migration_cost_ns": "250000"
        }
        
        for param, value in sysctl_params.items():
            self._apply_sysctl(param, value)
    
    def _apply_sysctl(self, param: str, value: str) -> bool:
        """Apply a sysctl parameter"""
        try:
            proc_path = Path("/proc/sys") / param.replace(".", "/")
            if proc_path.exists():
                proc_path.write_text(value)
                return True
        except Exception:
            try:
                subprocess.run(
                    ["sysctl", "-w", f"{param}={value}"],
                    capture_output=True
                )
                return True
            except Exception:
                pass
        return False
    
    def _enable_lavd_scheduler(self) -> bool:
        """Enable LAVD scheduler (experimental)"""
        self._logger.info("Attempting to enable LAVD scheduler (experimental)")
        
        # LAVD requires sched_ext BPF scheduler
        try:
            # Check if scx_lavd is available
            result = subprocess.run(
                ["which", "scx_lavd"],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                # Start LAVD scheduler
                subprocess.Popen(
                    ["scx_lavd"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                self._logger.info("LAVD scheduler started")
                return True
                
        except Exception as e:
            self._logger.warning(f"Failed to enable LAVD scheduler: {e}")
            
        return False
    
    def isolate_cores_for_gaming(self, game_pid: int) -> bool:
        """Isolate CPU cores for a specific game process"""
        if not self._topology or not self._topology.gaming_cores:
            return False
            
        # Set CPU affinity for game process
        mask = self._cores_to_mask(self._topology.gaming_cores)
        
        try:
            subprocess.run(
                ["taskset", "-p", mask, str(game_pid)],
                capture_output=True
            )
            
            # Set high priority
            os.setpriority(os.PRIO_PROCESS, game_pid, -10)
            
            self._logger.info(f"Isolated cores {self._topology.gaming_cores} for PID {game_pid}")
            return True
            
        except Exception as e:
            self._logger.error(f"Core isolation failed: {e}")
            return False
    
    def restore_defaults(self) -> bool:
        """Restore default kernel settings"""
        self._logger.info("Restoring default kernel settings")
        
        # Restore original governors
        for cpu_num, governor in self._original_governors.items():
            try:
                governor_path = self.CPU_PATH / f"cpu{cpu_num}" / "cpufreq/scaling_governor"
                if governor_path.exists():
                    governor_path.write_text(governor)
            except Exception:
                pass
                
        # Re-enable IRQ balancing
        self._configure_irq_balance(True)
        
        # Restore autogroup
        self._apply_sysctl("kernel.sched_autogroup_enabled", "1")
        
        self._current_profile = None
        return True
    
    def get_optimization_status(self) -> Dict:
        """Get current optimization status"""
        status = {
            "profile": self._current_profile.name if self._current_profile else "None",
            "cpu_governor": self._get_current_governor(),
            "lavd_available": self._lavd_available,
            "topology": {
                "physical_cores": self._topology.physical_cores if self._topology else 0,
                "logical_cores": self._topology.logical_cores if self._topology else 0,
                "gaming_cores": self._topology.gaming_cores if self._topology else [],
                "housekeeping_cores": self._topology.housekeeping_cores if self._topology else []
            }
        }
        
        # Check RCU offload status
        try:
            cmdline = Path("/proc/cmdline").read_text()
            status["rcu_offload"] = "rcu_nocbs=" in cmdline
            status["tickless"] = "nohz_full=" in cmdline or "nohz=on" in cmdline
        except Exception:
            status["rcu_offload"] = False
            status["tickless"] = False
            
        return status
    
    def _get_current_governor(self) -> str:
        """Get current CPU governor"""
        try:
            governor_path = self.CPU_PATH / "cpu0/cpufreq/scaling_governor"
            if governor_path.exists():
                return governor_path.read_text().strip()
        except Exception:
            pass
        return "unknown"
    
    def _cores_to_string(self, cores: List[int]) -> str:
        """Convert core list to string format (e.g., '2-5,7')"""
        if not cores:
            return ""
            
        ranges = []
        start = cores[0]
        end = cores[0]
        
        for core in cores[1:]:
            if core == end + 1:
                end = core
            else:
                if start == end:
                    ranges.append(str(start))
                else:
                    ranges.append(f"{start}-{end}")
                start = end = core
                
        if start == end:
            ranges.append(str(start))
        else:
            ranges.append(f"{start}-{end}")
            
        return ",".join(ranges)
    
    def _cores_to_mask(self, cores: List[int]) -> str:
        """Convert core list to hex affinity mask"""
        mask = 0
        for core in cores:
            mask |= (1 << core)
        return hex(mask)
    
    def generate_grub_params(self) -> str:
        """Generate recommended GRUB parameters based on system"""
        if not self._topology:
            self._detect_cpu_topology()
            
        params = ["preempt=full", "threadirqs", "rcu_nocbs=all", "rcu_nocb_poll"]
        
        if self._topology and self._topology.gaming_cores:
            cores_str = self._cores_to_string(self._topology.gaming_cores)
            params.append(f"nohz_full={cores_str}")
            params.append(f"isolcpus={cores_str}")
            
        params.extend([
            "processor.max_cstate=1",
            "intel_idle.max_cstate=0",
            "iommu=pt",
            "transparent_hugepage=madvise"
        ])
        
        return " ".join(params)


def main():
    """Main entry point for kernel optimizer service"""
    import argparse
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    parser = argparse.ArgumentParser(description="Aegis OS Kernel Optimizer")
    parser.add_argument("action", choices=["enable", "disable", "status", "grub-params"],
                       help="Action to perform")
    parser.add_argument("--profile", default="gaming",
                       choices=["gaming", "competitive", "balanced", "power_saving"],
                       help="Optimization profile")
    parser.add_argument("--game-pid", type=int, help="Game process ID for core isolation")
    
    args = parser.parse_args()
    
    optimizer = KernelOptimizer()
    optimizer.initialize()
    
    if args.action == "enable":
        if optimizer.apply_profile(args.profile):
            if args.game_pid:
                optimizer.isolate_cores_for_gaming(args.game_pid)
            print(f"Kernel optimization enabled: {args.profile}")
            sys.exit(0)
        else:
            print("Failed to apply kernel optimizations")
            sys.exit(1)
            
    elif args.action == "disable":
        optimizer.restore_defaults()
        print("Kernel optimizations disabled")
        sys.exit(0)
        
    elif args.action == "status":
        status = optimizer.get_optimization_status()
        print(f"Profile: {status['profile']}")
        print(f"CPU Governor: {status['cpu_governor']}")
        print(f"LAVD Available: {status['lavd_available']}")
        print(f"RCU Offload: {status['rcu_offload']}")
        print(f"Tickless: {status['tickless']}")
        print(f"Gaming Cores: {status['topology']['gaming_cores']}")
        sys.exit(0)
        
    elif args.action == "grub-params":
        params = optimizer.generate_grub_params()
        print("Recommended GRUB parameters:")
        print(params)
        sys.exit(0)


if __name__ == "__main__":
    main()


# Build marker
# %%BUILD_MARKER:KERNEL_OPTIMIZER%%
