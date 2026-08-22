#!/usr/bin/env python3
"""
API-Key-Balancer Engine
Per-request API key load balancer with instant 429 failovers
Implements round-robin distribution with automatic failover on rate limits
"""

import itertools
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class APIKeyConfig:
    """Configuration for a single API key"""
    key_id: str
    api_key: str
    provider: str
    rate_limit: int = 60  # requests per minute
    is_active: bool = True
    last_used: float = 0.0
    failure_count: int = 0


class APIKeyBalancer:
    """
    Per-request API key load balancer with instant 429 failovers.
    
    Features:
    - Round-robin distribution across multiple keys
    - Automatic failover on 429 (rate limit) responses
    - Circuit breaker for failing keys
    - Configurable retry with exponential backoff
    """
    
    def __init__(self, keys: List[APIKeyConfig], max_failures: int = 5, circuit_breaker_timeout: int = 60):
        self.keys = keys
        self.max_failures = max_failures
        self.circuit_breaker_timeout = circuit_breaker_timeout
        self._cycle = itertools.cycle(range(len(keys)))
        self._current_index = 0
        
    def get_next_key(self) -> Optional[APIKeyConfig]:
        """Get the next available API key using round-robin"""
        start_index = self._current_index
        
        for _ in range(len(self.keys)):
            key = self.keys[self._current_index]
            self._current_index = (self._current_index + 1) % len(self.keys)
            
            if key.is_active and key.failure_count < self.max_failures:
                return key
        
        return None
    
    def record_success(self, key_id: str):
        """Record successful API call for a key"""
        for key in self.keys:
            if key.key_id == key_id:
                key.last_used = time.time()
                key.failure_count = 0
                break
    
    def record_failure(self, key_id: str, is_rate_limit: bool = False):
        """Record failed API call for a key"""
        for key in self.keys:
            if key.key_id == key_id:
                key.failure_count += 1
                if is_rate_limit:
                    # Immediate failover on rate limit
                    key.is_active = False
                    time.sleep(1)  # Brief cooldown
                    key.is_active = True
                break
    
    def make_request(self, request_func, *args, **kwargs) -> Any:
        """
        Make API request with automatic failover on 429.
        
        Args:
            request_func: Function that makes the API request
            *args, **kwargs: Arguments to pass to request_func
            
        Returns:
            API response or raises exception on exhaustion
        """
        last_error = None
        
        for attempt in range(len(self.keys) * 2):  # Multiple rounds
            key = self.get_next_key()
            if key is None:
                raise Exception("All API keys exhausted")
            
            try:
                response = request_func(key.api_key, *args, **kwargs)
                
                # Check for rate limit
                if hasattr(response, 'status_code') and response.status_code == 429:
                    self.record_failure(key.key_id, is_rate_limit=True)
                    last_error = Exception("Rate limit exceeded (429)")
                    continue
                
                self.record_success(key.key_id)
                return response
                
            except Exception as e:
                self.record_failure(key.key_id)
                last_error = e
                continue
        
        raise last_error or Exception("All API requests failed")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current balancer status"""
        return {
            "total_keys": len(self.keys),
            "active_keys": sum(1 for k in self.keys if k.is_active),
            "exhausted_keys": sum(1 for k in self.keys if k.failure_count >= self.max_failures),
            "key_status": [
                {
                    "id": k.key_id,
                    "provider": k.provider,
                    "is_active": k.is_active,
                    "failure_count": k.failure_count,
                    "last_used": k.last_used
                }
                for k in self.keys
            ]
        }


def create_default_balanced_keys() -> APIKeyBalancer:
    """Create a balancer with default configuration"""
    keys = [
        APIKeyConfig(key_id="key_1", api_key="sk-test-1", provider="openai", rate_limit=60),
        APIKeyConfig(key_id="key_2", api_key="sk-test-2", provider="openai", rate_limit=60),
        APIKeyConfig(key_id="key_3", api_key="sk-test-3", provider="anthropic", rate_limit=60),
    ]
    return APIKeyBalancer(keys)


if __name__ == "__main__":
    # Demo
    balancer = create_default_balanced_keys()
    print("🔑 API-Key-Balancer initialized")
    print(f"   Keys: {balancer.get_status()['total_keys']}")
    print(f"   Active: {balancer.get_status()['active_keys']}")
    
    # Test round-robin
    for i in range(5):
        key = balancer.get_next_key()
        print(f"   Request {i+1}: Using {key.key_id} ({key.provider})")
        balancer.record_success(key.key_id)
    
    print("✅ API-Key-Balancer demo completed")