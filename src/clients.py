from typing import Protocol

from PIL import Image

from . import config
from .errors import ComparisonUnavailable
from .meta_compare import MetaComparer
from .models import ComparisonResult


class Comparer(Protocol):
    def analyze(self, original: Image.Image, suspect: Image.Image, *, owner_handle: str = "", suspect_handle: str = "") -> ComparisonResult: ...

    def compare(self, original: Image.Image, suspect: Image.Image) -> tuple[float, list[str]]:
        """Return (similarity score 0..1, human-readable reasons)."""
        ...


class MockComparer:
    """Fake result so the UI works before API access arrives."""

    def compare(self, original: Image.Image, suspect: Image.Image) -> tuple[float, list[str]]:
        return 0.87, ["[mock] Profile photo matches the original", "[mock] Same bio wording"]

    def analyze(self, original: Image.Image, suspect: Image.Image, **context) -> ComparisonResult:
        score, reasons = self.compare(original, suspect)
        return ComparisonResult(score, reasons, {"provider": "mock", "model": None, "summary": "Simulated result; no model was called."})


def get_comparer() -> Comparer:
    if config.COMPARER == "mock":
        return MockComparer()
    if config.COMPARER == "meta":
        return MetaComparer()
    if config.COMPARER != "local":
        raise ComparisonUnavailable("invalid_comparer", "COMPARER must be local, mock or meta.", 503)
    from .local_compare import LocalComparer

    return LocalComparer()
