import asyncio
import time
import logging
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """
    Circuit breaker states:
    - CLOSED: Requests are allowed through. All is normal.
    - OPEN: All requests are blocked immediately; the circuit is "tripped" due to too many
      failures.
    - HALF_OPEN: A limited number of test requests are allowed to check if the underlying
      issue is resolved.
    """

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreaker:
    provider_name: str
    failure_threshold: int
    recovery_timeout: int
    disable: bool = False

    state: CircuitState = field(default=CircuitState.CLOSED, init=False)
    failure_count: int = field(default=0, init=False)
    last_failure_time: float = field(default=0.0, init=False)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False)

    async def can_execute(self) -> bool:
        if self.disable:
            return True
        async with self._lock:
            if self.state == CircuitState.OPEN:
                if (time.time() - self.last_failure_time) > self.recovery_timeout:
                    self.state = CircuitState.HALF_OPEN
                    logger.info(f"Circuit breaker HALF_OPEN for {self.provider_name}")
                    return True
                return False
            return True

    async def record_success(self):
        if self.disable:
            return
        async with self._lock:
            if self.state != CircuitState.CLOSED:
                logger.info(f"Circuit breaker CLOSED for {self.provider_name}")
            self.failure_count = 0
            self.state = CircuitState.CLOSED

    async def record_failure(self):
        if self.disable:
            return
        async with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                if self.state != CircuitState.OPEN:
                    logger.info(f"Circuit breaker OPEN for {self.provider_name}")
                self.state = CircuitState.OPEN

    def get_status(self):
        return {"state": self.state.value, "failure_count": self.failure_count}
