"""Agent-facing Visual validation data tools."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    from cereal.evidence.types import EvidenceWindow

__all__ = ["make_validate_visual_claim_tool"]


def make_validate_visual_claim_tool(
    *,
    evidence_windows: Mapping[str, EvidenceWindow],
) -> Callable[..., dict[str, object]]:
    """Create a fake Visual validation tool for agent planning smoke."""

    def validate_visual_claim(claim: str, evidence_window_ref: str) -> dict[str, object]:
        """Validate one Visual claim against a retrieved Evidence window."""
        resolved_ref, window = _resolve_evidence_window(evidence_window_ref, evidence_windows)
        return {
            "claim": claim,
            "status": "supported",
            "class_name": window.target.class_name,
            "evidence_window_ref": resolved_ref,
        }

    return validate_visual_claim


def _resolve_evidence_window(
    evidence_window_ref: str,
    evidence_windows: Mapping[str, EvidenceWindow],
) -> tuple[str, EvidenceWindow]:
    if evidence_window_ref in evidence_windows:
        return evidence_window_ref, evidence_windows[evidence_window_ref]
    if len(evidence_windows) == 1:
        stored_ref, window = next(iter(evidence_windows.items()))
        # URI fallback is only for the single-candidate planning smoke.
        if evidence_window_ref == window.evidence_uri:
            return stored_ref, window
    return evidence_window_ref, evidence_windows[evidence_window_ref]
