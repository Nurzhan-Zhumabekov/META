from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone


@dataclass
class ComparisonResult:
    image_score: float
    reasons: list[str]
    analysis: dict = field(default_factory=dict)
    provider_images: tuple[bytes, bytes] | None = field(default=None, repr=False, compare=False)


@dataclass
class Claim:
    id: str
    suspect_handle: str
    owner_handle: str
    score: float
    reasons: list[str] = field(default_factory=list)
    status: str = "pending"  # pending -> under_review -> confirmed | rejected
    analysis: dict = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    evidence: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)
