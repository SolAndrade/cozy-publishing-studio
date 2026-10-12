class DomainError(ValueError):
    """Base error for invalid publishing workflow transitions."""


class LockedAssetError(DomainError):
    """Raised when normal production attempts to mutate locked art."""


class GenerationLimitError(DomainError):
    """Raised when regeneration exceeds the allowed retry policy."""


class InvalidTransitionError(DomainError):
    """Raised when a workflow transition skips required gates."""
