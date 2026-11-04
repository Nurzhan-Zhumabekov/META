"""Local image comparison with no API key: perceptual hash + color histogram.

This is classical computer vision, not a trained model. The real ML comparison
(Muse Spark / SAM 3.1) goes in MetaComparer once API access is available.
"""

import numpy as np
from PIL import Image
from .models import ComparisonResult

HASH_SIZE = 16


def _dhash(img: Image.Image) -> np.ndarray:
    g = img.convert("L").resize((HASH_SIZE + 1, HASH_SIZE))
    a = np.asarray(g, dtype=np.int16)
    return (a[:, 1:] > a[:, :-1]).flatten()


def _hist(img: Image.Image) -> np.ndarray:
    a = np.asarray(img.convert("RGB").resize((64, 64)))
    h, _ = np.histogramdd(a.reshape(-1, 3), bins=(8, 8, 8), range=((0, 256),) * 3)
    return h.flatten() / h.sum()


class LocalComparer:
    def analyze(self, original: Image.Image, suspect: Image.Image, **context) -> ComparisonResult:
        score, reasons = self.compare(original, suspect)
        return ComparisonResult(score, reasons, {
            "provider": "local", "model": None,
            "summary": "Local image and handle comparison; no AI model was called.",
            "limitations": ["Image similarity does not establish ownership or prove impersonation."],
            "recommendation": "needs_review",
        })

    def compare(self, original: Image.Image, suspect: Image.Image) -> tuple[float, list[str]]:
        hash_sim = 1.0 - float(np.mean(_dhash(original) != _dhash(suspect)))
        hist_sim = float(np.minimum(_hist(original), _hist(suspect)).sum())
        score = 0.6 * hash_sim + 0.4 * hist_sim
        reasons = [
            f"Structure similarity (perceptual hash): {hash_sim:.0%}",
            f"Color similarity (histogram): {hist_sim:.0%}",
        ]
        if hash_sim > 0.9:
            reasons.append("Profile images are near-identical")
        return score, reasons
