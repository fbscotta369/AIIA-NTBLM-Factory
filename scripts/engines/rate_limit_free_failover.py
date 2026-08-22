"""
Rate-Limit-Free-Failover Engine
Free model round-robin failover for LLM API calls
Rotates through free models when primary models hit rate limits
"""

import itertools
import time
import random
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum


class ModelStatus(Enum):
    AVAILABLE = "available"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"
    MAINTENANCE = "maintenance"


@dataclass
class ModelConfig:
    """Configuration for an LLM model provider"""
    name: str
    provider: str
    model_id: str
    api_endpoint: str = ""
    is_free: bool = False
    status: ModelStatus = ModelStatus.AVAILABLE
    rate_limit: int = 60  # requests per minute
    max_tokens: int = 4096
    last_used: float = 0.0
    failure_count: int = 0
    cooldown_until: float = 0.0


class RateLimitFreeFailover:
    """
    Free model round-robin failover engine.
    
    Features:
    - Primary model selection with fallback chain
    - Automatic failover on 429 (rate limit) errors
    - Free model rotation when primary models exhausted
    - Configurable cooldown periods
    - Circuit breaker pattern
    """
    
    def __init__(self, models: List[ModelConfig], 
                 primary_preference: str = None,
                 free_model_fallback: bool = True,
                 max_failures_before_fallback: int = 3):
        self.models = {m.name: m for m in models}
        self.primary_preference = primary_preference
        self.free_model_fallback = free_model_fallback
        self.max_failures_before_fallback = max_failures_before_fallback
        
        # Round-robin iterators
        self._primary_cycle = itertools.cycle([
            m.name for m in models if not m.is_free and m.status == ModelStatus.AVAILABLE
        ])
        self._free_cycle = itertools.cycle([
            m.name for m in models if m.is_free and m.status == ModelStatus.AVAILABLE
        ])
        
        self._current_primary = None
        self._current_free = None
        self._fallback_active = False
        
    def select_model(self, prefer_free: bool = False) -> Optional[str]:
        """Select best available model"""
        # Try primary preference first
        if self.primary_preference and not prefer_free:
            model = self.models.get(self.primary_preference)
            if model and model.status == ModelStatus.AVAILABLE:
                return self.primary_preference
        
        # Get next model from cycle
        selected = None
        
        if not prefer_free and not self._fallback_active:
            # Try primary models first
            for _ in range(len([m for m in self.models.values() if not m.is_free])):
                try:
                    name = next(self._primary_cycle)
                    model = self.models.get(name)
                    if model and model.status == ModelStatus.AVAILABLE:
                        selected = name
                        break
                except StopIteration:
                    break
        else:
            # Fallback to free models
            for _ in range(len([m for m in self.models.values() if m.is_free])):
                try:
                    name = next(self._free_cycle)
                    model = self.models.get(name)
                    if model and model.status == ModelStatus.AVAILABLE:
                        selected = name
                        self._fallback_active = True
                        break
                except StopIteration:
                    break
        
        return selected
    
    def record_success(self, model_name: str):
        """Record successful API call"""
        model = self.models.get(model_name)
        if model:
            model.last_used = time.time()
            model.failure_count = 0
            model.status = ModelStatus.AVAILABLE
            self._fallback_active = False
    
    def record_failure(self, model_name: str, error_type: str = "unknown"):
        """Record failed API call"""
        model = self.models.get(model_name)
        if model:
            model.failure_count += 1
            model.last_used = time.time()
            
            if error_type == "rate_limit":
                model.status = ModelStatus.RATE_LIMITED
                model.cooldown_until = time.time() + 60  # 1 minute cooldown
            elif error_type == "error":
                model.status = ModelStatus.ERROR
            elif error_type == "maintenance":
                model.status = ModelStatus.MAINTENANCE
                
            # Activate fallback if too many failures
            if model.failure_count >= self.max_failures_before_fallback:
                self._fallback_active = True
    
    def make_request(self, request_func: Callable, *args, **kwargs) -> Any:
        """
        Make API request with automatic failover.
        
        Args:
            request_func: Function that makes the API request
            *args, **kwargs: Arguments to pass to request_func
            
        Returns:
            API response or raises exception on exhaustion
        """
        last_error = None
        attempts = 0
        max_attempts = len(self.models) * 2
        
        while attempts < max_attempts:
            model_name = self.select_model(prefer_free=self._fallback_active)
            
            if model_name is None:
                raise Exception("No available models")
            
            model = self.models[model_name]
            
            # Check cooldown
            if model.cooldown_until > time.time():
                time.sleep(1)
                continue
            
            try:
                # Make request
                response = request_func(model_name, *args, **kwargs)
                
                self.record_success(model_name)
                return response
                
            except Exception as e:
                error_msg = str(e).lower()
                
                if "429" in error_msg or "rate limit" in error_msg:
                    self.record_failure(model_name, "rate_limit")
                elif "maintenance" in error_msg:
                    self.record_failure(model_name, "maintenance")
                else:
                    self.record_failure(model_name, "error")
                
                last_error = e
                attempts += 1
                
                # Brief delay before next attempt
                time.sleep(random.uniform(0.5, 2.0))
        
        raise last_error or Exception("All model requests failed")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current failover engine status"""
        return {
            "total_models": len(self.models),
            "available_models": sum(1 for m in self.models.values() if m.status == ModelStatus.AVAILABLE),
            "rate_limited_models": sum(1 for m in self.models.values() if m.status == ModelStatus.RATE_LIMITED),
            "error_models": sum(1 for m in self.models.values() if m.status == ModelStatus.ERROR),
            "maintenance_models": sum(1 for m in self.models.values() if m.status == ModelStatus.MAINTENANCE),
            "fallback_active": self._fallback_active,
            "model_details": [
                {
                    "name": m.name,
                    "provider": m.provider,
                    "is_free": m.is_free,
                    "status": m.status.value,
                    "failure_count": m.failure_count,
                    "last_used": m.last_used
                }
                for m in self.models.values()
            ]
        }


def create_demo_failover() -> RateLimitFreeFailover:
    """Create a demo failover engine with sample models"""
    models = [
        ModelConfig(name="gpt-4o", provider="openai", model_id="gpt-4o", is_free=False),
        ModelConfig(name="claude-3-opus", provider="anthropic", model_id="claude-3-opus", is_free=False),
        ModelConfig(name="gemini-pro", provider="google", model_id="gemini-pro", is_free=False),
        ModelConfig(name="llama-2-free", provider="fireworks", model_id="llama-2", is_free=True),
        ModelConfig(name="falcon-free", provider="together", model_id="falcon", is_free=True),
    ]
    
    return RateLimitFreeFailover(models, primary_preference="gpt-4o")


if __name__ == "__main__":
    failover = create_demo_failover()
    
    print("🔄 Rate-Limit-Free-Failover Engine initialized")
    print(f"   Total models: {failover.get_status()['total_models']}")
    print(f"   Available: {failover.get_status()['available_models']}")
    print(f"   Free models: {sum(1 for m in failover.models.values() if m.is_free)}")
    
    # Test model selection
    print("\n📋 Model Selection Tests:")
    for i in range(5):
        model = failover.select_model(prefer_free=False)
        print(f"   Request {i+1}: {model} (free={failover.models[model].is_free})")
        if model:
            failover.record_success(model)
    
    # Simulate rate limit and test failover
    print("\n⚠️  Simulating rate limit on primary model...")
    if failover.primary_preference:
        failover.record_failure(failover.primary_preference, "rate_limit")
    
    # Test failover
    model = failover.select_model(prefer_free=True)
    print(f"   Fallback model: {model}")
    
    print("\n✅ Rate-Limit-Free-Failover Engine demo completed")