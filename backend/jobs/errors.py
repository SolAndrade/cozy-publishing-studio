class RetryableJobError(RuntimeError):
    """Explicit opt-in for failures safe to retry without human review."""
