class ComparisonUnavailable(RuntimeError):
    """A safe, actionable comparison error; never contains upstream response text."""

    def __init__(self, code: str, message: str, status_code: int = 502):
        super().__init__(message)
        self.code = code
        self.status_code = status_code
