"""
Auto-Healing Engine - System Self-Healing and Recovery
Monitors system health and automatically recovers from failures
"""

import time
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum


class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"


@dataclass
class ComponentHealth:
    """Health status for a single component"""
    name: str
    status: HealthStatus = HealthStatus.HEALTHY
    last_check: float = 0.0
    error_count: int = 0
    recovery_attempts: int = 0


class AutoHealingEngine:
    """
    Auto-healing engine that monitors and recovers system components.
    
    Features:
    - Health monitoring for all components
    - Automatic recovery strategies
    - Circuit breaker pattern
    - Configurable healing actions
    """
    
    def __init__(self, check_interval: int = 30, max_recovery_attempts: int = 3):
        self.check_interval = check_interval
        self.max_recovery_attempts = max_recovery_attempts
        self.components: Dict[str, ComponentHealth] = {}
        self.recovery_strategies: Dict[str, Callable] = {}
        self.logger = logging.getLogger(__name__)
        
    def register_component(self, name: str, health_check: Callable[[], bool]):
        """Register a component for health monitoring"""
        self.components[name] = ComponentHealth(name=name)
        self.recovery_strategies[name] = health_check
        
    def check_health(self) -> Dict[str, HealthStatus]:
        """Check health of all registered components"""
        status = {}
        
        for name, component in self.components.items():
            component.last_check = time.time()
            
            try:
                is_healthy = self.recovery_strategies[name]()
                if is_healthy:
                    component.status = HealthStatus.HEALTHY
                    component.error_count = 0
                else:
                    component.status = HealthStatus.DEGRADED
                    component.error_count += 1
            except Exception as e:
                component.status = HealthStatus.FAILED
                component.error_count += 1
                self.logger.error(f"Component {name} check failed: {e}")
            
            status[name] = component.status
            
        return status
    
    def heal_component(self, name: str) -> bool:
        """Attempt to heal a failed component"""
        component = self.components.get(name)
        if not component:
            return False
        
        if component.recovery_attempts >= self.max_recovery_attempts:
            self.logger.warning(f"Max recovery attempts reached for {name}")
            return False
        
        component.recovery_attempts += 1
        
        # Try healing strategy
        try:
            # Reset and retry
            if hasattr(component, 'reset'):
                component.reset()
            
            # Re-check health
            is_healthy = self.recovery_strategies[name]()
            
            if is_healthy:
                component.status = HealthStatus.HEALTHY
                component.recovery_attempts = 0
                component.error_count = 0
                self.logger.info(f"Component {name} healed successfully")
                return True
            else:
                self.logger.warning(f"Healing attempt {component.recovery_attempts} failed for {name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Healing failed for {name}: {e}")
            return False
    
    def auto_heal(self):
        """Automatically heal degraded or failed components"""
        status = self.check_health()
        
        for name, comp_status in status.items():
            if comp_status in (HealthStatus.DEGRADED, HealthStatus.FAILED):
                self.heal_component(name)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system health status"""
        status = self.check_health()
        
        healthy_count = sum(1 for s in status.values() if s == HealthStatus.HEALTHY)
        degraded_count = sum(1 for s in status.values() if s == HealthStatus.DEGRADED)
        failed_count = sum(1 for s in status.values() if s == HealthStatus.FAILED)
        
        overall = HealthStatus.HEALTHY
        if failed_count > 0:
            overall = HealthStatus.FAILED
        elif degraded_count > 0:
            overall = HealthStatus.DEGRADED
        
        return {
            "overall_status": overall.value,
            "components": status,
            "summary": {
                "healthy": healthy_count,
                "degraded": degraded_count,
                "failed": failed_count,
                "total": len(status)
            }
        }


def create_demo_engine() -> AutoHealingEngine:
    """Create a demo auto-healing engine with sample components"""
    engine = AutoHealingEngine(check_interval=10, max_recovery_attempts=3)
    
    # Register demo components
    engine.register_component("database", lambda: True)  # Always healthy
    engine.register_component("cache", lambda: True)     # Always healthy
    engine.register_component("api", lambda: True)       # Always healthy
    
    return engine


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    engine = create_demo_engine()
    
    print("🏥 Auto-Healing Engine initialized")
    print(f"   Components: {len(engine.components)}")
    print(f"   Check interval: {engine.check_interval}s")
    print(f"   Max recovery attempts: {engine.max_recovery_attempts}")
    
    # Run health check
    status = engine.get_system_status()
    print(f"\n📊 System Status: {status['overall_status']}")
    print(f"   Healthy: {status['summary']['healthy']}")
    print(f"   Degraded: {status['summary']['degraded']}")
    print(f"   Failed: {status['summary']['failed']}")
    
    # Run auto-heal
    engine.auto_heal()
    print("\n🔧 Auto-heal completed")
    
    print("✅ Auto-Healing Engine demo completed")