"""
Circuit Breaker Pattern Implementation

Prevents cascading failures by stopping requests to failing services.
When open, returns clear errors instead of stale data.

States:
- CLOSED: Normal operation, requests pass through
- OPEN: Service is failing, requests blocked with clear error
- HALF_OPEN: Testing if service has recovered
"""
from __future__ import annotations
import threading
import time
from typing import Any
from dataclasses import dataclass, field
from enum import Enum


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitOpenError(Exception):
    """Raised when circuit breaker is open - API unavailable"""
    def __init__(self, circuit_name: str, recovery_in: float):
        self.circuit_name = circuit_name
        self.recovery_in = recovery_in
        super().__init__(f"Service '{circuit_name}' temporarily unavailable. Retry in {recovery_in:.0f}s")


@dataclass
class CircuitBreaker:
    """Circuit breaker for external service calls"""

    name: str
    failure_threshold: int = 5
    recovery_timeout: int = 60  # seconds
    half_open_max_calls: int = 3

    # Internal state
    _failure_count: int = field(default=0, init=False)
    _success_count: int = field(default=0, init=False)
    _last_failure_time: float | None = field(default=None, init=False)
    _state: CircuitState = field(default=CircuitState.CLOSED, init=False)
    _half_open_calls: int = field(default=0, init=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False)

    def record_failure(self) -> None:
        """Record a failed call to the service"""
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()
            self._success_count = 0

            if self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.OPEN
                self._half_open_calls = 0
            elif self._failure_count >= self.failure_threshold:
                self._state = CircuitState.OPEN

    def record_success(self) -> None:
        """Record a successful call to the service"""
        with self._lock:
            self._success_count += 1

            if self._state == CircuitState.HALF_OPEN:
                self._half_open_calls += 1
                if self._half_open_calls >= self.half_open_max_calls:
                    self._state = CircuitState.CLOSED
                    self._failure_count = 0
                    self._half_open_calls = 0
            elif self._state == CircuitState.CLOSED:
                self._failure_count = 0

    def check_state(self) -> None:
        """Check if request can proceed, raise CircuitOpenError if not"""
        with self._lock:
            if self._state == CircuitState.CLOSED:
                return

            if self._state == CircuitState.OPEN:
                if self._last_failure_time is None:
                    return

                elapsed = time.time() - self._last_failure_time
                if elapsed >= self.recovery_timeout:
                    self._state = CircuitState.HALF_OPEN
                    self._half_open_calls = 0
                    return

                remaining = self.recovery_timeout - elapsed
                raise CircuitOpenError(self.name, remaining)

            # HALF_OPEN - allow limited test calls
            if self._half_open_calls >= self.half_open_max_calls:
                raise CircuitOpenError(self.name, self.recovery_timeout)

    def get_status(self) -> dict[str, Any]:
        """Get current circuit breaker status"""
        with self._lock:
            status = {
                'name': self.name,
                'state': self._state.value,
                'failure_count': self._failure_count,
                'failure_threshold': self.failure_threshold,
                'healthy': self._state == CircuitState.CLOSED,
            }

            if self._last_failure_time and self._state == CircuitState.OPEN:
                elapsed = time.time() - self._last_failure_time
                remaining = max(0, self.recovery_timeout - elapsed)
                status['recovery_in_seconds'] = round(remaining)

            return status

    def reset(self) -> None:
        """Manually reset the circuit breaker"""
        with self._lock:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._success_count = 0
            self._last_failure_time = None
            self._half_open_calls = 0


class CircuitBreakerRegistry:
    """Registry for managing multiple circuit breakers"""

    def __init__(self) -> None:
        self._breakers: dict[str, CircuitBreaker] = {}
        self._lock = threading.Lock()

    def get(self, name: str, **kwargs) -> CircuitBreaker:
        """Get or create a circuit breaker by name"""
        with self._lock:
            if name not in self._breakers:
                self._breakers[name] = CircuitBreaker(name=name, **kwargs)
            return self._breakers[name]

    def get_all_status(self) -> dict[str, dict[str, Any]]:
        """Get status of all circuit breakers"""
        with self._lock:
            return {name: cb.get_status() for name, cb in self._breakers.items()}


# Global registry
circuit_registry = CircuitBreakerRegistry()
