#!/usr/bin/env python3
from dataclasses import dataclass

@dataclass
class RetryPolicy:
    max_attempts: int = 2
    retry_on_statuses: tuple = ('failed',)
    retry_on_validation_failure: bool = True


def should_retry(status: str, validation_ok: bool, attempt: int, policy: RetryPolicy) -> bool:
    if attempt >= policy.max_attempts:
        return False
    if status in policy.retry_on_statuses:
        return True
    if not validation_ok and policy.retry_on_validation_failure:
        return True
    return False
