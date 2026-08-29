"""
health.py — Health monitoring for MoA Swarm

Provides health check endpoints, component monitoring,
and system status reporting.

Author: MoA Swarm Team
Version: 1.0.0
Last Updated: August 29, 2026
"""

import time
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass, field

from core.config import get_config, MoASwarmConfig
from core.models import HealthCheck


# ─── Component Health ─────────────────────────────────────────────────────────

@dataclass
class ComponentHealth:
    """Health status of a single component."""
    name: str
    status: str = "unknown"
    message: str = ""
    last_check: datetime = field(default_factory=datetime.utcnow)
    latency_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_healthy(self) -> bool:
        """Check if component is healthy."""
        return self.status == "healthy"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "status": self.status,
            "message": self.message,
            "last_check": self.last_check.isoformat(),
            "latency_ms": self.latency_ms,
            "metadata": self.metadata,
        }


# ─── Health Monitor ───────────────────────────────────────────────────────────

class HealthMonitor:
    """
    Monitors health of all swarm components.
    
    The health monitor:
    1. Checks individual component health
    2. Aggregates health status
    3. Provides health check endpoints
    4. Tracks system uptime
    """
    
    def __init__(self, config: Optional[MoASwarmConfig] = None):
        """
        Initialize the Health Monitor.
        
        Args:
            config: MoASwarmConfig instance (uses default if not provided)
        """
        self.config = config or get_config()
        self.components: Dict[str, ComponentHealth] = {}
        self.start_time = time.time()
        
        # Initialize default components
        self._init_default_components()
    
    def _init_default_components(self) -> None:
        """Initialize default component health checks."""
        default_components = [
            "api_gateway",
            "model_service",
            "browser_service",
            "search_service",
            "orchestrator",
            "agent_pool",
            "database",
            "cache",
        ]
        
        for component in default_components:
            self.components[component] = ComponentHealth(
                name=component,
                status="unknown",
                message="Not yet checked",
            )
    
    # ─── Health Checks ────────────────────────────────────────────────────────
    
    def check_component(self, component_name: str) -> ComponentHealth:
        """
        Check health of a specific component.
        
        Args:
            component_name: Name of the component to check
        
        Returns:
            ComponentHealth status
        """
        start_time = time.time()
        
        # Placeholder health check logic
        # In production, this would make actual API calls or health checks
        component = self.components.get(component_name)
        if component is None:
            component = ComponentHealth(
                name=component_name,
                status="unknown",
                message="Component not registered",
            )
            self.components[component_name] = component
        
        # Simulate health check
        # TODO: Replace with actual health check logic
        component.status = "healthy"
        component.message = "Component is operational"
        component.last_check = datetime.utcnow()
        component.latency_ms = (time.time() - start_time) * 1000
        
        return component
    
    def check_all_components(self) -> Dict[str, ComponentHealth]:
        """
        Check health of all registered components.
        
        Returns:
            Dictionary of component health statuses
        """
        for component_name in self.components:
            self.check_component(component_name)
        
        return self.components.copy()
    
    def check_api_health(self) -> ComponentHealth:
        """
        Check API gateway health.
        
        Returns:
            ComponentHealth status
        """
        start_time = time.time()
        
        # TODO: Implement actual API health check
        # This would typically ping the API endpoint
        
        component = self.components.get("api_gateway")
        if component:
            component.status = "healthy"
            component.message = "API gateway is responsive"
            component.last_check = datetime.utcnow()
            component.latency_ms = (time.time() - start_time) * 1000
        
        return component
    
    def check_model_service_health(self) -> ComponentHealth:
        """
        Check model service health.
        
        Returns:
            ComponentHealth status
        """
        start_time = time.time()
        
        # TODO: Implement actual model service health check
        # This would typically make a test API call
        
        component = self.components.get("model_service")
        if component:
            component.status = "healthy"
            component.message = "Model service is operational"
            component.last_check = datetime.utcnow()
            component.latency_ms = (time.time() - start_time) * 1000
        
        return component
    
    # ─── System Health ────────────────────────────────────────────────────────
    
    def get_system_health(self) -> HealthCheck:
        """
        Get overall system health.
        
        Returns:
            HealthCheck with aggregated status
        """
        # Check all components
        self.check_all_components()
        
        # Determine overall status
        healthy_count = sum(1 for c in self.components.values() if c.is_healthy)
        total_count = len(self.components)
        
        if healthy_count == total_count:
            status = "healthy"
        elif healthy_count > total_count // 2:
            status = "degraded"
        else:
            status = "unhealthy"
        
        # Build component status dict
        components = {
            name: component.status
            for name, component in self.components.items()
        }
        
        return HealthCheck(
            status=status,
            timestamp=datetime.utcnow(),
            components=components,
            uptime_seconds=time.time() - self.start_time,
        )
    
    def get_health_report(self) -> Dict[str, Any]:
        """
        Get detailed health report.
        
        Returns:
            Comprehensive health report dictionary
        """
        system_health = self.get_system_health()
        
        return {
            "status": system_health.status,
            "uptime_seconds": system_health.uptime_seconds,
            "uptime_human": self._format_uptime(system_health.uptime_seconds),
            "timestamp": system_health.timestamp.isoformat(),
            "components": {
                name: component.to_dict()
                for name, component in self.components.items()
            },
            "summary": {
                "total_components": len(self.components),
                "healthy": sum(1 for c in self.components.values() if c.is_healthy),
                "unhealthy": sum(1 for c in self.components.values() if not c.is_healthy),
                "avg_latency_ms": self._calculate_avg_latency(),
            },
        }
    
    # ─── Utility Methods ──────────────────────────────────────────────────────
    
    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in human-readable format."""
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        parts.append(f"{secs}s")
        
        return " ".join(parts)
    
    def _calculate_avg_latency(self) -> float:
        """Calculate average latency across all components."""
        latencies = [c.latency_ms for c in self.components.values() if c.latency_ms > 0]
        if not latencies:
            return 0.0
        return sum(latencies) / len(latencies)
    
    def register_component(self, name: str) -> ComponentHealth:
        """
        Register a new component for health monitoring.
        
        Args:
            name: Component name
        
        Returns:
            ComponentHealth instance
        """
        component = ComponentHealth(
            name=name,
            status="unknown",
            message="Registered but not yet checked",
        )
        self.components[name] = component
        return component
    
    def unregister_component(self, name: str) -> bool:
        """
        Unregister a component.
        
        Args:
            name: Component name
        
        Returns:
            True if unregistered, False if not found
        """
        if name in self.components:
            del self.components[name]
            return True
        return False


# ─── Async Health Checker ─────────────────────────────────────────────────────

class AsyncHealthChecker:
    """
    Async version of health checker for non-blocking health checks.
    """
    
    def __init__(self, health_monitor: HealthMonitor):
        """
        Initialize async health checker.
        
        Args:
            health_monitor: HealthMonitor instance
        """
        self.monitor = health_monitor
        self._running = False
        self._check_interval = 30  # seconds
    
    async def start_periodic_checks(self, interval: int = 30) -> None:
        """
        Start periodic health checks.
        
        Args:
            interval: Check interval in seconds
        """
        self._running = True
        self._check_interval = interval
        
        while self._running:
            self.monitor.check_all_components()
            await asyncio.sleep(interval)
    
    def stop(self) -> None:
        """Stop periodic health checks."""
        self._running = False
    
    async def check_now(self) -> HealthCheck:
        """Perform an immediate health check."""
        return self.monitor.get_system_health()


# ─── Usage Example ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Initialize health monitor
    monitor = HealthMonitor()
    
    # Check all components
    print("Checking all components...")
    monitor.check_all_components()
    
    # Get system health
    health = monitor.get_system_health()
    print(f"\nSystem Health: {health.status}")
    print(f"Uptime: {health.uptime_seconds:.1f} seconds")
    
    # Get detailed report
    report = monitor.get_health_report()
    print(f"\nHealth Report:")
    print(f"  Total components: {report['summary']['total_components']}")
    print(f"  Healthy: {report['summary']['healthy']}")
    print(f"  Unhealthy: {report['summary']['unhealthy']}")
    print(f"  Avg latency: {report['summary']['avg_latency_ms']:.2f}ms")
    
    # Component details
    print(f"\nComponent Details:")
    for name, component in report["components"].items():
        print(f"  {name}: {component['status']} ({component['latency_ms']:.2f}ms)")
