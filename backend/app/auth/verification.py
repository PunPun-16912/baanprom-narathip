"""Fail-closed boundary for SC-04 Thai-ID/DBD-ID verification."""
from typing import Protocol


class VerificationProviderUnavailable(Exception):
    """Raised when no real Thai-ID/DBD-ID provider has been configured."""


class SalengVerificationProvider(Protocol):
    def is_verified(self, saleng_id: int) -> bool: ...


class UnconfiguredVerificationProvider:
    def is_verified(self, saleng_id: int) -> bool:
        raise VerificationProviderUnavailable(
            "ยังไม่ได้เชื่อมต่อผู้ให้บริการยืนยันตัวตน Thai-ID/DBD-ID"
        )


def get_verification_provider() -> SalengVerificationProvider:
    return UnconfiguredVerificationProvider()
