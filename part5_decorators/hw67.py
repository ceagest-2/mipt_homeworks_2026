import json
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from functools import wraps
from typing import Any, ParamSpec, Protocol, TypeVar
from urllib.request import urlopen

INVALID_CRITICAL_COUNT = "Breaker count must be positive integer!"
INVALID_RECOVERY_TIME = "Breaker recovery time must be positive integer!"
VALIDATIONS_FAILED = "Invalid decorator args."
TOO_MUCH = "Too much requests, just wait."


P = ParamSpec("P")
R_co = TypeVar("R_co", covariant=True)


class CallableWithMeta(Protocol[P, R_co]):
    __name__: str
    __module__: str

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R_co: ...


class BreakerError(Exception):
    def __init__(self, func_name: str, block_time: datetime):
        self.func_name = func_name
        self.block_time = block_time
        super().__init__(TOO_MUCH)


@dataclass
class _BreakerState:
    failed_count: int = 0
    blocked_until: datetime | None = None
    block_time: datetime | None = None


class CircuitBreaker:
    def __init__(
        self,
        critical_count: int = 5,
        time_to_recover: int = 30,
        triggers_on: type[Exception] = Exception,
    ):
        exceptions: list[ValueError] = []
        if not isinstance(critical_count, int) or (critical_count <= 0):
            exceptions.append(ValueError(INVALID_CRITICAL_COUNT))
        if not isinstance(time_to_recover, int) or (time_to_recover <= 0):
            exceptions.append(ValueError(INVALID_RECOVERY_TIME))
        if len(exceptions) > 0:
            raise ExceptionGroup(VALIDATIONS_FAILED, exceptions)
        self.critical_count = critical_count
        self.time_to_recover = time_to_recover
        self.triggers_on = triggers_on

    def __call__(self, func: CallableWithMeta[P, R_co]) -> CallableWithMeta[P, R_co]:
        state = _BreakerState()

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R_co:
            return self._execute(func, state, *args, **kwargs)

        return wrapper

    def _execute(
        self,
        func: CallableWithMeta[P, R_co],
        state: _BreakerState,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> R_co:
        now = datetime.now(UTC)
        func_name = f"{func.__module__}.{func.__name__}"
        blocking_error = self._get_blocking_error(state, now, func_name)
        if blocking_error is not None:
            raise blocking_error

        try:
            result = func(*args, **kwargs)
        except Exception as error:
            self._handle_failure(error, state, func_name)
            raise

        state.failed_count = 0
        return result

    def _get_blocking_error(
        self,
        state: _BreakerState,
        now: datetime,
        func_name: str,
    ) -> BreakerError | None:
        if state.blocked_until is None:
            return None
        if now >= state.blocked_until:
            state.blocked_until = None
            state.block_time = None
            state.failed_count = 0
            return None
        return BreakerError(func_name=func_name, block_time=state.block_time or now)

    def _handle_failure(
        self,
        error: Exception,
        state: _BreakerState,
        func_name: str,
    ) -> None:
        if not isinstance(error, self.triggers_on):
            return

        state.failed_count += 1
        if state.failed_count < self.critical_count:
            return

        block_time = datetime.now(UTC)
        state.block_time = block_time
        state.blocked_until = block_time + timedelta(seconds=self.time_to_recover)
        state.failed_count = 0
        raise BreakerError(func_name=func_name, block_time=block_time) from error


circuit_breaker = CircuitBreaker(5, 30, Exception)


# @circuit_breaker
def get_comments(post_id: int) -> Any:
    """
    Получает комментарии к посту

    Args:
        post_id (int): Идентификатор поста

    Returns:
        list[dict[int | str]]: Список комментариев
    """
    response = urlopen(f"https://jsonplaceholder.typicode.com/comments?postId={post_id}")
    return json.loads(response.read())


if __name__ == "__main__":
    comments = get_comments(1)
